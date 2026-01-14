"""Unit tests for render_matrix.py"""

import json
import pytest


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestVariantDiscovery:
    """Tests for sample variant discovery."""

    def test_discovers_variants_from_samples(self, temp_dir, monkeypatch):
        """Should discover variants from samples directory."""
        from render_matrix import discover_variants

        samples_dir = temp_dir / "samples"

        # Create sample variant directories
        (samples_dir / "default").mkdir(parents=True)
        (samples_dir / "default" / "copier-answers.yml").write_text(
            "project_name: Test\n"
        )

        (samples_dir / "api-python").mkdir(parents=True)
        (samples_dir / "api-python" / "copier-answers.yml").write_text(
            "project_name: API\n"
        )

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
        from render_matrix import discover_variants
        import render_matrix

        samples_dir = temp_dir / "samples"

        (samples_dir / "default").mkdir(parents=True)
        (samples_dir / "default" / "copier-answers.yml").write_text("name: Test\n")

        (samples_dir / "metadata").mkdir(parents=True)
        (samples_dir / "metadata" / "module_success.json").write_text("{}")

        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()
        variant_names = [v[0] for v in variants]

        assert "default" in variant_names
        assert "metadata" not in variant_names

    def test_empty_samples_directory(self, temp_dir, monkeypatch):
        """Should return empty list for empty samples dir."""
        from render_matrix import discover_variants
        import render_matrix

        samples_dir = temp_dir / "samples"
        samples_dir.mkdir(parents=True)

        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()
        assert variants == []

    def test_returns_sorted_variants(self, temp_dir, monkeypatch):
        """Should return variants in sorted order."""
        from render_matrix import discover_variants
        import render_matrix

        samples_dir = temp_dir / "samples"

        # Create variants in non-alphabetical order
        for variant in ["zebra", "alpha", "middle"]:
            variant_dir = samples_dir / variant
            variant_dir.mkdir(parents=True)
            (variant_dir / "copier-answers.yml").write_text(f"name: {variant}\n")

        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()
        variant_names = [v[0] for v in variants]

        # Should be alphabetically sorted
        assert variant_names == ["alpha", "middle", "zebra"]


@pytest.mark.unit
class TestSmokeResultsLoading:
    """Tests for smoke results loading."""

    def test_loads_valid_smoke_results(self, temp_dir):
        """Should load valid smoke results JSON."""
        from render_matrix import load_smoke_results

        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        smoke_file = variant_dir / "smoke-results.json"
        smoke_file.write_text(
            json.dumps(
                {
                    "results": [
                        {"module": "cli", "status": "passed", "duration": 1.5},
                        {"module": "api", "status": "failed", "error": "Import error"},
                    ]
                }
            )
        )

        results = load_smoke_results(answers_file)
        assert results is not None
        assert "results" in results
        assert len(results["results"]) == 2
        assert results["results"][0]["module"] == "cli"
        assert results["results"][0]["status"] == "passed"

    def test_returns_none_for_missing_file(self, temp_dir):
        """Should return None for missing smoke results file."""
        from render_matrix import load_smoke_results

        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        results = load_smoke_results(answers_file)
        assert results is None

    def test_handles_invalid_json(self, temp_dir):
        """Should raise error for invalid JSON."""
        from render_matrix import load_smoke_results

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
        from render_matrix import load_smoke_results

        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        smoke_file = variant_dir / "smoke-results.json"
        smoke_file.write_text(json.dumps({"results": []}))

        results = load_smoke_results(answers_file)
        assert results is not None
        assert results["results"] == []


