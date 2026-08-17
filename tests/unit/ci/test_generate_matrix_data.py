"""Unit tests for scripts/ci/generate_matrix_data.py helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from generate_matrix_data import (
    collect_samples,
    normalize_prompt,
    template_defaults_block,
    template_metadata,
)

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestNormalizePrompt:
    def test_dict_prompt_uses_defaults_fallback(self) -> None:
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
    def test_defaults_block_prefers_underscore(self) -> None:
        data = {"_defaults": {"a": 1}, "defaults": {"a": 2}}
        assert template_defaults_block(data) == {"a": 1}

    def test_metadata_block(self) -> None:
        data = {"_metadata": {"name": "riso"}}
        assert template_metadata(data)["name"] == "riso"


@pytest.mark.unit
class TestCollectSamples:
    def test_from_render_matrix_passthrough(self) -> None:
        matrix = {"variants": [{"variant": "default"}]}
        result = collect_samples(matrix)
        assert result["render_matrix"] == matrix
        assert "render_matrix.json" in result["source"]

    def test_from_answers_files(self, tmp_path: Path) -> None:
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
