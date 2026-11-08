"""Unit tests for scripts/ci/generate_matrix_data.py helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from generate_matrix_data import (
    collect_samples,
    normalize_prompt,
    sanitize_payload,
    template_defaults_block,
    template_metadata,
)

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestNormalizePrompt:
    """Prompt rows retain effective defaults and a consistent field shape."""

    def test_dict_prompt_uses_defaults_fallback(self) -> None:
        """Effective template defaults override a prompt-local default."""
        prompt = {
            "type": "str",
            "choices": ["a", "b"],
            "default": "a",
            "when": "{{ true }}",
            "help": "h",
            "multiselect": True,
        }
        defaults = {"quality_profile": "standard"}
        entry = normalize_prompt("quality_profile", prompt, defaults)
        assert entry["key"] == "quality_profile"
        assert entry["type"] == "str"
        assert entry["choices"] == ["a", "b"]
        assert entry["default"] == "standard"
        assert entry["multiselect"] is True

    def test_non_dict_prompt_shape(self) -> None:
        """Scalar prompt definitions still produce the complete row shape."""
        entry = normalize_prompt("x", "not-a-dict", {"x": 1})
        assert entry == {
            "key": "x",
            "type": None,
            "choices": None,
            "default": 1,
            "when": None,
            "help": None,
            "multiselect": None,
        }


@pytest.mark.unit
class TestTemplateBlocks:
    """Copier metadata and defaults blocks use the maintained key names."""

    def test_defaults_block_prefers_underscore(self) -> None:
        """The underscored defaults block takes precedence when both exist."""
        data = {"_defaults": {"a": 1}, "defaults": {"a": 2}}
        assert template_defaults_block(data) == {"a": 1}

    def test_metadata_block(self) -> None:
        """Template metadata is extracted without losing its name."""
        data = {"_metadata": {"name": "riso"}}
        assert template_metadata(data)["name"] == "riso"


@pytest.mark.unit
class TestCollectSamples:
    """Matrix data preserves render evidence and nested sample identities."""

    def test_from_render_matrix_passthrough(self) -> None:
        """Existing render evidence is used without rebuilding variant rows."""
        matrix = {"variants": [{"variant": "default"}]}
        result = collect_samples(matrix)
        assert result["render_matrix"] == matrix
        assert result["source"] == "samples/metadata/render_matrix.json"

    def test_from_answers_files(self, tmp_path: Path) -> None:
        """Answer-file discovery retains sample configuration values."""
        sample = tmp_path / "demo"
        sample.mkdir()
        answers = {"project_name": "Demo", "quality_profile": "standard"}
        (sample / "copier-answers.yml").write_text(
            yaml.safe_dump(answers), encoding="utf-8"
        )

        with patch("generate_matrix_data.SAMPLES_DIR", tmp_path):
            result = collect_samples(None)

        assert result["source"] == "samples/**/copier-answers.yml"
        assert len(result["variants"]) == 1
        assert result["variants"][0]["variant"] == "demo"
        assert result["variants"][0]["answers"]["project_name"] == "Demo"

    def test_discovers_nested_saas_starter_without_flattening(
        self, tmp_path: Path
    ) -> None:
        """Nested sample names retain their full relative paths."""
        nested = tmp_path / "saas-starter" / "vercel-starter"
        nested.mkdir(parents=True)
        (nested / "copier-answers.yml").write_text(
            yaml.safe_dump({"project_name": "Nested"}), encoding="utf-8"
        )
        (tmp_path / "default").mkdir()
        (tmp_path / "default" / "copier-answers.yml").write_text(
            yaml.safe_dump({"project_name": "Default"}), encoding="utf-8"
        )

        with patch("generate_matrix_data.SAMPLES_DIR", tmp_path):
            result = collect_samples(None)

        names = [row["variant"] for row in result["variants"]]
        assert "default" in names
        assert "saas-starter/vercel-starter" in names
        assert "vercel-starter" not in names


@pytest.mark.unit
class TestSanitizePayload:
    """Published snapshots omit machine paths and captured stdio."""

    def test_relativizes_repo_paths_and_drops_stdio(self, tmp_path: Path) -> None:
        """Absolute repo paths become relative; stdio keys are removed."""
        repo = tmp_path
        payload = {
            "sources": {
                "template": str(repo / "template" / "copier.yml"),
                "render_matrix": str(
                    repo / "samples" / "metadata" / "render_matrix.json"
                ),
            },
            "samples": {
                "source": "samples/metadata/render_matrix.json",
                "render_matrix": {
                    "variants": [
                        {
                            "answers": str(
                                repo / "samples" / "default" / "copier-answers.yml"
                            ),
                            "destination": str(repo / "samples" / "default" / "render"),
                            "stdout": "build log",
                            "stderr": "build err",
                            "nested": {"stderr": "inner", "status": "ok"},
                        }
                    ]
                },
            },
            "stdout": "top-level log",
            "outside": str(repo.parent / "elsewhere.txt"),
        }

        cleaned = sanitize_payload(payload, repo)

        assert cleaned["sources"]["template"] == "template/copier.yml"
        assert (
            cleaned["sources"]["render_matrix"] == "samples/metadata/render_matrix.json"
        )
        assert cleaned["samples"]["source"] == "samples/metadata/render_matrix.json"
        variant = cleaned["samples"]["render_matrix"]["variants"][0]
        assert variant["answers"] == "samples/default/copier-answers.yml"
        assert variant["destination"] == "samples/default/render"
        assert "stdout" not in variant
        assert "stderr" not in variant
        assert variant["nested"] == {"status": "ok"}
        assert "stdout" not in cleaned
        assert "stderr" not in cleaned
        assert cleaned["outside"] == str(repo.parent / "elsewhere.txt")