@pytest.mark.unit
class TestPostGenMetadataLoading:
    """Tests for post-generation metadata loading."""

    def test_loads_valid_metadata(self, temp_dir):
        """Should load valid post-gen metadata."""
        from render_matrix import load_post_gen_metadata

        variant_dir = temp_dir / "variant"
        render_dir = variant_dir / "render"
        riso_dir = render_dir / ".riso"
        riso_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        metadata_file = riso_dir / "post_gen_metadata.json"
        metadata_file.write_text(
            json.dumps(
                {"workflow_validation": "passed", "container_validation": "validated"}
            )
        )

        metadata = load_post_gen_metadata(answers_file)
        assert metadata is not None
        assert metadata["workflow_validation"] == "passed"
        assert metadata["container_validation"] == "validated"

    def test_returns_none_for_missing_metadata(self, temp_dir):
        """Should return None when metadata file doesn't exist."""
        from render_matrix import load_post_gen_metadata

        variant_dir = temp_dir / "variant"
        variant_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\n")

        metadata = load_post_gen_metadata(answers_file)
        assert metadata is None

    def test_handles_invalid_metadata_json(self, temp_dir):
        """Should raise error for invalid metadata JSON."""
        from render_matrix import load_post_gen_metadata

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
        from render_matrix import load_post_gen_metadata

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


@pytest.mark.unit
class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_discovers_and_loads_complete_variant(self, temp_dir, monkeypatch):
        """Should discover variant and load all associated metadata."""
        from render_matrix import (
            discover_variants,
            load_smoke_results,
            load_post_gen_metadata,
        )
        import render_matrix

        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "default"
        variant_dir.mkdir(parents=True)

        # Create copier answers
        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test Project\napi_tracks: python\n")

        # Create smoke results
        smoke_file = variant_dir / "smoke-results.json"
        smoke_file.write_text(
            json.dumps(
                {"results": [{"module": "cli", "status": "passed", "duration": 0.5}]}
            )
        )

        # Create post-gen metadata
        render_dir = variant_dir / "render"
        riso_dir = render_dir / ".riso"
        riso_dir.mkdir(parents=True)
        metadata_file = riso_dir / "post_gen_metadata.json"
        metadata_file.write_text(json.dumps({"workflow_validation": "passed"}))

        # Discover variants
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


@pytest.mark.unit
class TestRenderVariant:
    """Tests for render_variant function."""

    def test_render_variant_basic(self, temp_dir, monkeypatch):
        """Should render variant and return metadata."""
        from unittest.mock import patch, MagicMock
        import render_matrix

        # Setup paths
        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "test-variant"
        variant_dir.mkdir(parents=True)
        render_dir = variant_dir / "render"
        render_dir.mkdir()

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: Test\napi_tracks: none\n")

        # Mock subprocess.run to avoid actually running render script
        with patch("subprocess.run") as mock_run, \
             patch.object(render_matrix, "load_post_gen_metadata") as mock_metadata, \
             patch.object(render_matrix, "load_smoke_results") as mock_smoke:
            mock_run.return_value = MagicMock(returncode=0)
            mock_metadata.return_value = {"workflow_validation": "passed"}
            mock_smoke.return_value = None

            monkeypatch.setattr(render_matrix, "REPO_ROOT", temp_dir)
            monkeypatch.setattr(render_matrix, "RENDER_SCRIPT", temp_dir / "render.sh")

            result = render_matrix.render_variant("test-variant", answers_file)

            assert result["variant"] == "test-variant"
            assert result["workflow_validation"] == "passed"
            mock_run.assert_called_once()

    def test_render_variant_with_containers(self, temp_dir, monkeypatch):
        """Should check container files when api_tracks is set."""
        from unittest.mock import patch, MagicMock
        import render_matrix

        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "api-variant"
        variant_dir.mkdir(parents=True)
        render_dir = variant_dir / "render"
        docker_dir = render_dir / ".docker"
        docker_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: API\napi_tracks: python\n")

        # Create container files
        (docker_dir / "Dockerfile").write_text("FROM python:3.11")
        (render_dir / "docker-compose.yml").write_text("version: '3'")

        with patch("subprocess.run") as mock_run, \
             patch.object(render_matrix, "load_post_gen_metadata") as mock_metadata, \
             patch.object(render_matrix, "load_smoke_results") as mock_smoke:
            # First call is render script, second could be hadolint
            mock_run.return_value = MagicMock(returncode=0)
            mock_metadata.return_value = {"workflow_validation": "passed"}
            mock_smoke.return_value = None

            monkeypatch.setattr(render_matrix, "REPO_ROOT", temp_dir)
            monkeypatch.setattr(render_matrix, "RENDER_SCRIPT", temp_dir / "render.sh")

            result = render_matrix.render_variant("api-variant", answers_file)

            # Either files_present (no hadolint) or validated (hadolint passed)
            assert result["container_status"] in ("files_present", "validated")

    def test_render_variant_missing_containers(self, temp_dir, monkeypatch):
        """Should report files_missing when container files missing."""
        from unittest.mock import patch, MagicMock
        import render_matrix

        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "api-variant"
        variant_dir.mkdir(parents=True)
        render_dir = variant_dir / "render"
        render_dir.mkdir()

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text("project_name: API\napi_tracks: python\n")

        with patch("subprocess.run") as mock_run, \
             patch.object(render_matrix, "load_post_gen_metadata") as mock_metadata, \
             patch.object(render_matrix, "load_smoke_results") as mock_smoke:
            mock_run.return_value = MagicMock(returncode=0)
            mock_metadata.return_value = {"workflow_validation": "passed"}
            mock_smoke.return_value = None

            monkeypatch.setattr(render_matrix, "REPO_ROOT", temp_dir)
            monkeypatch.setattr(render_matrix, "RENDER_SCRIPT", temp_dir / "render.sh")

            result = render_matrix.render_variant("api-variant", answers_file)

            assert result["container_status"] == "files_missing"


