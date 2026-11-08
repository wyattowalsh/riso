"""Integration checks for rendered pre-commit layout (DG-1 Option A)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[2]
CHANGELOG_RENDER = REPO_ROOT / "samples" / "changelog-python" / "render"


@pytest.fixture(name="changelog_render")
def _changelog_render() -> Path:
    """Require an existing changelog render without regenerating official samples."""
    if not CHANGELOG_RENDER.is_dir():
        pytest.skip("changelog-python render missing; run ./scripts/render-samples.sh")
    return CHANGELOG_RENDER


class TestRenderedPrecommitLayout:
    """Validate pre-commit artifacts in a rendered Python sample."""

    def test_root_precommit_config_exists(self, changelog_render: Path) -> None:
        """The rendered project ships a valid pre-commit repository configuration."""
        config_path = changelog_render / ".pre-commit-config.yaml"
        assert config_path.exists()
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert isinstance(config, dict)
        assert "repos" in config

    def test_no_legacy_root_pyproject_stub(self, changelog_render: Path) -> None:
        """Python configuration lives in its package without the former task stub."""
        root_pyproject = changelog_render / "pyproject.toml"
        python_pyproject = changelog_render / "python" / "pyproject.toml"
        assert python_pyproject.exists()
        if root_pyproject.exists():
            content = root_pyproject.read_text(encoding="utf-8")
            assert "[project]" in content or "[tool.uv.tasks]" not in content

    def test_root_task_runner_delegates_hooks(self, changelog_render: Path) -> None:
        """The root task runner delegates hook execution to its quality include."""
        justfile = changelog_render / "justfile"
        makefile = changelog_render / "Makefile"
        if justfile.exists():
            content = justfile.read_text(encoding="utf-8")
            assert "quality/justfile.quality" in content
            quality_content = (
                changelog_render / "quality" / "justfile.quality"
            ).read_text(encoding="utf-8")
            assert "hooks" in quality_content
        elif makefile.exists():
            content = makefile.read_text(encoding="utf-8")
            assert "quality/makefile.quality" in content
            quality_content = (
                changelog_render / "quality" / "makefile.quality"
            ).read_text(encoding="utf-8")
            assert "hooks" in quality_content
        else:
            pytest.fail("expected justfile or Makefile at project root")

    def test_post_gen_metadata_hooks_install(self, changelog_render: Path) -> None:
        """Post-gen metadata records hook installation and commit-message coverage."""
        metadata_path = changelog_render / ".riso" / "post_gen_metadata.json"
        assert metadata_path.exists()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        pre_commit = metadata["pre_commit"]
        install_cmd = pre_commit["install_command"]
        assert install_cmd in {"just hooks", "make hooks"}
        assert "commit-msg" in pre_commit["hooks"]

    def test_render_precommit_script_passes_changelog(self) -> None:
        """The maintainer validator accepts the existing changelog hook layout."""
        if not CHANGELOG_RENDER.is_dir():
            pytest.skip(
                "changelog-python render missing; run ./scripts/render-samples.sh"
            )

        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "scripts/ci/render_precommit_configs.py",
                "--variants",
                "changelog-python",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr or result.stdout
