"""Copier API tools for MCP.

Provides direct access to Copier template operations:
- copier_copy: Create new project from template
- copier_update: Update existing project
- copier_recopy: Regenerate project from scratch
- list_template_variants: List sample configurations
- validate_template_answers: Validate answers against schema
- get_prompts: Get all template prompts with schemas
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from ..answer_validation import reject_removed_answer_keys
from ..config import get_config
from ..errors import (
    CopierOperationError,
    OperationCancelled,
    OperationTimeoutError,
    PathNotFoundError,
    PermissionDeniedError,
    ValidationFailedError,
)
from ..progress import (
    CancellationToken,
    OperationStage,
    ProgressTracker,
    ProgressUpdate,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP


def validate_destination(dest: str, safe_parent: Path | None = None) -> Path:
    """Validate destination doesn't escape safe directory.

    Parameters
    ----------
    dest
        Destination path to validate
    safe_parent
        Optional parent directory that destination must be within

    Returns
    -------
    Path
        Validated and resolved destination path

    Raises
    ------
    PermissionDeniedError
        If destination is outside safe_parent or in dangerous system paths
    """
    path = Path(dest).expanduser().resolve()

    # If safe_parent is provided, ensure destination is within it
    if safe_parent:
        safe_parent = safe_parent.resolve()
        try:
            path.relative_to(safe_parent)
        except ValueError as err:
            raise PermissionDeniedError(
                "destination", f"Outside allowed parent: {safe_parent}"
            ) from err

    # Block common dangerous system paths
    # Note: On macOS, /etc -> /private/etc, /tmp -> /private/tmp
    # On macOS, /home -> /System/Volumes/Data/home
    # We need to be specific about /var subdirectories to not block temp files
    dangerous_paths = [
        "/etc",
        "/usr",
        "/bin",
        "/sbin",
        "/root",
        "/private/etc",
        "/var/log",
        "/var/db",
        "/var/mail",
        "/var/spool",
        "/private/var/log",
        "/private/var/db",
        "/private/var/mail",
        "/private/var/spool",  # macOS equivalents
        "/System/Volumes/Data/home",  # macOS resolution of /home
        "/home",  # Linux/Unix home (but only if it doesn't resolve to macOS path)
    ]
    path_str = str(path)

    # Check if path starts with any dangerous path
    for dangerous in dangerous_paths:
        # Ensure we're checking full path components, not partial matches
        if path_str == dangerous or path_str.startswith(dangerous + "/"):
            raise PermissionDeniedError(
                "destination", "Cannot write to system directories"
            )

    return path


def _run_with_progress(
    operation_func: Callable[..., Any],
    tracker: ProgressTracker,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Run an operation with progress tracking through major stages.

    Parameters
    ----------
    operation_func
        The function to execute
    tracker
        Progress tracker for reporting milestones
    *args
        Positional arguments for operation_func
    **kwargs
        Keyword arguments for operation_func

    Returns
    -------
    Any
        Result from operation_func

    Raises
    ------
    OperationCancelled
        If operation is cancelled via tracker's cancellation token
    """
    # INITIALIZING stage (already started by tracker init)
    tracker.update(1.0, "Initialization complete")

    # VALIDATING stage
    tracker.start_stage(OperationStage.VALIDATING)
    tracker.update(0.5, "Validating configuration...")
    # Validation happens before this function in copier_copy
    tracker.update(1.0, "Validation complete")

    # RENDERING stage
    tracker.start_stage(OperationStage.RENDERING)
    tracker.update(0.2, "Loading template...")

    # Execute the actual Copier operation (rendering + writing)
    # Since Copier doesn't provide progress callbacks, we estimate
    tracker.update(0.5, "Rendering templates...")

    try:
        result = operation_func(*args, **kwargs)
    except Exception as e:
        raise e

    # WRITING stage
    tracker.start_stage(OperationStage.WRITING)
    tracker.update(0.5, "Writing files to disk...")
    tracker.update(1.0, "Files written successfully")

    # FINALIZING stage
    tracker.start_stage(OperationStage.FINALIZING)
    tracker.update(0.5, "Running post-generation hooks...")
    tracker.update(1.0, "Finalization complete")

    # Mark complete
    tracker.complete()

    return result


