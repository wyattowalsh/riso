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
from typing import TYPE_CHECKING, Any

from ..config import get_config
from ..errors import (
    CopierOperationError,
    PathNotFoundError,
    ValidationFailedError,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP


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
            - api_tracks: "none", "python", "node", or "python+node"
            - mcp_module: "enabled" or "disabled"
            - docs_site: "fumadocs", "sphinx-shibuya", "docusaurus", or "none"
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
        from riso.template import (
            get_defaults,
            get_template_path,
            merge_answers_with_defaults,
            run_generator,
            load_copier_config,
            validate_answers,
        )

        try:
            template_path = config.template_path
            if not template_path.exists():
                template_path = get_template_path()

            copier_config = load_copier_config(template_path)
            defaults = get_defaults(template_path)

            # Build complete answers
            provided = answers or {}
            project_name = provided.get(
                "project_name", defaults.get("project_name", "riso-project")
            )
            final_answers = merge_answers_with_defaults(
                project_name=project_name,
                config=copier_config,
                provided_answers=provided,
            )

            validation = validate_answers(final_answers, template_path)
            if not validation.valid:
                raise ValidationFailedError(validation.errors)

            result = run_generator(
                destination=Path(destination).expanduser().resolve(),
                data=final_answers,
                template_path=template_path,
                force=force,
                vcs_ref=vcs_ref,
                timeout=config.timeouts.copier_copy,
            )

            return result.to_dict()

        except Exception as e:
            raise CopierOperationError("copy", str(e)) from e

    @mcp.tool()
    def copier_update(
        destination: str,
        skip_answered: bool = True,
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

        Returns
        -------
        dict
            Operation result with success status and message
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

            result = run_update(
                destination=dest_path,
                template_path=template_path,
                skip_answered=skip_answered,
                timeout=config.timeouts.tool,
            )

            return result.to_dict()

        except (PathNotFoundError, CopierOperationError):
            raise
        except Exception as e:
            raise CopierOperationError("update", str(e)) from e

    @mcp.tool()
    def copier_recopy(
        destination: str,
        answers: dict[str, Any] | None = None,
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

        Returns
        -------
        dict
            Operation result with success status and message
        """
        from riso.template import get_template_path, run_recopy

        try:
            dest_path = Path(destination).expanduser().resolve()
            if not dest_path.exists():
                raise PathNotFoundError(str(dest_path))

            template_path = config.template_path
            if not template_path.exists():
                template_path = get_template_path()

            result = run_recopy(
                destination=dest_path,
                data=answers,
                template_path=template_path,
                timeout=config.timeouts.tool,
            )

            return result.to_dict()

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
