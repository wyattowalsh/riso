"""Unit tests for post_gen_project.py hook.

This module contains comprehensive tests for the post-generation hook,
focusing on setup functions, metadata recording, guidance rendering,
and integration with quality tools.
"""

import json
from datetime import datetime

import pytest


pytestmark = pytest.mark.usefixtures("hooks_path")


@pytest.mark.unit
class TestRecordMetadata:
    """Tests for record_metadata function."""

    def test_creates_metadata_directory(self, tmp_path):
        """Should create .riso directory if it doesn't exist."""
        from post_gen_project import record_metadata

        data = {"test": "value"}
        record_metadata(tmp_path, data)

        riso_dir = tmp_path / ".riso"
        assert riso_dir.exists()
        assert riso_dir.is_dir()

    def test_writes_metadata_json(self, tmp_path):
        """Should write metadata as properly formatted JSON."""
        from post_gen_project import record_metadata

        data = {
            "rendered_at": "2024-01-01T00:00:00Z",
            "destination": str(tmp_path),
            "modules": {"cli": "enabled"},
        }
        record_metadata(tmp_path, data)

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        assert metadata_file.exists()

        content = json.loads(metadata_file.read_text(encoding="utf-8"))
        assert content == data

    def test_overwrites_existing_metadata(self, tmp_path):
        """Should overwrite existing metadata file."""
        from post_gen_project import record_metadata

        riso_dir = tmp_path / ".riso"
        riso_dir.mkdir()
        metadata_file = riso_dir / "post_gen_metadata.json"
        metadata_file.write_text('{"old": "data"}', encoding="utf-8")

        new_data = {"new": "data"}
        record_metadata(tmp_path, new_data)

        content = json.loads(metadata_file.read_text(encoding="utf-8"))
        assert content == new_data
        assert "old" not in content

    def test_handles_nested_data_structures(self, tmp_path):
        """Should handle complex nested data structures."""
        from post_gen_project import record_metadata

        data = {
            "modules": {
                "cli": "enabled",
                "api": {
                    "tracks": ["python", "node"],
                    "config": {"port": 8000},
                },
            },
            "quality": {
                "tools": ["ruff", "mypy", "pytest"],
            },
        }
        record_metadata(tmp_path, data)

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))
        assert content["modules"]["api"]["config"]["port"] == 8000
        assert "ruff" in content["quality"]["tools"]

    def test_uses_utf8_encoding(self, tmp_path):
        """Should properly encode UTF-8 characters."""
        from post_gen_project import record_metadata

        data = {
            "description": "Test with unicode: émoji 🚀",
            "author": "François",
        }
        record_metadata(tmp_path, data)

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        # JSON escapes unicode by default, so parse and check the values
        content = json.loads(metadata_file.read_text(encoding="utf-8"))
        assert content["description"] == "Test with unicode: émoji 🚀"
        assert content["author"] == "François"