def _copier_copy_with_progress(
    destination: str,
    answers: dict[str, Any] | None = None,
    force: bool = False,
    vcs_ref: str | None = None,
    progress_callback: Callable[[ProgressUpdate], None] | None = None,
    cancellation_token: CancellationToken | None = None,
) -> dict[str, Any]:
    """Internal copier_copy implementation with progress tracking support.

    Parameters
    ----------
    destination
        Directory where the project will be created
    answers
        Template answers as a dictionary
    force
        Overwrite existing files if destination exists
    vcs_ref
        Git ref (branch/tag) to use for the template
    progress_callback
        Optional callback for receiving progress updates
    cancellation_token
        Optional token for cancellation support

    Returns
    -------
    dict
        Operation result with keys:
        - success: bool
        - destination: str
        - message: str
        - metadata: dict

    Raises
    ------
    OperationCancelled
        If operation is cancelled via token
    ValidationFailedError
        If answers fail validation
    CopierOperationError
        If Copier operation fails
    """
    from riso.template import (
        get_defaults,
        get_template_path,
        merge_answers_with_defaults,
        run_generator,
        load_copier_config,
        validate_answers,
    )

    config = get_config()

    # Initialize progress tracker if callback provided
    tracker: ProgressTracker | None = None
    if progress_callback or cancellation_token:
        tracker = ProgressTracker(cancellation_token=cancellation_token)
        if progress_callback:
            tracker.add_callback(progress_callback)
        tracker.start_stage(OperationStage.INITIALIZING)

    try:
        # INITIALIZING: Validate destination path for security
        if tracker:
            tracker.update(0.3, "Validating destination path...")
        validated_dest = validate_destination(destination)

        if tracker:
            tracker.update(0.6, "Loading template configuration...")
        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        copier_config = load_copier_config(template_path)
        defaults = get_defaults(template_path)

        # Build complete answers
        provided = answers or {}
        reject_removed_answer_keys(provided)
        project_name = provided.get(
            "project_name", defaults.get("project_name", "riso-project")
        )
        final_answers = merge_answers_with_defaults(
            project_name=project_name,
            config=copier_config,
            provided_answers=provided,
        )

        if tracker:
            tracker.update(1.0, "Initialization complete")

        # VALIDATING: Validate answers
        if tracker:
            tracker.start_stage(OperationStage.VALIDATING)
            tracker.update(0.5, "Validating template answers...")

        validation = validate_answers(final_answers, template_path)
        if not validation.valid:
            raise ValidationFailedError(validation.errors)

        if tracker:
            tracker.update(1.0, "Validation complete")

        # RENDERING + WRITING: Run Copier operation
        if tracker:
            tracker.start_stage(OperationStage.RENDERING)
            tracker.update(0.3, "Preparing to render templates...")

        # Wrap run_generator call to insert progress updates
        def _run_generator_wrapper() -> Any:
            if tracker:
                tracker.update(0.6, "Rendering templates from source...")
                tracker.start_stage(OperationStage.WRITING)
                tracker.update(0.3, "Writing files to destination...")

            result = run_generator(
                destination=validated_dest,
                data=final_answers,
                template_path=template_path,
                force=force,
                vcs_ref=vcs_ref,
                timeout=config.timeouts.copier_copy,
            )

            if tracker:
                tracker.update(0.8, "Files written successfully")

            return result

        result = _run_generator_wrapper()

        # FINALIZING
        if tracker:
            tracker.start_stage(OperationStage.FINALIZING)
            tracker.update(0.5, "Running post-generation tasks...")
            tracker.update(1.0, "Finalization complete")
            tracker.complete()

        return result.to_dict()

    except OperationCancelled:
        raise  # Re-raise cancellation
    except OperationTimeoutError:
        raise  # Re-raise timeout errors with proper error code
    except Exception as e:
        raise CopierOperationError("copy", str(e)) from e


