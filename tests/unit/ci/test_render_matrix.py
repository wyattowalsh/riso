"""Unit tests for render_matrix.py"""

# The ci_scripts_path fixture must configure sys.path before script imports.
# pylint: disable=import-outside-toplevel

import json
import pytest


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


def _variant_record(name="default", status="ok", returncode=0):
    """Build an evidence record with the fields emitted by render_variant."""
    return {
        "variant": name,
        "answers": f"samples/{name}/copier-answers.yml",
        "destination": f"samples/{name}/render",
        "smoke_results": None,
        "workflow_validation": "unknown",
        "container_status": "not_applicable",
        "render_status": status,
        "render_returncode": returncode,
    }


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

    def test_discovers_nested_saas_starter_without_flattening(
        self, temp_dir, monkeypatch
    ):
        """Nested answers stay relative to samples/ and are not basename-flattened."""
        from render_matrix import discover_variants
        import render_matrix

        samples_dir = temp_dir / "samples"
        nested = samples_dir / "saas-starter" / "vercel-starter"
        nested.mkdir(parents=True)
        (nested / "copier-answers.yml").write_text("project_name: Nested\n")
        (samples_dir / "default").mkdir(parents=True)
        (samples_dir / "default" / "copier-answers.yml").write_text(
            "project_name: Default\n"
        )
        render_copy = samples_dir / "default" / "render" / "copier-answers.yml"
        render_copy.parent.mkdir(parents=True)
        render_copy.write_text("project_name: ShouldIgnore\n")

        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        variants = discover_variants()
        variant_names = [v[0] for v in variants]
        assert "default" in variant_names
        assert "saas-starter/vercel-starter" in variant_names
        assert "vercel-starter" not in variant_names
        dest_by_name = {name: answers.parent / "render" for name, answers in variants}
        assert dest_by_name["saas-starter/vercel-starter"] == nested / "render"


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
                    "variant": "variant",
                    "modules": {
                        "cli": {"status": "passed", "duration": 1.5},
                        "api": {"status": "failed", "error": "Import error"},
                    },
                }
            )
        )

        results = load_smoke_results(answers_file)
        assert results is not None
        assert "modules" in results
        assert len(results["modules"]) == 2
        assert results["modules"]["cli"]["status"] == "passed"

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
        smoke_file.write_text(json.dumps({"variant": "variant", "modules": {}}))

        results = load_smoke_results(answers_file)
        assert results is not None
        assert results["modules"] == {}


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
class TestIntegration:  # pylint: disable=too-few-public-methods
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
        answers_file.write_text(
            "project_name: Test Project\n"
            "api_module: enabled\n"
            "api_languages:\n"
            "  - python\n"
        )

        # Create smoke results
        smoke_file = variant_dir / "smoke-results.json"
        smoke_file.write_text(
            json.dumps(
                {
                    "variant": "default",
                    "modules": {"cli": {"status": "passed", "duration": 0.5}},
                }
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
        assert len(smoke_results["modules"]) == 1

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
        answers_file.write_text("project_name: Test\napi_module: disabled\n")

        # Mock subprocess.run to avoid actually running render script
        with (
            patch("subprocess.run") as mock_run,
            patch.object(render_matrix, "load_post_gen_metadata") as mock_metadata,
            patch.object(render_matrix, "load_smoke_results") as mock_smoke,
        ):
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
        """Should check container files when API languages are set."""
        from unittest.mock import patch, MagicMock
        import render_matrix

        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "api-variant"
        variant_dir.mkdir(parents=True)
        render_dir = variant_dir / "render"
        docker_dir = render_dir / ".docker"
        docker_dir.mkdir(parents=True)

        answers_file = variant_dir / "copier-answers.yml"
        answers_file.write_text(
            "project_name: API\napi_module: enabled\napi_languages:\n  - python\n"
        )

        # Create container files
        (docker_dir / "Dockerfile").write_text("FROM python:3.11")
        (render_dir / "docker-compose.yml").write_text("version: '3'")

        with (
            patch("subprocess.run") as mock_run,
            patch.object(render_matrix, "load_post_gen_metadata") as mock_metadata,
            patch.object(render_matrix, "load_smoke_results") as mock_smoke,
        ):
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
        answers_file.write_text(
            "project_name: API\napi_module: enabled\napi_languages:\n  - python\n"
        )

        with (
            patch("subprocess.run") as mock_run,
            patch.object(render_matrix, "load_post_gen_metadata") as mock_metadata,
            patch.object(render_matrix, "load_smoke_results") as mock_smoke,
        ):
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

    def test_quality_only_preserves_existing_render_evidence(
        self, temp_dir, monkeypatch
    ):
        """Quality consolidation must never manufacture or rewrite render results."""
        from unittest.mock import patch
        import render_matrix

        metadata = temp_dir / "metadata"
        metadata.mkdir()
        original = '{"variants":[{"variant":"default","render_status":"failed"}]}'
        (metadata / "render_matrix.json").write_text(original)
        artifact = temp_dir / "quality.json"
        artifact.write_text(
            json.dumps({"profile": "standard", "durations": {"ruff": 1.2, "ty": 0.5}})
        )
        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata)
        with (
            patch(
                "sys.argv",
                [
                    "render_matrix.py",
                    "--quality-only",
                    "--quality-artifacts",
                    str(artifact),
                ],
            ),
            patch.object(render_matrix, "render_variant") as render,
        ):
            render_matrix.main()
        render.assert_not_called()
        assert (metadata / "render_matrix.json").read_text() == original
        report = json.loads((metadata / "quality_summary.json").read_text())
        assert report["kind"] == "quality-only"
        assert "variants" not in report
        assert report["quality_runs"][0]["profile"] == "standard"

    def test_quality_only_missing_artifact_fails_without_rendering(
        self, temp_dir, monkeypatch
    ):
        """Missing downloaded quality evidence fails before any output is created."""
        from unittest.mock import patch
        import render_matrix

        metadata = temp_dir / "metadata"
        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata)
        with (
            patch(
                "sys.argv",
                [
                    "render_matrix.py",
                    "--quality-only",
                    "--quality-artifacts",
                    str(temp_dir / "absent.json"),
                ],
            ),
            patch.object(render_matrix, "render_variant") as render,
            pytest.raises(SystemExit) as error,
        ):
            render_matrix.main()
        assert error.value.code == 2
        render.assert_not_called()
        assert not metadata.exists()

    def test_skip_render_missing_metadata_never_starts_render(
        self, temp_dir, monkeypatch
    ):
        """Verify skip render missing metadata never starts render."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "absent-metadata"
        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)
        with (
            patch("sys.argv", ["render_matrix.py", "--skip-render"]),
            patch.object(render_matrix, "render_variant") as render,
            pytest.raises(SystemExit) as exc,
        ):
            render_matrix.main()
        assert exc.value.code == 2
        render.assert_not_called()
        assert not metadata_dir.exists()

    def test_main_skip_render_with_existing(self, temp_dir, monkeypatch):
        """Should skip rendering when --skip-render and file exists."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        metadata_dir.mkdir()

        # Create existing render_matrix.json
        record = _variant_record()
        record["smoke_results"] = {
            "modules": {"cli": {"status": "passed"}},
        }
        existing_data = {
            "variants": [record],
            "quality_runs": [{"profile": "standard", "durations": {"ruff": 1.0}}],
            "quality_retention_days": 30,
        }
        (metadata_dir / "render_matrix.json").write_text(json.dumps(existing_data))

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)

        with (
            patch("sys.argv", ["render_matrix.py", "--skip-render"]),
            patch.object(render_matrix, "render_variant") as render,
        ):
            render_matrix.main()

        # Should have updated with module_success
        result = json.loads((metadata_dir / "render_matrix.json").read_text())
        render.assert_not_called()
        assert result["variants"] == existing_data["variants"]
        assert result["quality_runs"] == existing_data["quality_runs"]
        assert result["quality_retention_days"] == 30
        assert "module_success" in result

    @pytest.mark.parametrize(
        "payload",
        [
            None,
            [],
            "not a matrix",
            {},
            {"variants": None},
            {"variants": {}},
            {"variants": []},
            {"variants": [None]},
            {"variants": ["default"]},
            {"variants": [{}]},
            {"variants": [_variant_record(), _variant_record()]},
            *(
                {"variants": [_variant_record() | {field: value}]}
                for field, value in (
                    ("variant", ""),
                    ("variant", "   "),
                    ("variant", 1),
                    ("answers", None),
                    ("destination", []),
                    ("workflow_validation", False),
                    ("container_status", {}),
                    ("smoke_results", []),
                    ("render_status", "passed"),
                    ("render_status", "unknown"),
                    ("render_status", []),
                    ("render_returncode", True),
                    ("render_returncode", "0"),
                    ("render_returncode", 0.0),
                    ("render_returncode", 1),
                    ("render_status", "failed"),
                )
            ),
            *(
                {
                    "variants": [
                        {
                            key: value
                            for key, value in _variant_record().items()
                            if key != field
                        }
                    ]
                }
                for field in _variant_record()
            ),
            {"variants": [_variant_record(), {"variant": "bad-later-record"}]},
        ],
    )
    def test_skip_render_rejects_invalid_evidence_before_writing(
        self, temp_dir, monkeypatch, payload
    ):
        """Invalid evidence must not render, aggregate, or overwrite either output."""
        from unittest.mock import patch
        import render_matrix

        metadata = temp_dir / "metadata"
        metadata.mkdir()
        matrix = metadata / "render_matrix.json"
        original = json.dumps(payload, indent=2) + "\n"
        matrix.write_text(original)
        metrics = metadata / "module_success.json"
        metrics.write_text('{"preserve":"existing evidence"}\n')
        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata)
        with (
            patch("sys.argv", ["render_matrix.py", "--skip-render"]),
            patch.object(render_matrix, "render_variant") as render,
            patch.object(render_matrix, "discover_variants") as discover,
            patch.object(render_matrix, "ModuleSuccessRecorder") as recorder,
            pytest.raises(SystemExit) as error,
        ):
            render_matrix.main()
        assert error.value.code == 2
        render.assert_not_called()
        discover.assert_not_called()
        recorder.assert_not_called()
        assert matrix.read_text() == original
        assert metrics.read_text() == '{"preserve":"existing evidence"}\n'

    def test_skip_render_rejects_invalid_json_without_creating_metrics(
        self, temp_dir, monkeypatch
    ):
        """JSON parse errors fail clearly without replacing the original artifact."""
        from unittest.mock import patch
        import render_matrix

        metadata = temp_dir / "metadata"
        metadata.mkdir()
        matrix = metadata / "render_matrix.json"
        original = '{"variants":['
        matrix.write_text(original)
        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata)
        with (
            patch("sys.argv", ["render_matrix.py", "--skip-render"]),
            patch.object(render_matrix, "render_variant") as render,
            pytest.raises(SystemExit) as error,
        ):
            render_matrix.main()
        assert error.value.code == 2
        render.assert_not_called()
        assert matrix.read_text() == original
        assert not (metadata / "module_success.json").exists()

    def test_skip_render_read_error_never_falls_back_to_rendering(
        self, temp_dir, monkeypatch
    ):
        """Unreadable evidence fails even after the initial file-presence check."""
        from unittest.mock import patch
        import render_matrix

        metadata = temp_dir / "metadata"
        metadata.mkdir()
        matrix = metadata / "render_matrix.json"
        original = json.dumps({"variants": [_variant_record()]})
        matrix.write_text(original)
        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata)
        with (
            patch("sys.argv", ["render_matrix.py", "--skip-render"]),
            patch.object(
                render_matrix, "load_render_summary", side_effect=OSError("unreadable")
            ),
            patch.object(render_matrix, "render_variant") as render,
            patch.object(render_matrix, "discover_variants") as discover,
            pytest.raises(SystemExit) as error,
        ):
            render_matrix.main()
        assert error.value.code == 2
        render.assert_not_called()
        discover.assert_not_called()
        assert matrix.read_text() == original
        assert not (metadata / "module_success.json").exists()

    def test_main_renders_variants(self, temp_dir, monkeypatch):
        """Should render all discovered variants."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "test"
        variant_dir.mkdir(parents=True)
        (variant_dir / "copier-answers.yml").write_text("name: Test\n")

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        with (
            patch("sys.argv", ["render_matrix.py"]),
            patch.object(render_matrix, "render_variant") as mock_render,
        ):
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
        (metadata_dir / "render_matrix.json").write_text(
            json.dumps({"variants": [_variant_record()]})
        )

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)

        with patch(
            "sys.argv",
            [
                "render_matrix.py",
                "--skip-render",
                "--quality-artifacts",
                str(artifact_file),
                "--retention-days",
                "30",
            ],
        ):
            render_matrix.main()

        result = json.loads((metadata_dir / "render_matrix.json").read_text())
        assert "quality_runs" in result
        assert result["quality_retention_days"] == 30

    def test_main_skip_render_without_existing_does_not_render(
        self, temp_dir, monkeypatch
    ):
        """--skip-render must never fall back to rendering the full matrix."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "test"
        variant_dir.mkdir(parents=True)
        (variant_dir / "copier-answers.yml").write_text("name: Test\n")

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        with (
            patch("sys.argv", ["render_matrix.py", "--skip-render"]),
            patch.object(render_matrix, "render_variant") as mock_render,
            pytest.raises(SystemExit) as error,
        ):
            render_matrix.main()

        mock_render.assert_not_called()
        assert error.value.code == 2
        assert not metadata_dir.exists()

    def test_main_quality_only_without_render_evidence_merges_quality_artifacts(
        self, temp_dir, monkeypatch
    ):
        """Quality artifacts still land in the summary when no prior matrix exists."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "test"
        variant_dir.mkdir(parents=True)
        (variant_dir / "copier-answers.yml").write_text("name: Test\n")

        artifact_file = temp_dir / "quality-standard.json"
        artifact_file.write_text(
            json.dumps({"profile": "standard", "durations": {"ruff": 1.0}})
        )

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        with (
            patch(
                "sys.argv",
                [
                    "render_matrix.py",
                    "--quality-only",
                    "--quality-artifacts",
                    str(artifact_file),
                    "--retention-days",
                    "90",
                ],
            ),
            patch.object(render_matrix, "render_variant") as mock_render,
        ):
            render_matrix.main()

        mock_render.assert_not_called()

        result = json.loads((metadata_dir / "quality_summary.json").read_text())
        assert "variants" not in result
        assert not (metadata_dir / "render_matrix.json").exists()
        assert result["quality_runs"] == [
            {"profile": "standard", "durations": {"ruff": 1.0}}
        ]
        assert result["quality_retention_days"] == 90

    def test_main_skip_render_preserves_failed_variants_as_failure(
        self, temp_dir, monkeypatch
    ):
        """Reusing render evidence must retain its failing release-gate result."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        metadata_dir.mkdir()
        (metadata_dir / "render_matrix.json").write_text(
            json.dumps(
                {
                    "variants": [
                        _variant_record(),
                        _variant_record("saas-starter/vercel-starter", "failed", 1),
                    ]
                }
            )
        )

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)

        with (
            patch("sys.argv", ["render_matrix.py", "--skip-render"]),
            patch.object(render_matrix, "render_variant") as mock_render,
            pytest.raises(SystemExit) as error,
        ):
            render_matrix.main()

        mock_render.assert_not_called()
        assert error.value.code == 1

        result = json.loads((metadata_dir / "render_matrix.json").read_text())
        assert [v["variant"] for v in result["variants"]] == [
            "default",
            "saas-starter/vercel-starter",
        ]

    def test_main_exits_nonzero_on_failed_render(self, temp_dir, monkeypatch):
        """The live render path still fails the job when a variant fails."""
        from unittest.mock import patch
        import render_matrix

        metadata_dir = temp_dir / "metadata"
        samples_dir = temp_dir / "samples"
        variant_dir = samples_dir / "test"
        variant_dir.mkdir(parents=True)
        (variant_dir / "copier-answers.yml").write_text("name: Test\n")

        monkeypatch.setattr(render_matrix, "METADATA_DIR", metadata_dir)
        monkeypatch.setattr(render_matrix, "SAMPLES_DIR", samples_dir)

        with (
            patch("sys.argv", ["render_matrix.py"]),
            patch.object(render_matrix, "render_variant") as mock_render,
        ):
            mock_render.return_value = {
                "variant": "test",
                "answers": str(variant_dir / "copier-answers.yml"),
                "destination": str(variant_dir / "render"),
                "smoke_results": None,
                "workflow_validation": "unknown",
                "container_status": "not_applicable",
                "render_status": "failed",
                "render_returncode": 1,
            }

            with pytest.raises(SystemExit) as excinfo:
                render_matrix.main()

        assert excinfo.value.code == 1
        mock_render.assert_called_once()