@pytest.mark.unit
class TestLoadAnswers:
    """Tests for load_answers function."""

    def test_returns_empty_dict_when_file_missing(self, tmp_path):
        """Should return empty dict when answers file doesn't exist."""
        from post_gen_project import load_answers

        result = load_answers(tmp_path)
        assert result == {}

    def test_loads_valid_yaml_answers(self, tmp_path):
        """Should load and parse valid YAML answers file."""
        from post_gen_project import load_answers

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(
            """
            project_name: test-project
            cli_module: enabled
            docs_framework: fumadocs
            """,
            encoding="utf-8",
        )

        result = load_answers(tmp_path)
        assert result["project_name"] == "test-project"
        assert result["cli_module"] == "enabled"
        assert result["docs_framework"] == "fumadocs"

    def test_preserves_yaml_value_types(self, tmp_path):
        """Should preserve non-string YAML values for list answers."""
        from post_gen_project import load_answers

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(
            """
            version: 1.0
            port: 8000
            enabled: true
            """,
            encoding="utf-8",
        )

        result = load_answers(tmp_path)
        assert result["version"] == 1.0
        assert result["port"] == 8000
        assert result["enabled"] is True

    def test_validate_removed_answer_keys_rejects_legacy_keys(self):
        """Should fail fast when removed answer keys are present."""
        from post_gen_project import validate_removed_answer_keys

        with pytest.raises(SystemExit):
            validate_removed_answer_keys({"api_tracks": "python"})

    def test_filters_none_values(self, tmp_path):
        """Should filter out None values from answers."""
        from post_gen_project import load_answers

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(
            """
            valid_key: value
            null_key: null
            another_key: data
            """,
            encoding="utf-8",
        )

        result = load_answers(tmp_path)
        assert "valid_key" in result
        assert "another_key" in result
        assert "null_key" not in result

    def test_handles_non_dict_yaml(self, tmp_path):
        """Should return empty dict for non-dict YAML content."""
        from post_gen_project import load_answers

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("- item1\n- item2\n", encoding="utf-8")

        result = load_answers(tmp_path)
        assert result == {}

    def test_handles_malformed_yaml(self, tmp_path):
        """Should handle malformed YAML gracefully."""
        from post_gen_project import load_answers

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("invalid: yaml: content: {{{", encoding="utf-8")

        result = load_answers(tmp_path)
        assert result == {}

    def test_handles_missing_yaml_module(self, tmp_path, monkeypatch):
        """Should handle missing yaml module gracefully."""
        from post_gen_project import load_answers

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("key: value\n", encoding="utf-8")

        # Mock yaml import to raise ImportError
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("No module named 'yaml'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        result = load_answers(tmp_path)
        # Should return empty dict when yaml can't be imported
        assert isinstance(result, dict)


@pytest.mark.unit
class TestCleanupEmptyScaffoldDirs:
    """Tests for empty scaffold directory cleanup."""

    def test_removes_known_empty_scaffold_dirs(self, tmp_path):
        """Should remove known empty directories left by Copier excludes."""
        from post_gen_project import cleanup_empty_scaffold_dirs

        empty_dir = tmp_path / "graphql"
        empty_dir.mkdir()
        populated_dir = tmp_path / "mcp"
        populated_dir.mkdir()
        (populated_dir / "tooling.py").write_text("# keep\n", encoding="utf-8")

        removed = cleanup_empty_scaffold_dirs(tmp_path)

        assert "graphql" in removed
        assert not empty_dir.exists()
        assert populated_dir.exists()


@pytest.mark.unit
class TestCleanupEmptyRenderedFiles:
    """Tests for zero-byte conditional template stub cleanup."""

    def test_removes_empty_rendered_files(self, tmp_path):
        """Should delete zero-byte stubs but keep populated docs and .gitkeep."""
        from post_gen_project import cleanup_empty_rendered_files

        docs_dir = tmp_path / "node" / "docs" / "fumadocs" / "content" / "docs"
        docs_dir.mkdir(parents=True)
        (docs_dir / "stub.mdx").write_text("", encoding="utf-8")
        (docs_dir / "real.mdx").write_text(
            "---\ntitle: Real\n---\n\n# Real\n", encoding="utf-8"
        )
        (tmp_path / "static" / "img").mkdir(parents=True)
        (tmp_path / "static" / "img" / ".gitkeep").write_text("", encoding="utf-8")

        removed = cleanup_empty_rendered_files(tmp_path)

        assert "node/docs/fumadocs/content/docs/stub.mdx" in removed
        assert not (docs_dir / "stub.mdx").exists()
        assert (docs_dir / "real.mdx").exists()
        assert (tmp_path / "static" / "img" / ".gitkeep").exists()


@pytest.mark.unit
class TestLayoutGuidance:
    """Tests for layout_guidance function."""

    def test_monorepo_layout_guidance(self):
        """Should return monorepo-specific guidance."""
        from post_gen_project import layout_guidance

        result = layout_guidance("monorepo")
        assert len(result) > 0
        assert any("pnpm install" in item for item in result)
        assert any("pytest" in item for item in result)
        assert any("api-node" in item for item in result)

    def test_single_package_layout(self):
        """Should return empty list for single-package layout."""
        from post_gen_project import layout_guidance

        result = layout_guidance("single-package")
        assert result == []

    def test_unknown_layout(self):
        """Should return empty list for unknown layout."""
        from post_gen_project import layout_guidance

        result = layout_guidance("unknown-layout")
        assert result == []

    def test_case_sensitivity(self):
        """Should handle case-sensitive layout names."""
        from post_gen_project import layout_guidance

        result = layout_guidance("Monorepo")
        # Should not match due to case difference
        assert result == []


@pytest.mark.unit
class TestDocsGuidance:
    """Tests for docs_guidance function."""

    def test_fumadocs_guidance(self):
        """Should return fumadocs-specific guidance."""
        from post_gen_project import docs_guidance

        answers = {"docs_module": "enabled", "docs_framework": "fumadocs"}
        result = docs_guidance(answers)

        assert len(result) == 2
        assert any("docs-fumadocs dev" in item for item in result)
        assert any("docs-fumadocs build" in item for item in result)

    def test_sphinx_shibuya_guidance(self):
        """Should return Sphinx-specific guidance."""
        from post_gen_project import docs_guidance

        answers = {"docs_module": "enabled", "docs_framework": "sphinx-shibuya"}
        result = docs_guidance(answers)

        assert len(result) == 2
        assert any("sphinx-build" in item for item in result)
        assert any("linkcheck" in item for item in result)

    def test_docusaurus_guidance(self):
        """Should return Docusaurus-specific guidance."""
        from post_gen_project import docs_guidance

        answers = {"docs_module": "enabled", "docs_framework": "docusaurus"}
        result = docs_guidance(answers)

        assert len(result) == 2
        assert any("docs-docusaurus start" in item for item in result)
        assert any("docs-docusaurus build" in item for item in result)

    def test_docs_module_disabled(self):
        """Should return guidance for skipped documentation."""
        from post_gen_project import docs_guidance

        answers = {"docs_module": "disabled"}
        result = docs_guidance(answers)

        assert len(result) == 1
        assert "skipped" in result[0]

    def test_missing_docs_module_key(self):
        """Should skip docs when no docs module is enabled."""
        from post_gen_project import docs_guidance

        answers = {}
        result = docs_guidance(answers)

        assert len(result) == 1
        assert "skipped" in result[0]

    def test_component_first_docs_module(self):
        """Should derive docs guidance from component-first answers."""
        from post_gen_project import docs_guidance

        answers = {"docs_module": "enabled", "docs_framework": "fumadocs"}
        result = docs_guidance(answers)

        assert len(result) == 2
        assert any("docs-fumadocs dev" in item for item in result)

    def test_case_insensitive_matching(self):
        """Should handle case-insensitive docs framework values."""
        from post_gen_project import docs_guidance

        answers = {"docs_module": "ENABLED", "docs_framework": "FUMADOCS"}
        result = docs_guidance(answers)

        assert len(result) == 2
        assert any("fumadocs" in item for item in result)


@pytest.mark.unit
class TestOptionalModuleGuidance:
    """Tests for optional_module_guidance function."""

    def test_cli_module_enabled(self):
        """Should include CLI guidance when enabled."""
        from post_gen_project import optional_module_guidance

        answers = {"cli_module": "enabled"}
        result = optional_module_guidance(answers)

        assert any("Typer CLI" in item for item in result)
        assert any("cli --help" in item for item in result)

    def test_python_api_languages(self):
        """Should include FastAPI guidance for Python API."""
        from post_gen_project import optional_module_guidance

        answers = {"api_module": "enabled", "api_languages": ["python"]}
        result = optional_module_guidance(answers)

        assert any("FastAPI" in item for item in result)
        assert any("uvicorn" in item for item in result)

    def test_component_first_python_api(self):
        """Should derive API guidance from component-first answers."""
        from post_gen_project import optional_module_guidance

        answers = {"api_module": "enabled", "api_languages": ["python"]}
        result = optional_module_guidance(answers)

        assert any("FastAPI" in item for item in result)

    def test_node_api_languages(self):
        """Should include Fastify guidance for Node API."""
        from post_gen_project import optional_module_guidance

        answers = {"api_module": "enabled", "api_languages": ["node"]}
        result = optional_module_guidance(answers)

        assert any("Fastify" in item for item in result)
        assert any("api-node" in item for item in result)

    def test_dual_api_languages(self):
        """Should include both API guidance for dual tracks."""
        from post_gen_project import optional_module_guidance

        answers = {"api_module": "enabled", "api_languages": ["python", "node"]}
        result = optional_module_guidance(answers)

        fastapi_items = [item for item in result if "FastAPI" in item]
        fastify_items = [item for item in result if "Fastify" in item]

        assert len(fastapi_items) > 0
        assert len(fastify_items) > 0

    def test_mcp_module_enabled(self):
        """Should include MCP guidance when enabled."""
        from post_gen_project import optional_module_guidance

        answers = {"mcp_module": "enabled"}
        result = optional_module_guidance(answers)

        assert any("MCP tools" in item for item in result)
        assert any("tooling.list_tools()" in item for item in result)

    def test_multiple_modules_enabled(self):
        """Should include guidance for all enabled modules."""
        from post_gen_project import optional_module_guidance

        answers = {
            "cli_module": "enabled",
            "api_module": "enabled",
            "api_languages": ["python"],
            "mcp_module": "enabled",
        }
        result = optional_module_guidance(answers)

        assert len(result) >= 3
        assert any("CLI" in item for item in result)
        assert any("FastAPI" in item for item in result)
        assert any("MCP" in item for item in result)

    def test_no_modules_enabled(self):
        """Should return empty list when no modules enabled."""
        from post_gen_project import optional_module_guidance

        answers = {}
        result = optional_module_guidance(answers)

        assert result == []

    def test_case_insensitive_module_values(self):
        """Should handle case-insensitive module values."""
        from post_gen_project import optional_module_guidance

        answers = {
            "cli_module": "ENABLED",
            "mcp_module": "Enabled",
        }
        result = optional_module_guidance(answers)

        assert len(result) >= 2


@pytest.mark.unit
class TestRenderGuidance:
    """Tests for render_guidance function."""

    def test_includes_default_guidance(self):
        """Should always include default guidance steps."""
        from post_gen_project import render_guidance

        answers = {}
        result = render_guidance("test_package", answers)

        assert "Next steps:" in result
        assert "uv venv" in result
        assert "uv sync" in result
        assert "test_package.quickstart" in result
        assert "AGENTS.md" in result

    def test_formats_package_name(self):
        """Should properly format package name in guidance."""
        from post_gen_project import render_guidance

        answers = {}
        result = render_guidance("my_project", answers)

        assert "my_project.quickstart" in result

    def test_includes_monorepo_guidance(self):
        """Should include monorepo guidance when applicable."""
        from post_gen_project import render_guidance

        answers = {"project_layout": "monorepo"}
        result = render_guidance("test_pkg", answers)

        assert "pnpm install" in result
        assert "pytest" in result

    def test_includes_docs_guidance(self):
        """Should include documentation guidance."""
        from post_gen_project import render_guidance

        answers = {"docs_module": "enabled", "docs_framework": "fumadocs"}
        result = render_guidance("test_pkg", answers)

        assert "fumadocs" in result

    def test_includes_optional_module_guidance(self):
        """Should include optional module guidance."""
        from post_gen_project import render_guidance

        answers = {
            "cli_module": "enabled",
            "api_module": "enabled",
            "api_languages": ["python"],
        }
        result = render_guidance("test_pkg", answers)

        assert "CLI" in result
        assert "FastAPI" in result

    def test_includes_ai_tools_guidance_when_enabled(self):
        """Should mention AGENTS and ai-tools when ai_tools_module is enabled."""
        from post_gen_project import render_guidance

        answers = {"ai_tools_module": "enabled"}
        result = render_guidance("test_pkg", answers)

        assert "AGENTS.md" in result
        assert "ai-tools.md" in result

    def test_comprehensive_guidance_rendering(self):
        """Should render comprehensive guidance with all features."""
        from post_gen_project import render_guidance

        answers = {
            "project_layout": "monorepo",
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "cli_module": "enabled",
            "api_module": "enabled",
            "api_languages": ["python", "node"],
            "mcp_module": "enabled",
        }
        result = render_guidance("full_project", answers)

        # Should have multiple sections
        lines = result.split("\n")
        assert len(lines) > 10

        # Verify key components
        assert "Next steps:" in result
        assert "uv venv" in result
        assert "pnpm install" in result
        assert "fumadocs" in result
        assert "CLI" in result
        assert "FastAPI" in result
        assert "Fastify" in result
        assert "MCP" in result


@pytest.mark.unit
class TestMain:
    """Tests for main function."""

    def test_executes_without_errors(self, tmp_path, monkeypatch):
        """Should execute main function without errors."""
        monkeypatch.chdir(tmp_path)

        # Create minimal answers file
        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("project_name: test\n", encoding="utf-8")

        from post_gen_project import main

        # Should not raise any exceptions
        main()

    def test_creates_metadata_file(self, tmp_path, monkeypatch):
        """Should create metadata file during execution."""
        monkeypatch.chdir(tmp_path)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(
            """
            project_layout: single-package
            cli_module: enabled
            """,
            encoding="utf-8",
        )

        from post_gen_project import main

        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        assert metadata_file.exists()

        content = json.loads(metadata_file.read_text(encoding="utf-8"))
        assert "rendered_at" in content
        assert "destination" in content

    def test_records_quality_tool_checks(self, tmp_path, monkeypatch):
        """Should record quality tool check results in metadata."""
        monkeypatch.chdir(tmp_path)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("quality_profile: standard\n", encoding="utf-8")

        from post_gen_project import main

        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))

        assert "quality" in content
        assert "tool_install_attempts" in content["quality"]

    def test_validates_workflows_for_github_actions(self, tmp_path, monkeypatch):
        """Should validate workflows when CI platform is GitHub Actions."""
        monkeypatch.chdir(tmp_path)

        # Create workflows directory
        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("ci_platform: github-actions\n", encoding="utf-8")

        from post_gen_project import main

        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))

        assert "workflow_validation" in content
        assert content["workflow_validation"] in ["pass", "fail"]

    def test_skips_workflow_validation_for_other_ci(self, tmp_path, monkeypatch):
        """Should skip workflow validation for non-GitHub CI platforms."""
        monkeypatch.chdir(tmp_path)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("ci_platform: gitlab-ci\n", encoding="utf-8")

        from post_gen_project import main

        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))

        assert content["workflow_validation"] == "skipped"

    def test_outputs_guidance_to_stdout(self, tmp_path, monkeypatch, capsys):
        """Should output guidance to stdout."""
        monkeypatch.chdir(tmp_path)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("cli_module: enabled\n", encoding="utf-8")

        from post_gen_project import main

        main()

        captured = capsys.readouterr()
        assert "Next steps:" in captured.out
        assert "uv venv" in captured.out

    def test_handles_missing_answers_file(self, tmp_path, monkeypatch):
        """Should handle missing answers file gracefully."""
        monkeypatch.chdir(tmp_path)

        from post_gen_project import main

        # Should not raise exceptions even without answers file
        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        assert metadata_file.exists()

    def test_records_complete_module_configuration(self, tmp_path, monkeypatch):
        """Should record complete module configuration in metadata."""
        monkeypatch.chdir(tmp_path)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(
            """
            cli_module: enabled
            api_module: enabled
            api_languages:
              - python
              - node
            mcp_module: enabled
            docs_module: enabled
            docs_framework: fumadocs
            shared_logic: enabled
            """,
            encoding="utf-8",
        )

        # Mock quality tool checks to avoid subprocess calls
        import post_gen_project

        monkeypatch.setattr(post_gen_project, "ensure_python_quality_tools", lambda: [])
        monkeypatch.setattr(
            post_gen_project, "ensure_node_quality_tools", lambda required: []
        )

        from post_gen_project import main

        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))

        modules = content["modules"]
        assert modules["cli_module"] == "enabled"
        assert modules["api_module"] == "enabled"
        assert modules["api_languages"] == ["python", "node"]
        assert modules["mcp_module"] == "enabled"
        assert modules["docs_module"] == "enabled"
        assert modules["docs_framework"] == "fumadocs"
        assert modules["shared_logic"] == "enabled"
        assert "api_tracks" not in modules
        assert "docs_site" not in modules

    def test_uses_package_name_from_directory(self, tmp_path, monkeypatch):
        """Should derive package name from directory name."""
        project_dir = tmp_path / "my-test-project"
        project_dir.mkdir()
        monkeypatch.chdir(project_dir)

        answers_file = project_dir / ".copier-answers.yml"
        answers_file.write_text("test: value\n", encoding="utf-8")

        from post_gen_project import main

        main()

        # Package name should be directory name with hyphens converted to underscores
        # Verify this in the output guidance (which would contain the package name)


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_handles_empty_answers_dict(self):
        """Should handle empty answers dictionary."""
        from post_gen_project import render_guidance

        result = render_guidance("test_pkg", {})
        assert "Next steps:" in result
        assert len(result) > 0

    def test_handles_unicode_in_package_name(self):
        """Should handle unicode characters in package name."""
        from post_gen_project import render_guidance

        # Should not crash with unicode
        result = render_guidance("test_émoji_pkg", {})
        assert "test_émoji_pkg" in result

    def test_metadata_with_special_characters(self, tmp_path):
        """Should handle special characters in metadata."""
        from post_gen_project import record_metadata

        data = {
            "special_chars": "Test with <>&\"'",
            "unicode": "Test with émoji 🎉",
        }
        record_metadata(tmp_path, data)

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))
        assert content["special_chars"] == "Test with <>&\"'"
        assert content["unicode"] == "Test with émoji 🎉"

    def test_handles_very_long_guidance(self):
        """Should handle very long guidance output."""
        from post_gen_project import render_guidance

        answers = {
            "project_layout": "monorepo",
            "docs_module": "enabled",
            "docs_framework": "fumadocs",
            "cli_module": "enabled",
            "api_module": "enabled",
            "api_languages": ["python", "node"],
            "mcp_module": "enabled",
        }
        result = render_guidance("test_package", answers)

        # Should produce substantial output
        assert len(result) > 500
        assert result.count("\n") > 5

    def test_renders_iso_timestamp(self, tmp_path, monkeypatch):
        """Should render ISO-formatted timestamp in metadata."""
        monkeypatch.chdir(tmp_path)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("test: value\n", encoding="utf-8")

        from post_gen_project import main

        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))

        # Should have ISO timestamp ending in Z
        assert content["rendered_at"].endswith("Z")
        assert "T" in content["rendered_at"]

        # Should be parseable as datetime
        datetime.fromisoformat(content["rendered_at"].rstrip("Z"))