@pytest.mark.unit
class TestMain:
    """Tests for main function."""

    def test_main_skip_render_with_existing(self, temp_dir, monkeypatch):
        """Should skip rendering when --skip-render and file exists."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        metadata_dir.mkdir()

        # Create existing render_matrix.json
        existing_data = {
            "variants": [
                {
                    "variant": "default",
                    "smoke_results": {"results": [{"module": "cli", "status": "passed"}]}
                }
            ]
        }
        (metadata_dir / "render_matrix.json").write_text(json.dumps(existing_data))

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)

        with patch("sys.argv", ["render_matrix.py", "--skip-render"]):
            render_matrix.main()

        # Should have updated with module_success
        result = json.loads((metadata_dir / "render_matrix.json").read_text())
        assert "module_success" in result

    def test_main_renders_variants(self, temp_dir, monkeypatch):
        """Should render all discovered variants."""
        from unittest.mock import patch, MagicMock
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "test"
        variant_dir.mkdir(parents=True)
        (variant_dir / "copier-answers.yml").write_text("name: Test\n")

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        with patch("sys.argv", ["render_matrix.py"]), \
             patch.object(render_matrix, "render_variant") as mock_render:
            mock_render.return_value = {
                "variant": "test",
                "answers": str(variant_dir / "copier-answers.yml"),
                "destination": str(variant_dir / "render"),
                "smoke_results": None,
                "workflow_validation": "passed",
                "container_status": "not_applicable",
            }

            render_matrix.main()

        mock_render.assert_called_once()
        assert (metadata_dir / "render_matrix.json").exists()

    def test_main_with_quality_artifacts(self, temp_dir, monkeypatch):
        """Should include quality artifacts in output."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        metadata_dir.mkdir()

        # Create quality artifact
        artifact_file = temp_dir / "quality.json"
        artifact_file.write_text(json.dumps({"lint": "passed", "tests": "passed"}))

        # Create existing render_matrix.json
        (metadata_dir / "render_matrix.json").write_text(json.dumps({"variants": []}))

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)

        with patch("sys.argv", ["render_matrix.py", "--skip-render", 
                               "--quality-artifacts", str(artifact_file),
                               "--retention-days", "30"]):
            render_matrix.main()

        result = json.loads((metadata_dir / "render_matrix.json").read_text())
        assert "quality_runs" in result
        assert result["quality_retention_days"] == 30
