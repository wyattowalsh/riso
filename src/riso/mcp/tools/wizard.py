"""Interactive wizard tools for MCP.

Provides multi-step project generation workflow:
- wizard_start: Start a new wizard session
- wizard_step: Submit answers for current step
- wizard_back: Go back to previous step
- wizard_status: Get current session state
- wizard_generate: Generate project from completed session
- wizard_cancel: Cancel and cleanup session
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..config import get_config
from ..errors import (
    CopierOperationError,
    SessionNotFoundError,
    ValidationFailedError,
)
from ..session import SessionManager

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_wizard_tools(mcp: FastMCP, session_manager: SessionManager) -> None:
    """Register all wizard tools with the MCP server.

    Parameters
    ----------
    mcp
        FastMCP server instance
    session_manager
        Session manager for wizard state
    """
    config = get_config()

    @mcp.tool()
    def wizard_start(
        project_name: str = "",
        destination: str = "",
        template_variant: str = "default",
    ) -> dict[str, Any]:
        """Start a new interactive wizard session.

        Creates a session that guides through project configuration
        step by step. Use wizard_step to provide answers.

        Parameters
        ----------
        project_name
            Initial project name (can be changed later)
        destination
            Target directory for the project
        template_variant
            Sample variant to use as starting point

        Returns
        -------
        dict
            Session information with:
            - session_id: Unique session identifier
            - current_step: Current step index
            - current_step_info: Details about the current step
            - total_steps: Total number of steps
            - prompts_for_step: Prompts to answer for current step
        """
        from riso.template import get_prompts, get_defaults, get_template_path

        session = session_manager.create_session(
            project_name=project_name,
            destination=destination,
            template_variant=template_variant,
        )

        # Pre-populate with defaults
        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        defaults = get_defaults(template_path)
        session.set_answers(defaults)

        if project_name:
            session.set_answer("project_name", project_name)
            session.set_answer("project_slug", project_name.replace(" ", "-").lower())
            session.set_answer(
                "package_name", project_name.replace(" ", "-").lower().replace("-", "_")
            )

        # Get prompts for current step
        all_prompts = get_prompts(template_path)
        current_step = session.steps[session.current_step]
        step_prompts = {
            name: all_prompts.get(name, {})
            for name in current_step.prompts
            if name in all_prompts
        }

        return {
            "session_id": session.session_id,
            "current_step": session.current_step,
            "current_step_info": {
                "name": current_step.name,
                "title": current_step.title,
                "required": current_step.required,
            },
            "total_steps": len(session.steps),
            "prompts_for_step": step_prompts,
            "current_answers": session.answers,
        }

    @mcp.tool()
    def wizard_step(
        session_id: str,
        answers: dict[str, Any],
        advance: bool = True,
    ) -> dict[str, Any]:
        """Submit answers for the current wizard step.

        Validates and stores answers, optionally advancing to
        the next step.

        Parameters
        ----------
        session_id
            Active wizard session ID
        answers
            Answers for the current step's prompts
        advance
            Automatically advance to next step (default: True)

        Returns
        -------
        dict
            Updated session state with next step info
        """
        from riso.template import get_prompts, get_template_path, validate_answers

        session = session_manager.get_session(session_id)

        # Store answers
        session.set_answers(answers)

        # Validate current answers
        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        validation = validate_answers(session.answers, template_path)
        session.validation_errors = validation.errors

        # Mark current step as completed
        current_step = session.steps[session.current_step]
        current_step.completed = True
        current_step.data = {name: session.answers.get(name) for name in current_step.prompts}

        # Advance if requested and not at end
        if advance and session.current_step < len(session.steps) - 1:
            session.advance_step()

        # Check if all steps completed
        if session.current_step >= len(session.steps) - 1:
            if all(s.completed or not s.required for s in session.steps):
                session.is_complete = True

        # Get prompts for new current step
        all_prompts = get_prompts(template_path)
        new_step = session.steps[session.current_step]
        step_prompts = {
            name: all_prompts.get(name, {})
            for name in new_step.prompts
            if name in all_prompts
        }

        return {
            "session_id": session.session_id,
            "current_step": session.current_step,
            "current_step_info": {
                "name": new_step.name,
                "title": new_step.title,
                "required": new_step.required,
                "completed": new_step.completed,
            },
            "total_steps": len(session.steps),
            "prompts_for_step": step_prompts,
            "current_answers": session.answers,
            "is_complete": session.is_complete,
            "validation_errors": session.validation_errors,
        }

    @mcp.tool()
    def wizard_back(session_id: str) -> dict[str, Any]:
        """Go back to the previous wizard step.

        Parameters
        ----------
        session_id
            Active wizard session ID

        Returns
        -------
        dict
            Updated session state
        """
        from riso.template import get_prompts, get_template_path

        session = session_manager.get_session(session_id)
        session.go_back()

        # Get prompts for current step
        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        all_prompts = get_prompts(template_path)
        current_step = session.steps[session.current_step]
        step_prompts = {
            name: all_prompts.get(name, {})
            for name in current_step.prompts
            if name in all_prompts
        }

        return {
            "session_id": session.session_id,
            "current_step": session.current_step,
            "current_step_info": {
                "name": current_step.name,
                "title": current_step.title,
                "required": current_step.required,
                "completed": current_step.completed,
            },
            "total_steps": len(session.steps),
            "prompts_for_step": step_prompts,
            "current_answers": session.answers,
        }

    @mcp.tool()
    def wizard_status(session_id: str) -> dict[str, Any]:
        """Get the current state of a wizard session.

        Parameters
        ----------
        session_id
            Wizard session ID

        Returns
        -------
        dict
            Complete session state including:
            - All steps and their completion status
            - Current answers
            - Validation status
            - Whether generation is ready
        """
        session = session_manager.get_session(session_id)

        steps_info = [
            {
                "name": step.name,
                "title": step.title,
                "required": step.required,
                "completed": step.completed,
                "prompts": step.prompts,
            }
            for step in session.steps
        ]

        return {
            "session_id": session.session_id,
            "current_step": session.current_step,
            "total_steps": len(session.steps),
            "steps": steps_info,
            "answers": session.answers,
            "project_name": session.project_name or session.answers.get("project_name", ""),
            "destination": session.destination or session.answers.get("destination", ""),
            "is_complete": session.is_complete,
            "validation_errors": session.validation_errors,
            "ready_to_generate": session.is_complete and len(session.validation_errors) == 0,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
        }

    @mcp.tool()
    def wizard_generate(
        session_id: str,
        destination: str | None = None,
    ) -> dict[str, Any]:
        """Generate the project from a completed wizard session.

        Parameters
        ----------
        session_id
            Completed wizard session ID
        destination
            Override destination directory (optional)

        Returns
        -------
        dict
            Generation result with:
            - success: bool
            - destination: str
            - message: str
            - answers_used: dict
        """
        from riso.template import (
            get_template_path,
            load_copier_config,
            merge_answers_with_defaults,
            run_generator,
            validate_answers,
        )

        session = session_manager.get_session(session_id)

        # Validate before generation
        template_path = config.template_path
        if not template_path.exists():
            template_path = get_template_path()

        validation = validate_answers(session.answers, template_path)
        if not validation.valid:
            raise ValidationFailedError(validation.errors)

        # Determine destination
        final_destination = destination or session.destination
        if not final_destination:
            project_name = session.answers.get("project_name", "riso-project")
            final_destination = str(Path.cwd() / project_name)

        # Build final answers
        copier_config = load_copier_config(template_path)
        project_name = session.answers.get("project_name", "riso-project")
        final_answers = merge_answers_with_defaults(
            project_name=project_name,
            config=copier_config,
            provided_answers=session.answers,
        )

        # Generate
        result = run_generator(
            destination=Path(final_destination),
            data=final_answers,
            template_path=template_path,
            force=True,
        )

        if result.success:
            # Cleanup session
            session_manager.delete_session(session_id)

        return {
            "success": result.success,
            "destination": str(result.destination),
            "message": result.message,
            "answers_used": final_answers,
            "session_cleaned_up": result.success,
        }

    @mcp.tool()
    def wizard_cancel(session_id: str) -> dict[str, Any]:
        """Cancel and cleanup a wizard session.

        Parameters
        ----------
        session_id
            Wizard session ID to cancel

        Returns
        -------
        dict
            Cancellation confirmation
        """
        try:
            session = session_manager.get_session(session_id)
            answers_count = len(session.answers)
            step_count = session.current_step + 1
            session_manager.delete_session(session_id)

            return {
                "success": True,
                "session_id": session_id,
                "message": f"Session cancelled. {answers_count} answers discarded after {step_count} steps.",
            }
        except SessionNotFoundError:
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session already expired or not found.",
            }

    @mcp.tool()
    def wizard_list_sessions() -> list[dict[str, Any]]:
        """List all active wizard sessions.

        Returns
        -------
        list
            Active sessions with basic info
        """
        return session_manager.list_sessions()