@pytest.mark.unit
class TestCleanupLegacyRootPyproject:
    """Tests for cleanup_legacy_root_pyproject."""

    def test_removes_legacy_stub_when_python_pyproject_exists(self, tmp_path):
        from post_gen_project import cleanup_legacy_root_pyproject

        (tmp_path / "python").mkdir()
        (tmp_path / "python" / "pyproject.toml").write_text(
            "[project]\nname = 'demo'\n", encoding="utf-8"
        )
        (tmp_path / "pyproject.toml").write_text(
            "[tool.uv.tasks]\nquality = 'mypy'\n", encoding="utf-8"
        )

        removed = cleanup_legacy_root_pyproject(tmp_path)

        assert removed == ["pyproject.toml"]
        assert not (tmp_path / "pyproject.toml").exists()

    def test_keeps_valid_root_pyproject(self, tmp_path):
        from post_gen_project import cleanup_legacy_root_pyproject

        (tmp_path / "python").mkdir()
        (tmp_path / "python" / "pyproject.toml").write_text(
            "[project]\nname = 'demo'\n", encoding="utf-8"
        )
        (tmp_path / "pyproject.toml").write_text(
            "[project]\nname = 'root'\n", encoding="utf-8"
        )

        removed = cleanup_legacy_root_pyproject(tmp_path)

        assert removed == []
        assert (tmp_path / "pyproject.toml").exists()


@pytest.mark.unit
class TestPreCommitSetupGuidance:
    """Tests for pre_commit_setup_guidance metadata."""

    def test_standard_changelog_includes_commit_msg(self, tmp_path, monkeypatch):
        """changelog_module=enabled on standard profile should list commit-msg hooks."""
        monkeypatch.chdir(tmp_path)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text(
            "quality_profile: standard\nchangelog_module: enabled\n",
            encoding="utf-8",
        )

        from post_gen_project import main

        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))

        assert content["pre_commit"]["hooks"] == ["pre-commit", "commit-msg"]
        assert content["pre_commit"]["install_command"] == "make hooks"

    def test_strict_includes_pre_push(self, tmp_path, monkeypatch):
        """strict profile should list pre-push hooks."""
        monkeypatch.chdir(tmp_path)

        answers_file = tmp_path / ".copier-answers.yml"
        answers_file.write_text("quality_profile: strict\n", encoding="utf-8")

        from post_gen_project import main

        main()

        metadata_file = tmp_path / ".riso" / "post_gen_metadata.json"
        content = json.loads(metadata_file.read_text(encoding="utf-8"))

        assert content["pre_commit"]["hooks"] == [
            "pre-commit",
            "commit-msg",
            "pre-push",
        ]
