"""Comprehensive end-to-end tests for wizard functionality.

Tests wizard.py which implements multi-step project generation workflow.
"""

from __future__ import annotations

import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("fastmcp")

from riso.mcp.errors import (
    SessionExpiredError,
    SessionNotFoundError,
    ValidationFailedError,
)
from riso.mcp.session import SessionManager, WizardSession, WizardStep
from riso.mcp.tools.wizard import register_wizard_tools


@pytest.fixture
def session_manager():
    """Create a session manager for testing."""
    return SessionManager(ttl_minutes=60, max_sessions=100)


@pytest.fixture
def mcp_server(session_manager):
    """Create MCP server with wizard tools registered."""
    from fastmcp import FastMCP

    mcp = FastMCP("test-wizard")
    register_wizard_tools(mcp, session_manager)
    return mcp


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_template_functions():
    """Mock template module functions."""
    with (
        patch("riso.template.get_template_path") as mock_get_path,
        patch("riso.template.get_prompts") as mock_get_prompts,
        patch("riso.template.get_defaults") as mock_get_defaults,
        patch("riso.template.load_sample_answers") as mock_load_samples,
        patch("riso.template.validate_answers") as mock_validate,
        patch("riso.template.run_generator") as mock_run_gen,
    ):
        # Setup mock returns
        mock_get_path.return_value = Path("/fake/template")
        mock_get_prompts.return_value = {
            "project_name": {"type": "str", "help": "Project name"},
            "project_layout": {
                "type": "str",
                "choices": ["single-package", "monorepo"],
            },
            "project_language": {"type": "str", "choices": ["python", "node", "multi"]},
            "quality_profile": {"type": "str", "choices": ["standard", "strict"]},
            "python_versions": {"type": "str"},
            "cli_module": {"type": "str", "choices": ["enabled", "disabled"]},
            "api_module": {"type": "str", "choices": ["enabled", "disabled"]},
            "api_languages": {"type": "yaml"},
            "mcp_module": {"type": "str", "choices": ["enabled", "disabled"]},
            "mcp_languages": {"type": "yaml"},
            "websocket_module": {"type": "str", "choices": ["enabled", "disabled"]},
            "docs_module": {"type": "str", "choices": ["enabled", "disabled"]},
            "docs_framework": {"type": "str"},
            "shared_logic": {"type": "str"},
            "ci_platform": {"type": "str"},
            "changelog_module": {"type": "str"},
            "destination": {"type": "str", "help": "Output directory"},
        }
        mock_get_defaults.return_value = {
            "project_name": "my-project",
            "project_layout": "single-package",
            "project_language": "python",
            "quality_profile": "standard",
        }
        mock_load_samples.return_value = {}

        # Mock validation to succeed by default
        mock_validation = MagicMock()
        mock_validation.valid = True
        mock_validation.errors = []
        mock_validation.warnings = []
        mock_validate.return_value = mock_validation

        # Mock generator
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.destination = Path("/fake/output")
        mock_result.message = "Project generated successfully"
        mock_run_gen.return_value = mock_result

        yield {
            "get_path": mock_get_path,
            "get_prompts": mock_get_prompts,
            "get_defaults": mock_get_defaults,
            "load_samples": mock_load_samples,
            "validate": mock_validate,
            "run_generator": mock_run_gen,
        }


