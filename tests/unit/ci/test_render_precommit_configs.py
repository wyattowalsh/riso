"""Unit tests for render_precommit_configs.py."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from render_precommit_configs import load_answers, main, python_enabled, validate_render

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestPythonEnabled:
    def test_enabled_when_api_python(self):
        answers = {"api_module": "enabled", "api_languages": ["python"]}
        assert python_enabled(answers) is True

    def test_disabled_when_no_python_components(self):
        answers = {"api_module": "disabled", "cli_module": "disabled"}
        assert python_enabled(answers) is False


@pytest.mark.unit
class TestValidateRender:
    def test_detects_missing_precommit(self, tmp_path):
        errors = validate_render(
            tmp_path, {"api_module": "enabled", "api_languages": ["python"]}
        )
        assert "missing root .pre-commit-config.yaml" in errors

    def test_detects_legacy_pyproject_stub(self, tmp_path):
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
            tmp_path, {"api_module": "enabled", "api_languages": ["python"]}
        )
        assert any("legacy root pyproject.toml" in err for err in errors)


@pytest.mark.unit
class TestMain:
    def test_missing_render_dir_fails(self, tmp_path, monkeypatch):
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
        assert load_answers(tmp_path) == {}

    def test_valid_minimal_render_passes(self, tmp_path):
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
            tmp_path, {"api_module": "enabled", "api_languages": ["python"]}
        )
        assert errors == []
