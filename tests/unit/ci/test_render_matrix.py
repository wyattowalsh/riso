"""Unit tests for render_matrix.py"""
import json
import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parents[3] / "scripts" / "ci"))

from render_matrix import discover_variants, load_smoke_results, load_post_gen_metadata


class TestVariantDiscovery:
    """Tests for sample variant discovery."""

    def test_discovers_variants_from_samples(self, temp_dir, monkeypatch):
        """Should discover variants from samples directory."""
        samples_dir = temp_dir / "samples"

        # Create sample variant directories
        (samples_dir / "default").mkdir(parents=True)
        (samples_dir / "default" / "copier-answers.yml").write_text("project_name: Test\n")

        (samples_dir / "api-python").mkdir(parents=True)
        (samples_dir / "api-python" / "copier-answers.yml").write_text("project_name: API\n")

        # Monkey patch SAMPLES_DIR to use our temp directory
        import render_matrix
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()

        # Should return list of tuples (variant_name, answers_path)
        assert len(variants) == 2
        variant_names = [v[0] for v in variants]
        assert "api-python" in variant_names
        assert "default" in variant_names

    def test_ignores_metadata_directory(self, temp_dir, monkeypatch):
        """Should ignore metadata directory."""
        samples_dir = temp_dir / "samples"

        (samples_dir / "default").mkdir(parents=True)
        (samples_dir / "default" / "copier-answers.yml").write_text("name: Test\n")

        (samples_dir / "metadata").mkdir(parents=True)
        (samples_dir / "metadata" / "module_success.json").write_text("{}")

        import render_matrix
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()
        variant_names = [v[0] for v in variants]

        assert "default" in variant_names
        assert "metadata" not in variant_names

    def test_empty_samples_directory(self, temp_dir, monkeypatch):
        """Should return empty list for empty samples dir."""
        samples_dir = temp_dir / "samples"
        samples_dir.mkdir(parents=True)

        import render_matrix
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()
        assert variants == []

    def test_returns_sorted_variants(self, temp_dir, monkeypatch):
        """Should return variants in sorted order."""
        samples_dir = temp_dir / "samples"

        # Create variants in non-alphabetical order
        for variant in ["zebra", "alpha", "middle"]:
            variant_dir = samples_dir / variant
            variant_dir.mkdir(parents=True)
            (variant_dir / "copier-answers.yml").write_text(f"name: {variant}\n")

        import render_matrix
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()
        variant_names = [v[0] for v in variants]

        # Should be alphabetically sorted
        assert variant_names == ["alpha", "middle", "zebra"]


class TestSmokeResultsLoading:
    """Tests for smoke results loading."""

    def test_loads_valid_smoke_results(self, temp_dir):
        """Should load valid smoke results JSON."""
        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        smoke_file = variant_dir / "smoke-results.json"
        smoke_file.write_text(json.dumps({
            "results": [
                {"module": "cli", "status": "passed", "duration": 1.5},
                {"module": "api", "status": "failed", "error": "Import error"}
            ]
        }))

        results = load_smoke_results(answers_file)
        assert results is not None
        assert "results" in results
        assert len(results["results"]) == 2
        assert results["results"][0]["module"] == "cli"
        assert results["results"][0]["status"] == "passed"

    def test_returns_none_for_missing_file(self, temp_dir):
        """Should return None for missing smoke results file."""
        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        results = load_smoke_results(answers_file)
        assert results is None

    def test_handles_invalid_json(self, temp_dir):
        """Should raise error for invalid JSON."""
        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        smoke_file = variant_dir / "smoke-results.json"
        smoke_file.write_text("not valid json")

        with pytest.raises(json.JSONDecodeError):
            load_smoke_results(answers_file)

    def test_loads_empty_results_array(self, temp_dir):
        """Should handle empty results array."""
        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        smoke_file = variant_dir / "smoke-results.json"
        smoke_file.write_text(json.dumps({"results": []}))

        results = load_smoke_results(answers_file)
        assert results is not None
        assert results["results"] == []


class TestPostGenMetadataLoading:
    """Tests for post-generation metadata loading."""

    def test_loads_valid_metadata(self, temp_dir):
        """Should load valid post-gen metadata."""
        variant_dir = temp_dir / "variant"
        render_dir = variant_dir / "render"
        riso_dir = render_dir / ".riso"
        riso_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        metadata_file = riso_dir / "post_gen_metadata.json"
        metadata_file.write_text(json.dumps({
            "workflow_validation": "passed",
            "container_validation": "validated"
        }))

        metadata = load_post_gen_metadata(answers_file)
        assert metadata is not None
        assert metadata["workflow_validation"] == "passed"
        assert metadata["container_validation"] == "validated"

    def test_returns_none_for_missing_metadata(self, temp_dir):
        """Should return None when metadata file doesn't exist."""
        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        metadata = load_post_gen_metadata(answers_file)
        assert metadata is None

    def test_handles_invalid_metadata_json(self, temp_dir):
        """Should raise error for invalid metadata JSON."""
        variant_dir = temp_dir / "variant"
        render_dir = variant_dir / "render"
        riso_dir = render_dir / ".riso"
        riso_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        metadata_file = riso_dir / "post_gen_metadata.json"
        metadata_file.write_text("not valid json")

        with pytest.raises(json.JSONDecodeError):
            load_post_gen_metadata(answers_file)

    def test_loads_minimal_metadata(self, temp_dir):
        """Should handle minimal metadata with missing fields."""
        variant_dir = temp_dir / "variant"
        render_dir = variant_dir / "render"
        riso_dir = render_dir / ".riso"
        riso_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        metadata_file = riso_dir / "post_gen_metadata.json"
        metadata_file.write_text(json.dumps({}))

        metadata = load_post_gen_metadata(answers_file)
        assert metadata is not None
        assert isinstance(metadata, dict)
        assert len(metadata) == 0


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_discovers_and_loads_complete_variant(self, temp_dir, monkeypatch):
        """Should discover variant and load all associated metadata."""
        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "default"
        variant_dir.mkdir(parents=True)

        # Create copier answers
        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test Project\napi_tracks: python\n")

        # Create smoke results
        smoke_file = variant_dir / "smoke-results.json"
        smoke_file.write_text(json.dumps({
            "results": [
                {"module": "cli", "status": "passed", "duration": 0.5}
            ]
        }))

        # Create post-gen metadata
        render_dir = variant_dir / "render"
        riso_dir = render_dir / ".riso"
        riso_dir.mkdir(parents=True)
        metadata_file = riso_dir / "post_gen_metadata.json"
        metadata_file.write_text(json.dumps({
            "workflow_validation": "passed"
        }))

        # Discover variants
        import render_matrix
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()
        assert len(variants) == 1

        variant_name, variant_answers = variants[0]
        assert variant_name == "default"

        # Load associated data
        smoke_results = load_smoke_results(variant_answers)
        assert smoke_results is not None
        assert len(smoke_results["results"]) == 1

        metadata = load_post_gen_metadata(variant_answers)
        assert metadata is not None
        assert metadata["workflow_validation"] == "passed"