class TestWizardStart:
    """Tests for wizard_start tool."""

    def test_wizard_start_creates_session(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_start returns valid session_id and step info."""
        # Get the wizard_start tool
        wizard_start = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_start":
                wizard_start = tool.fn
                break

        assert wizard_start is not None, "wizard_start tool not found"

        # Call wizard_start
        result = wizard_start()

        # Verify session was created
        assert "session_id" in result
        assert result["session_id"] is not None
        assert len(result["session_id"]) > 0

        # Verify step info
        assert result["current_step"] == 0
        assert "current_step_info" in result
        assert result["current_step_info"]["name"] == "project_basics"
        assert "total_steps" in result
        assert result["total_steps"] > 0
        assert "prompts_for_step" in result

        # Verify session exists in manager
        session = session_manager.get_session(result["session_id"])
        assert session is not None

    def test_wizard_start_with_project_name(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_start accepts initial project_name."""
        wizard_start = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_start":
                wizard_start = tool.fn
                break

        result = wizard_start(project_name="test-project")

        assert result["session_id"] is not None

        # Verify project_name was set
        session = session_manager.get_session(result["session_id"])
        assert session.project_name == "test-project"
        assert session.answers.get("project_name") == "test-project"
        assert session.answers.get("project_slug") == "test-project"
        assert session.answers.get("package_name") == "test_project"

    def test_wizard_start_with_destination(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_start accepts destination path."""
        wizard_start = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_start":
                wizard_start = tool.fn
                break

        result = wizard_start(destination="/tmp/test-output")

        session = session_manager.get_session(result["session_id"])
        assert session.destination == "/tmp/test-output"
        assert session.answers.get("destination") == "/tmp/test-output"

    def test_wizard_start_with_template_variant(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_start accepts template_variant preset."""
        # Mock load_sample_answers to return specific answers
        mock_template_functions["load_samples"].return_value = {
            "project_layout": "monorepo",
            "cli_module": "enabled",
        }

        wizard_start = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_start":
                wizard_start = tool.fn
                break

        result = wizard_start(template_variant="full-stack")

        session = session_manager.get_session(result["session_id"])
        assert session.template_variant == "full-stack"
        # Verify variant answers were applied
        assert session.answers.get("project_layout") == "monorepo"
        assert session.answers.get("cli_module") == "enabled"


class TestWizardStep:
    """Tests for wizard_step tool."""

    def test_wizard_step_validates_and_stores_answers(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_step accepts and stores valid answers."""
        # Create a session first
        session = session_manager.create_session()
        session.answers = {}  # Clear defaults for test clarity

        # Get wizard_step tool
        wizard_step = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_step":
                wizard_step = tool.fn
                break

        # Submit answers for first step
        answers = {
            "project_name": "my-app",
            "project_layout": "single-package",
            "project_language": "python",
        }
        wizard_step(session_id=session.session_id, answers=answers)

        # Verify answers were stored
        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.answers["project_name"] == "my-app"
        assert updated_session.answers["project_layout"] == "single-package"
        assert updated_session.answers["project_language"] == "python"

    def test_wizard_step_advances_to_next(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_step advances when advance=True."""
        session = session_manager.create_session()
        initial_step = session.current_step

        wizard_step = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_step":
                wizard_step = tool.fn
                break

        result = wizard_step(
            session_id=session.session_id,
            answers={"project_name": "test"},
            advance=True,
        )

        assert result["current_step"] == initial_step + 1
        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.current_step == initial_step + 1

    def test_wizard_step_stays_on_current(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_step stays when advance=False."""
        session = session_manager.create_session()
        initial_step = session.current_step

        wizard_step = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_step":
                wizard_step = tool.fn
                break

        result = wizard_step(
            session_id=session.session_id,
            answers={"project_name": "test"},
            advance=False,
        )

        assert result["current_step"] == initial_step
        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.current_step == initial_step

    def test_wizard_step_invalid_session(self, mcp_server, mock_template_functions):
        """wizard_step with invalid session raises SessionNotFoundError."""
        wizard_step = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_step":
                wizard_step = tool.fn
                break

        with pytest.raises(SessionNotFoundError):
            wizard_step(session_id="invalid-session-id", answers={})

    def test_wizard_step_rejects_removed_answer_keys(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_step rejects removed answer keys instead of converting them."""
        session = session_manager.create_session()

        wizard_step = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_step":
                wizard_step = tool.fn
                break

        with pytest.raises(ValidationFailedError) as exc_info:
            wizard_step(
                session_id=session.session_id,
                answers={"api_tracks": "python+node"},
            )
        assert "api_tracks" in exc_info.value.data["errors"][0]

    def test_wizard_step_updates_project_name_derivatives(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_step updates project_slug and package_name when project_name changes."""
        session = session_manager.create_session()

        wizard_step = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_step":
                wizard_step = tool.fn
                break

        wizard_step(
            session_id=session.session_id,
            answers={"project_name": "My Cool App"},
            advance=False,
        )

        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.answers["project_slug"] == "my-cool-app"
        assert updated_session.answers["package_name"] == "my_cool_app"

    def test_wizard_step_marks_step_completed(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_step marks current step as completed when validation passes."""
        session = session_manager.create_session()

        wizard_step = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_step":
                wizard_step = tool.fn
                break

        wizard_step(
            session_id=session.session_id,
            answers={"project_name": "test", "project_layout": "single-package"},
            advance=False,
        )

        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.steps[0].completed is True

    def test_wizard_step_validation_errors_prevent_completion(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_step does not mark step completed when validation fails."""
        # Mock validation to fail
        mock_validation = MagicMock()
        mock_validation.valid = False
        mock_validation.errors = ["project_name: required"]
        mock_template_functions["validate"].return_value = mock_validation

        session = session_manager.create_session()

        wizard_step = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_step":
                wizard_step = tool.fn
                break

        result = wizard_step(
            session_id=session.session_id,
            answers={},
            advance=False,
        )

        assert len(result["validation_errors"]) > 0
        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.steps[0].completed is False


class TestWizardBack:
    """Tests for wizard_back tool."""

    def test_wizard_back_moves_to_previous_step(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_back returns to previous step."""
        session = session_manager.create_session()
        # Manually advance to step 2
        session.advance_step()
        session.advance_step()
        assert session.current_step == 2

        wizard_back = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_back":
                wizard_back = tool.fn
                break

        result = wizard_back(session_id=session.session_id)

        assert result["current_step"] == 1
        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.current_step == 1

    def test_wizard_back_on_first_step(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_back on first step handles gracefully."""
        session = session_manager.create_session()
        assert session.current_step == 0

        wizard_back = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_back":
                wizard_back = tool.fn
                break

        result = wizard_back(session_id=session.session_id)

        # Should stay at step 0
        assert result["current_step"] == 0
        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.current_step == 0

    def test_wizard_back_resets_completion_flag(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_back resets is_complete flag."""
        session = session_manager.create_session()
        session.is_complete = True
        session.advance_step()

        wizard_back = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_back":
                wizard_back = tool.fn
                break

        wizard_back(session_id=session.session_id)

        updated_session = session_manager.get_session(session.session_id)
        assert updated_session.is_complete is False


class TestWizardStatus:
    """Tests for wizard_status tool."""

    def test_wizard_status_returns_complete_state(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_status returns complete session state."""
        session = session_manager.create_session(project_name="test-project")
        session.set_answers({"key1": "value1", "key2": "value2"})
        session.advance_step()

        wizard_status = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_status":
                wizard_status = tool.fn
                break

        result = wizard_status(session_id=session.session_id)

        # Verify all expected fields
        assert result["session_id"] == session.session_id
        assert result["current_step"] == 1
        assert result["total_steps"] == len(session.steps)
        assert "steps" in result
        assert len(result["steps"]) == len(session.steps)
        assert result["answers"] == session.answers
        assert result["project_name"] == "test-project"
        assert "created_at" in result
        assert "last_activity" in result
        assert "is_complete" in result
        assert "validation_errors" in result
        assert "ready_to_generate" in result

    def test_wizard_status_includes_all_steps_info(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_status includes detailed info for all steps."""
        session = session_manager.create_session()

        wizard_status = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_status":
                wizard_status = tool.fn
                break

        result = wizard_status(session_id=session.session_id)

        steps = result["steps"]
        assert len(steps) > 0
        for step in steps:
            assert "name" in step
            assert "title" in step
            assert "required" in step
            assert "completed" in step
            assert "prompts" in step

    def test_wizard_status_invalid_session(self, mcp_server, mock_template_functions):
        """wizard_status with invalid session raises SessionNotFoundError."""
        wizard_status = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_status":
                wizard_status = tool.fn
                break

        with pytest.raises(SessionNotFoundError):
            wizard_status(session_id="non-existent-session")

    def test_wizard_status_ready_to_generate_flag(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_status ready_to_generate is true only when complete and valid."""
        session = session_manager.create_session()

        wizard_status = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_status":
                wizard_status = tool.fn
                break

        # Not complete yet
        result = wizard_status(session_id=session.session_id)
        assert result["ready_to_generate"] is False

        # Mark as complete with no errors
        session.is_complete = True
        session.validation_errors = []
        result = wizard_status(session_id=session.session_id)
        assert result["ready_to_generate"] is True

        # Complete but with errors
        session.validation_errors = ["error1"]
        result = wizard_status(session_id=session.session_id)
        assert result["ready_to_generate"] is False


class TestWizardGenerate:
    """Tests for wizard_generate tool."""

    def test_wizard_generate_creates_project(
        self, mcp_server, session_manager, temp_output_dir, mock_template_functions
    ):
        """wizard_generate creates project files."""
        session = session_manager.create_session()
        session.set_answers(
            {
                "project_name": "test-project",
                "project_layout": "single-package",
            }
        )
        session.is_complete = True

        wizard_generate = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_generate":
                wizard_generate = tool.fn
                break

        # Mock additional template functions
        with (
            patch("riso.template.load_copier_config") as mock_load_config,
            patch("riso.template.merge_answers_with_defaults") as mock_merge,
        ):
            mock_load_config.return_value = {}
            mock_merge.return_value = session.answers

            result = wizard_generate(
                session_id=session.session_id,
                destination=str(temp_output_dir),
                force=True,
            )

        assert result["success"] is True
        assert "destination" in result
        assert "message" in result
        assert "answers_used" in result

    def test_wizard_generate_requires_completion(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_generate fails if wizard not complete."""
        # Mock validation to fail
        mock_validation = MagicMock()
        mock_validation.valid = False
        mock_validation.errors = ["project_name: required"]
        mock_template_functions["validate"].return_value = mock_validation

        session = session_manager.create_session()
        session.is_complete = False

        wizard_generate = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_generate":
                wizard_generate = tool.fn
                break

        with pytest.raises(ValidationFailedError):
            wizard_generate(session_id=session.session_id)

    def test_wizard_generate_cleans_up_session_on_success(
        self, mcp_server, session_manager, temp_output_dir, mock_template_functions
    ):
        """wizard_generate removes session after successful generation."""
        session = session_manager.create_session()
        session.set_answers({"project_name": "test"})
        session.is_complete = True
        session_id = session.session_id

        wizard_generate = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_generate":
                wizard_generate = tool.fn
                break

        with (
            patch("riso.template.load_copier_config") as mock_load_config,
            patch("riso.template.merge_answers_with_defaults") as mock_merge,
        ):
            mock_load_config.return_value = {}
            mock_merge.return_value = session.answers

            result = wizard_generate(
                session_id=session_id,
                destination=str(temp_output_dir),
                force=True,
            )

        assert result["session_cleaned_up"] is True

        # Verify session was deleted
        with pytest.raises(SessionNotFoundError):
            session_manager.get_session(session_id)

    def test_wizard_generate_uses_default_destination(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_generate uses default destination if not provided."""
        session = session_manager.create_session()
        session.set_answers({"project_name": "my-project"})
        session.is_complete = True

        wizard_generate = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_generate":
                wizard_generate = tool.fn
                break

        with (
            patch("riso.template.load_copier_config") as mock_load_config,
            patch("riso.template.merge_answers_with_defaults") as mock_merge,
        ):
            mock_load_config.return_value = {}
            mock_merge.return_value = session.answers

            wizard_generate(session_id=session.session_id, force=True)

        # Verify run_generator was called
        mock_template_functions["run_generator"].assert_called_once()
        call_kwargs = mock_template_functions["run_generator"].call_args[1]
        # Should use current directory / project name
        assert "my-project" in str(call_kwargs["destination"])


class TestWizardCancel:
    """Tests for wizard_cancel tool."""

    def test_wizard_cancel_deletes_session(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_cancel removes session and returns confirmation."""
        session = session_manager.create_session(project_name="test")
        session.set_answers({"key1": "value1", "key2": "value2"})
        session_id = session.session_id

        wizard_cancel = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_cancel":
                wizard_cancel = tool.fn
                break

        result = wizard_cancel(session_id=session_id)

        assert result["success"] is True
        assert result["session_id"] == session_id
        assert "message" in result

        # Verify session was deleted
        with pytest.raises(SessionNotFoundError):
            session_manager.get_session(session_id)

    def test_wizard_cancel_non_existent_session(
        self, mcp_server, mock_template_functions
    ):
        """wizard_cancel handles non-existent session gracefully."""
        wizard_cancel = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_cancel":
                wizard_cancel = tool.fn
                break

        result = wizard_cancel(session_id="non-existent")

        # Should still return success
        assert result["success"] is True
        assert "not found" in result["message"].lower()


class TestWizardListSessions:
    """Tests for wizard_list_sessions tool."""

    def test_wizard_list_sessions_returns_active_sessions(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_list_sessions returns list of active sessions."""
        # Create multiple sessions
        session1 = session_manager.create_session(project_name="project1")
        session2 = session_manager.create_session(project_name="project2")

        wizard_list_sessions = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_list_sessions":
                wizard_list_sessions = tool.fn
                break

        result = wizard_list_sessions()

        assert isinstance(result, list)
        assert len(result) == 2

        session_ids = [s["session_id"] for s in result]
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids

        # Verify each session has expected fields
        for session_info in result:
            assert "session_id" in session_info
            assert "project_name" in session_info
            assert "current_step" in session_info
            assert "is_complete" in session_info
            assert "created_at" in session_info
            assert "last_activity" in session_info

    def test_wizard_list_sessions_empty(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """wizard_list_sessions returns empty list when no sessions."""
        wizard_list_sessions = None
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name == "wizard_list_sessions":
                wizard_list_sessions = tool.fn
                break

        result = wizard_list_sessions()

        assert isinstance(result, list)
        assert len(result) == 0


class TestWizardWorkflow:
    """End-to-end workflow tests."""

    def test_full_wizard_workflow(
        self, mcp_server, session_manager, temp_output_dir, mock_template_functions
    ):
        """Complete wizard from start to generation."""
        # Get all wizard tools
        tools = {}
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name.startswith("wizard_"):
                tools[tool.name] = tool.fn

        # 1. Start wizard
        start_result = tools["wizard_start"](project_name="workflow-test")
        session_id = start_result["session_id"]
        assert session_id is not None

        # 2. Step through multiple steps
        step_answers = [
            {"project_name": "workflow-test", "project_layout": "single-package"},
            {"quality_profile": "standard"},
            {"cli_module": "enabled"},
            {"docs_module": "disabled"},
            {"ci_platform": "github"},
            {"destination": str(temp_output_dir)},
        ]

        for answers in step_answers:
            step_result = tools["wizard_step"](
                session_id=session_id,
                answers=answers,
                advance=True,
            )
            assert "current_step" in step_result

        # 3. Check status
        status_result = tools["wizard_status"](session_id=session_id)
        assert status_result["session_id"] == session_id

        # 4. Generate project
        with (
            patch("riso.template.load_copier_config") as mock_load_config,
            patch("riso.template.merge_answers_with_defaults") as mock_merge,
        ):
            mock_load_config.return_value = {}
            session = session_manager.get_session(session_id)
            mock_merge.return_value = session.answers
            session.is_complete = True

            gen_result = tools["wizard_generate"](
                session_id=session_id,
                destination=str(temp_output_dir),
                force=True,
            )

        assert gen_result["success"] is True

    def test_wizard_workflow_with_back_navigation(
        self, mcp_server, session_manager, mock_template_functions
    ):
        """Test wizard with back navigation."""
        tools = {}
        for tool in mcp_server._tool_manager._tools.values():
            if tool.name.startswith("wizard_"):
                tools[tool.name] = tool.fn

        # Start and advance
        start_result = tools["wizard_start"]()
        session_id = start_result["session_id"]

        tools["wizard_step"](
            session_id=session_id, answers={"project_name": "test"}, advance=True
        )
        tools["wizard_step"](
            session_id=session_id, answers={"quality_profile": "standard"}, advance=True
        )

        # Go back
        back_result = tools["wizard_back"](session_id=session_id)
        assert back_result["current_step"] == 1

        # Re-answer and advance
        step_result = tools["wizard_step"](
            session_id=session_id,
            answers={"quality_profile": "strict"},
            advance=True,
        )
        assert step_result["current_step"] == 2


class TestWizardConcurrency:
    """Thread safety tests."""

    def test_concurrent_sessions(self, session_manager):
        """Multiple sessions can run concurrently."""
        results = []

        def create_and_modify_session(name: str):
            session = session_manager.create_session(project_name=name)
            session.set_answers({"key": f"value-{name}"})
            session.advance_step()
            results.append((session.session_id, session.answers["key"]))

        # Create threads
        threads = [
            threading.Thread(target=create_and_modify_session, args=(f"project-{i}",))
            for i in range(5)
        ]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify all sessions were created correctly
        assert len(results) == 5
        session_ids = {r[0] for r in results}
        assert len(session_ids) == 5  # All unique

        # Verify data integrity
        for session_id, value in results:
            session = session_manager.get_session(session_id)
            assert session.answers["key"] == value


class TestWizardSessionExpiry:
    """Session lifecycle tests."""

    def test_session_expiry(self):
        """Expired sessions are cleaned up."""
        manager = SessionManager(ttl_minutes=1)  # 1 minute TTL

        session = manager.create_session(project_name="test")
        session_id = session.session_id

        # Session should exist
        retrieved = manager.get_session(session_id)
        assert retrieved is not None

        # Manually expire the session
        session.last_activity = datetime.now() - timedelta(minutes=2)

        # Should raise SessionExpiredError
        with pytest.raises(SessionExpiredError):
            manager.get_session(session_id)

        # Session should be removed from manager
        assert session_id not in manager._sessions

    def test_cleanup_expired_sessions(self):
        """cleanup_expired removes all expired sessions."""
        manager = SessionManager(ttl_minutes=1)

        # Create sessions
        s1 = manager.create_session(project_name="p1")
        s2 = manager.create_session(project_name="p2")
        s3 = manager.create_session(project_name="p3")

        # Expire two sessions
        s1.last_activity = datetime.now() - timedelta(minutes=2)
        s2.last_activity = datetime.now() - timedelta(minutes=2)

        # Keep s3 fresh
        s3.touch()

        # Cleanup
        count = manager.cleanup_expired()

        assert count == 2
        assert manager.active_session_count == 1

        # Only s3 should remain
        assert manager.get_session_or_none(s3.session_id) is not None
        assert manager.get_session_or_none(s1.session_id) is None
        assert manager.get_session_or_none(s2.session_id) is None

    def test_session_touch_updates_activity(self):
        """Session touch() updates last_activity timestamp."""
        manager = SessionManager()
        session = manager.create_session()

        original_time = session.last_activity

        # Small delay
        time.sleep(0.01)

        # Touch the session
        session.touch()

        assert session.last_activity > original_time


class TestWizardStepDataclass:
    """Tests for WizardStep dataclass."""

    def test_wizard_step_creation(self):
        """WizardStep can be created with required fields."""
        step = WizardStep(
            name="test_step",
            title="Test Step",
            prompts=["prompt1", "prompt2"],
        )

        assert step.name == "test_step"
        assert step.title == "Test Step"
        assert step.prompts == ["prompt1", "prompt2"]
        assert step.required is True
        assert step.completed is False
        assert step.data == {}

    def test_wizard_step_optional_fields(self):
        """WizardStep optional fields work correctly."""
        step = WizardStep(
            name="test_step",
            title="Test Step",
            prompts=["prompt1"],
            required=False,
            completed=True,
            data={"key": "value"},
        )

        assert step.required is False
        assert step.completed is True
        assert step.data == {"key": "value"}


class TestWizardSessionDataclass:
    """Tests for WizardSession dataclass."""

    def test_wizard_session_creation(self):
        """WizardSession can be created with minimal fields."""
        session = WizardSession(session_id="test-id-123")

        assert session.session_id == "test-id-123"
        assert session.current_step == 0
        assert session.steps == []
        assert session.answers == {}
        assert session.validation_errors == []
        assert session.is_complete is False

    def test_wizard_session_advance_step(self):
        """WizardSession advance_step increments current_step."""
        session = WizardSession(session_id="test")
        original_activity = session.last_activity

        time.sleep(0.01)
        new_step = session.advance_step()

        assert new_step == 1
        assert session.current_step == 1
        assert session.last_activity > original_activity

    def test_wizard_session_go_back(self):
        """WizardSession go_back decrements current_step."""
        session = WizardSession(session_id="test")
        session.advance_step()
        session.advance_step()
        session.is_complete = True

        session.go_back()

        assert session.current_step == 1
        assert session.is_complete is False

    def test_wizard_session_go_back_at_start(self):
        """WizardSession go_back at step 0 stays at 0."""
        session = WizardSession(session_id="test")

        session.go_back()

        assert session.current_step == 0

    def test_wizard_session_is_expired(self):
        """WizardSession is_expired checks TTL correctly."""
        session = WizardSession(session_id="test")

        # Should not be expired with fresh timestamp
        assert session.is_expired(ttl_minutes=60) is False

        # Manually set old timestamp
        session.last_activity = datetime.now() - timedelta(minutes=61)

        # Should now be expired
        assert session.is_expired(ttl_minutes=60) is True