def register_copier_tools(mcp: FastMCP) -> None:
    """Register all Copier API tools with the MCP server.

    Parameters
    ----------
    mcp
        FastMCP server instance
    """
    config = get_config()

    @mcp.tool()
    def copier_copy(
        destination: str,
        answers: dict[str, Any] | None = None,
        force: bool = False,
        vcs_ref: str | None = None,
    ) -> dict[str, Any]:
        """Create a new project from the Riso template.

        Parameters
        ----------
        destination
            Directory where the project will be created. Can be absolute
            or relative to the current working directory.
        answers
            Template answers as a dictionary. If not provided, defaults
            will be used. Common keys include:
            - project_name: Human-friendly name
            - project_layout: "single-package" or "monorepo"
            - quality_profile: "standard" or "strict"
            - cli_module: "enabled" or "disabled"
            - api_module: "enabled" or "disabled"
            - api_languages: list containing "python", "node", "go", and/or "rust"
            - mcp_module: "enabled" or "disabled"
            - mcp_languages: list containing enabled MCP implementation languages
            - docs_module: "enabled" or "disabled"
            - docs_framework: "fumadocs", "sphinx-shibuya", or "docusaurus"
        force
            Overwrite existing files if destination exists
        vcs_ref
            Git ref (branch/tag) to use for the template

        Returns
        -------
        dict
            Operation result with keys:
            - success: bool
            - destination: str
            - message: str
            - metadata: dict
        """
        # Delegate to internal implementation without progress tracking
        # Progress tracking will be exposed through future FastMCP context integration
        return _copier_copy_with_progress(
            destination=destination,
            answers=answers,
            force=force,
            vcs_ref=vcs_ref,
            progress_callback=None,
            cancellation_token=None,
        )

    @mcp.tool()
    def copier_update(
        destination: str,
        skip_answered: bool = True,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Update an existing project with the latest template changes.

        Applies template updates while preserving project-specific
        modifications. Uses the answers from .copier-answers.yml.

        Parameters
        ----------
        destination
            Path to the existing project directory
        skip_answered
            Skip prompts that already have answers (default: True)
        dry_run
            Preview changes without applying them (default: False)

        Returns
        -------
        dict
            Operation result with success status and message.
            If dry_run=True, returns a DiffResult showing what would change.
        """
        from riso.template import get_template_path, run_update

        try:
            dest_path = Path(destination).expanduser().resolve()
            if not dest_path.exists():
                raise PathNotFoundError(str(dest_path))

            answers_file = dest_path / ".copier-answers.yml"
            if not answers_file.exists():
                raise CopierOperationError(
                    "update",
                    f"No .copier-answers.yml found at {dest_path}. "
                    "This project may not have been created with Copier.",
                )

            template_path = config.template_path
            if not template_path.exists():
                template_path = get_template_path()

            # If dry_run, compute and return diff
            if dry_run:
                from .diff import compute_diff
                import asyncio
                import yaml

                # Load existing answers
                answers = yaml.safe_load(answers_file.read_text(encoding="utf-8"))
                reject_removed_answer_keys(answers or {})

                diff_result = asyncio.run(
                    compute_diff(
                        answers=answers,
                        destination=dest_path,
                        template_path=template_path,
                        operation="update",
                    )
                )
                return diff_result.to_dict()

            result = run_update(
                destination=dest_path,
                template_path=template_path,
                skip_answered=skip_answered,
                timeout=config.timeouts.tool,
            )

            return result.to_dict()

        except OperationTimeoutError:
            raise  # Re-raise timeout errors with proper error code
        except (PathNotFoundError, CopierOperationError):
            raise
        except Exception as e:
            raise CopierOperationError("update", str(e)) from e

    @mcp.tool()
    def copier_recopy(
        destination: str,
        answers: dict[str, Any] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Regenerate a project from scratch with current or new answers.

        Recreates the entire project structure. Use this to apply
        significant template changes or update all answers.

        Parameters
        ----------
        destination
            Path to the existing project directory
        answers
            Optional new answers to merge with existing ones
        dry_run
            Preview changes without applying them (default: False)

        Returns
        -------
        dict
            Operation result with success status and message.
            If dry_run=True, returns a DiffResult showing what would change.
        """
        from riso.template import get_template_path, run_recopy

        try:
            dest_path = Path(destination).expanduser().resolve()
            if not dest_path.exists():
                raise PathNotFoundError(str(dest_path))

            template_path = config.template_path
            if not template_path.exists():
                template_path = get_template_path()

            # If dry_run, compute and return diff
            if dry_run:
                from .diff import compute_diff
                import asyncio
                import yaml

                # Load existing answers and merge with provided ones
                answers_file = dest_path / ".copier-answers.yml"
                if answers_file.exists():
                    existing_answers = yaml.safe_load(
                        answers_file.read_text(encoding="utf-8")
                    )
                else:
                    existing_answers = {}

                reject_removed_answer_keys(existing_answers or {})
                reject_removed_answer_keys(answers or {})
                final_answers = {**existing_answers, **(answers or {})}

                diff_result = asyncio.run(
                    compute_diff(
                        answers=final_answers,
                        destination=dest_path,
                        template_path=template_path,
                        operation="recopy",
                    )
                )
                return diff_result.to_dict()

            result = run_recopy(
                destination=dest_path,
                data=answers,
                template_path=template_path,
                timeout=config.timeouts.tool,
            )

            return result.to_dict()

        except OperationTimeoutError:
            raise  # Re-raise timeout errors with proper error code
        except PathNotFoundError:
            raise
        except Exception as e:
            raise CopierOperationError("recopy", str(e)) from e

    @mcp.tool()
    def list_template_variants() -> list[dict[str, Any]]:
        """List all available sample project configurations.

        Returns sample project variants with their answers files,
        useful for understanding different template configurations.

        Returns
        -------
        list
            List of variant information with:
            - name: Variant name
            - path: Path to variant directory
            - has_answers: Whether answers file exists
            - answers: The answers if available
            - has_render: Whether rendered output exists
        """
        from riso.template import get_samples_path, list_sample_variants

        samples_path = config.samples_path
        if not samples_path.exists():
            samples_path = get_samples_path()

        return list_sample_variants(samples_path)

    @mcp.tool()
    def validate_template_answers(
        answers: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate answers against the template schema.

        Checks that provided answers are valid for the template,
        including type validation and choice constraints.

        Parameters
        ----------
        answers
            Answers dictionary to validate

        Returns
        -------
        dict
            Validation result with:
            - valid: bool
            - errors: list of error messages
            - warnings: list of warning messages

        Raises
        ------
        ValidationFailedError
            If answers contain critical errors
        """
        from riso.template import get_template_path, validate_answers

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        reject_removed_answer_keys(answers)
        result = validate_answers(answers, template_path)

        if not result.valid:
            raise ValidationFailedError(result.errors)

        return result.to_dict()

    @mcp.tool()
    def get_prompts() -> dict[str, Any]:
        """Get all template prompts with their schemas.

        Returns the complete prompt configuration from copier.yml,
        including types, choices, defaults, and conditions.

        Returns
        -------
        dict
            Complete prompt information with:
            - prompts: dict of prompt definitions
            - defaults: dict of default values
            - metadata: template metadata
        """
        from riso.template import (
            get_defaults,
            get_prompts as _get_prompts,
            get_template_path,
            load_copier_config,
        )

        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        full_config = load_copier_config(template_path)

        return {
            "prompts": _get_prompts(template_path),
            "defaults": get_defaults(template_path),
            "metadata": full_config.get("metadata", {}),
        }

    @mcp.tool()
    def copier_diff(
        destination: str,
        answers: dict[str, Any] | None = None,
        operation: str = "copy",
    ) -> dict[str, Any]:
        """Preview changes that would be made by a Copier operation.

        Compares the current state with what would be generated,
        without making any actual changes.

        Parameters
        ----------
        destination
            Path to compare against. For 'copy', this can be
            nonexistent. For 'update' and 'recopy', must exist.
        answers
            Template answers to use for generating the preview.
            For 'update' and 'recopy', merges with existing answers.
        operation
            Type of operation to preview: "copy", "update", or "recopy"

        Returns
        -------
        dict
            DiffResult showing all files that would be added,
            modified, or deleted, with:
            - summary: Human-readable summary
            - added_count: Number of new files
            - modified_count: Number of changed files
            - deleted_count: Number of removed files
            - files: List of file diffs with status and changes
        """
        from riso.template import get_template_path
        from .diff import compute_diff
        import asyncio

        try:
            dest_path = Path(destination).expanduser().resolve()

            # For update/recopy, destination must exist
            if operation in ("update", "recopy") and not dest_path.exists():
                raise PathNotFoundError(str(dest_path))

            template_path = config.template_path
            if not template_path.exists():
                template_path = get_template_path()

            # Prepare answers based on operation type
            final_answers: dict[str, Any]

            if operation == "copy":
                # For copy, use provided answers with defaults
                from riso.template import (
                    get_defaults,
                    load_copier_config,
                    merge_answers_with_defaults,
                )

                copier_config = load_copier_config(template_path)
                defaults = get_defaults(template_path)

                provided = answers or {}
                reject_removed_answer_keys(provided)
                project_name = provided.get(
                    "project_name", defaults.get("project_name", "riso-project")
                )
                final_answers = merge_answers_with_defaults(
                    project_name=project_name,
                    config=copier_config,
                    provided_answers=provided,
                )

            elif operation in ("update", "recopy"):
                # For update/recopy, load and merge with existing answers
                import yaml

                answers_file = dest_path / ".copier-answers.yml"
                if answers_file.exists():
                    existing_answers = yaml.safe_load(
                        answers_file.read_text(encoding="utf-8")
                    )
                else:
                    existing_answers = {}

                reject_removed_answer_keys(existing_answers or {})
                reject_removed_answer_keys(answers or {})
                final_answers = {**existing_answers, **(answers or {})}

            else:
                raise ValueError(
                    f"Invalid operation: {operation}. "
                    "Must be 'copy', 'update', or 'recopy'."
                )

            # Compute and return diff
            diff_result = asyncio.run(
                compute_diff(
                    answers=final_answers,
                    destination=dest_path,
                    template_path=template_path,
                    operation=operation,
                )
            )

            return diff_result.to_dict()

        except PathNotFoundError:
            raise
        except Exception as e:
            raise CopierOperationError("diff", str(e)) from e
