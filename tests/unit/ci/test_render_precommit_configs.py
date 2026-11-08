"""Unit tests for render_precommit_configs.py."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from render_precommit_configs import load_answers, main, python_enabled, validate_render

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestPythonEnabled:
    """Python layout checks follow the enabled component language tracks."""

    def test_enabled_when_api_python(self):
        """An enabled Python API activates Python layout validation."""
        answers = {"api_module": "enabled", "api_languages": ["python"]}
        assert python_enabled(answers) is True

    def test_disabled_when_no_python_components(self):
        """Projects without Python components skip Python-specific checks."""
        answers = {"api_module": "disabled", "cli_module": "disabled"}
        assert python_enabled(answers) is False


@pytest.mark.unit
class TestValidateRender:
    """Rendered pre-commit layouts are checked for missing or obsolete files."""

    def test_detects_missing_precommit(self, tmp_path):
        """A render without pre-commit configuration reports an error."""
        errors = validate_render(
            tmp_path, {"api_module": "enabled", "api_languages": ["python"]}
        )
        assert "missing root .pre-commit-config.yaml" in errors

    def test_detects_legacy_pyproject_stub(self, tmp_path):
        """An obsolete root pyproject stub is rejected for Python projects."""
        (tmp_path / "python").mkdir()
        (tmp_path / "python" / "pyproject.toml").write_text("[project]\nname='x'\n")
        (tmp_path / "pyproject.toml").write_text("[tool.uv.tasks]\nquality='x'\n")
        (tmp_path / "Makefile").write_text(
            "hooks:\n\t@$(MAKE) -f quality/makefile.quality hooks\n"
        )
        (tmp_path / "quality").mkdir()
        (tmp_path / "quality" / "makefile.quality").write_text("hooks:\n\ttrue\n")
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")

        errors = validate_render(
            tmp_path,
            {
                "api_module": "enabled",
                "api_languages": ["python"],
                "task_runner": "makefile",
            },
        )
        assert any("legacy root pyproject.toml" in err for err in errors)


@pytest.mark.unit
class TestMain:
    """Pre-commit layout validation selects and checks requested renders."""

    def test_missing_render_dir_fails(self, tmp_path, monkeypatch):
        """Missing render directories produce a failing command result."""
        samples = tmp_path / "samples"
        variant = samples / "demo"
        variant.mkdir(parents=True)
        (variant / "copier-answers.yml").write_text(
            "api_module: enabled\napi_languages: [python]\n"
        )
        monkeypatch.setattr("render_precommit_configs.SAMPLES_DIR", samples)

        with patch(
            "sys.argv",
            ["render_precommit_configs.py", "--variants", "demo"],
        ):
            assert main() == 1

    def test_load_answers_empty_when_missing(self, tmp_path):
        """Absent answer files produce an empty configuration mapping."""
        assert load_answers(tmp_path) == {}

    def test_valid_minimal_render_passes(self, tmp_path):
        """A complete minimal render passes the layout check."""
        (tmp_path / "python").mkdir()
        (tmp_path / "python" / "pyproject.toml").write_text("[project]\nname='x'\n")
        (tmp_path / "Makefile").write_text(
            "hooks:\n\t@$(MAKE) -f quality/makefile.quality hooks\n"
        )
        (tmp_path / "quality").mkdir()
        (tmp_path / "quality" / "makefile.quality").write_text("hooks:\n\ttrue\n")
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
        (tmp_path / ".riso").mkdir()
        (tmp_path / ".riso" / "post_gen_metadata.json").write_text(
            json.dumps({"pre_commit": {"install_command": "make hooks"}})
        )

        errors = validate_render(
            tmp_path,
            {
                "api_module": "enabled",
                "api_languages": ["python"],
                "task_runner": "makefile",
            },
        )
        assert errors == []

    def test_valid_just_render_passes(self, tmp_path):
        """A valid Just-based render passes the layout check."""
        (tmp_path / "python").mkdir()
        (tmp_path / "python" / "pyproject.toml").write_text("[project]\nname='x'\n")
        (tmp_path / "justfile").write_text("import 'quality/justfile.quality'\n")
        (tmp_path / "quality").mkdir()
        (tmp_path / "quality" / "justfile.quality").write_text("hooks:\n\ttrue\n")
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
        (tmp_path / ".riso").mkdir()
        (tmp_path / ".riso" / "post_gen_metadata.json").write_text(
            json.dumps({"pre_commit": {"install_command": "just hooks"}})
        )

        errors = validate_render(
            tmp_path,
            {
                "api_module": "enabled",
                "api_languages": ["python"],
                "task_runner": "just",
            },
        )
        assert errors == []
