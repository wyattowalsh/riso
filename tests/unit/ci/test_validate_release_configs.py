"""Unit tests for validate_release_configs.py"""
import sys
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parents[3] / "scripts" / "ci"))


class TestValidateCommitlintConfig:
    """Tests for commitlint configuration validation."""

    def test_valid_config_passes(self, temp_dir):
        """Valid commitlint config should pass validation."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("""
extends:
  - "@commitlint/config-conventional"
rules:
  type-enum:
    - 2
    - always
    - [feat, fix, docs, style, refactor, test, chore]
""")
        from validate_release_configs import validate_commitlint_config

        valid, errors = validate_commitlint_config(config)
        assert valid is True
        assert len(errors) == 0

    def test_missing_file_returns_true(self, temp_dir):
        """Missing config file should return True (not an error)."""
        config = temp_dir / ".commitlintrc.yml"
        from validate_release_configs import validate_commitlint_config

        valid, errors = validate_commitlint_config(config)
        assert valid is True
        assert len(errors) == 0

    def test_missing_extends_fails(self, temp_dir):
        """Missing extends field should fail."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("""
rules:
  type-enum:
    - 2
    - always
    - [feat, fix]
""")
        from validate_release_configs import validate_commitlint_config

        valid, errors = validate_commitlint_config(config)
        assert valid is False
        assert any("extends" in e.lower() for e in errors)

    def test_missing_rules_fails(self, temp_dir):
        """Missing rules field should fail."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("""
extends:
  - "@commitlint/config-conventional"
""")
        from validate_release_configs import validate_commitlint_config

        valid, errors = validate_commitlint_config(config)
        assert valid is False
        assert any("rules" in e.lower() for e in errors)

    def test_missing_type_enum_fails(self, temp_dir):
        """Missing type-enum rule should fail."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("""
extends:
  - "@commitlint/config-conventional"
rules:
  subject-case:
    - 2
    - always
    - lower-case
""")
        from validate_release_configs import validate_commitlint_config

        valid, errors = validate_commitlint_config(config)
        assert valid is False
        assert any("type-enum" in e.lower() for e in errors)

    def test_invalid_type_enum_format_fails(self, temp_dir):
        """Invalid type-enum format should fail."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("""
extends:
  - "@commitlint/config-conventional"
rules:
  type-enum: invalid
""")
        from validate_release_configs import validate_commitlint_config

        valid, errors = validate_commitlint_config(config)
        assert valid is False
        assert any("type-enum" in e.lower() for e in errors)

    def test_invalid_yaml_fails(self, temp_dir):
        """Invalid YAML should fail with parsing error."""
        config = temp_dir / ".commitlintrc.yml"
        config.write_text("""
extends:
  - "@commitlint/config-conventional
rules:
  type-enum: [1, 2, 3
""")
        from validate_release_configs import validate_commitlint_config

        valid, errors = validate_commitlint_config(config)
        assert valid is False
        assert any("yaml" in e.lower() or "parsing" in e.lower() for e in errors)


class TestValidateSemanticReleaseConfig:
    """Tests for .releaserc.yml validation."""

    def test_valid_config_passes(self, temp_dir):
        """Valid releaserc config should pass."""
        config = temp_dir / ".releaserc.yml"
        config.write_text("""
branches:
  - main
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - "@semantic-release/changelog"
  - "@semantic-release/github"
""")
        from validate_release_configs import validate_semantic_release_config

        valid, errors = validate_semantic_release_config(config)
        assert valid is True
        assert len(errors) == 0

    def test_missing_file_returns_true(self, temp_dir):
        """Missing config file should return True (not an error)."""
        config = temp_dir / ".releaserc.yml"
        from validate_release_configs import validate_semantic_release_config

        valid, errors = validate_semantic_release_config(config)
        assert valid is True
        assert len(errors) == 0

    def test_missing_branches_fails(self, temp_dir):
        """Missing branches field should fail."""
        config = temp_dir / ".releaserc.yml"
        config.write_text("""
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - "@semantic-release/changelog"
""")
        from validate_release_configs import validate_semantic_release_config

        valid, errors = validate_semantic_release_config(config)
        assert valid is False
        assert any("branches" in e.lower() for e in errors)

    def test_missing_plugins_fails(self, temp_dir):
        """Missing plugins field should fail."""
        config = temp_dir / ".releaserc.yml"
        config.write_text("""
branches:
  - main
""")
        from validate_release_configs import validate_semantic_release_config

        valid, errors = validate_semantic_release_config(config)
        assert valid is False
        assert any("plugins" in e.lower() for e in errors)

    def test_missing_required_plugin_fails(self, temp_dir):
        """Missing required plugin should fail."""
        config = temp_dir / ".releaserc.yml"
        config.write_text("""
branches:
  - main
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/github"
""")
        from validate_release_configs import validate_semantic_release_config

        valid, errors = validate_semantic_release_config(config)
        assert valid is False
        assert any("changelog" in e.lower() or "release-notes" in e.lower() for e in errors)

    def test_plugins_with_config_passes(self, temp_dir):
        """Plugins with configuration objects should pass."""
        config = temp_dir / ".releaserc.yml"
        config.write_text("""
branches:
  - main
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - ["@semantic-release/changelog", {"changelogFile": "CHANGELOG.md"}]
  - "@semantic-release/github"
""")
        from validate_release_configs import validate_semantic_release_config

        valid, errors = validate_semantic_release_config(config)
        assert valid is True
        assert len(errors) == 0

    def test_invalid_yaml_fails(self, temp_dir):
        """Invalid YAML should fail with parsing error."""
        config = temp_dir / ".releaserc.yml"
        config.write_text("""
branches:
  - main
plugins: [invalid yaml
""")
        from validate_release_configs import validate_semantic_release_config

        valid, errors = validate_semantic_release_config(config)
        assert valid is False
        assert any("yaml" in e.lower() or "parsing" in e.lower() for e in errors)


class TestValidateReleaseWorkflow:
    """Tests for release workflow validation."""

    def test_valid_workflow_passes(self, temp_dir):
        """Valid release workflow should pass."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
'on':
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run semantic-release
        run: npx semantic-release
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is True
        assert len(errors) == 0

    def test_missing_workflow_returns_true(self, temp_dir):
        """Missing workflow should return True (not an error)."""
        workflow = temp_dir / "riso-release.yml"
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is True
        assert len(errors) == 0

    def test_missing_name_fails(self, temp_dir):
        """Missing name field should fail."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
'on':
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is False
        assert any("name" in e.lower() for e in errors)

    def test_missing_on_fails(self, temp_dir):
        """Missing on field should fail."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is False
        assert any("'on'" in e.lower() or "on" in e for e in errors)

    def test_missing_jobs_fails(self, temp_dir):
        """Missing jobs field should fail."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
'on':
  push:
    branches: [main]
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is False
        assert any("jobs" in e.lower() for e in errors)

    def test_missing_release_job_fails(self, temp_dir):
        """Missing release job should fail."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
'on':
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is False
        assert any("release" in e.lower() and "job" in e.lower() for e in errors)

    def test_missing_runs_on_fails(self, temp_dir):
        """Missing runs-on in release job should fail."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
'on':
  push:
    branches: [main]
jobs:
  release:
    steps:
      - uses: actions/checkout@v4
      - name: Run semantic-release
        run: npx semantic-release
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is False
        assert any("runs-on" in e.lower() for e in errors)

    def test_missing_steps_fails(self, temp_dir):
        """Missing steps in release job should fail."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
'on':
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is False
        assert any("steps" in e.lower() for e in errors)

    def test_missing_semantic_release_step_fails(self, temp_dir):
        """Missing semantic-release step should fail."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
'on':
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build project
        run: npm run build
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is False
        assert any("semantic-release" in e.lower() for e in errors)

    def test_invalid_yaml_fails(self, temp_dir):
        """Invalid YAML should fail with parsing error."""
        workflow = temp_dir / "riso-release.yml"
        workflow.write_text("""
name: Release
'on':
  push:
    branches: [main
jobs: invalid yaml
""")
        from validate_release_configs import validate_release_workflow

        valid, errors = validate_release_workflow(workflow)
        assert valid is False
        assert any("yaml" in e.lower() or "parsing" in e.lower() for e in errors)
