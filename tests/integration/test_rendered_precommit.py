"""Integration checks for rendered pre-commit layout (DG-1 Option A)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[2]
CHANGELOG_RENDER = REPO_ROOT / "samples" / "changelog-python" / "render"


@pytest.fixture
def changelog_render() -> Path:
    if not CHANGELOG_RENDER.is_dir():
        pytest.skip("changelog-python render missing; run ./scripts/render-samples.sh")
    return CHANGELOG_RENDER


class TestRenderedPrecommitLayout:
    """Validate pre-commit artifacts in a rendered Python sample."""

    def test_root_precommit_config_exists(self, changelog_render: Path) -> None:
        config_path = changelog_render / ".pre-commit-config.yaml"
        assert config_path.exists()
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert isinstance(config, dict)
        assert "repos" in config

    def test_no_legacy_root_pyproject_stub(self, changelog_render: Path) -> None:
        root_pyproject = changelog_render / "pyproject.toml"
        python_pyproject = changelog_render / "python" / "pyproject.toml"
        assert python_pyproject.exists()
        if root_pyproject.exists():
            content = root_pyproject.read_text(encoding="utf-8")
            assert "[project]" in content or "[tool.uv.tasks]" not in content

    def test_root_makefile_delegates_hooks(self, changelog_render: Path) -> None:
        makefile = changelog_render / "Makefile"
        assert makefile.exists()
        content = makefile.read_text(encoding="utf-8")
        assert "quality/makefile.quality" in content
        assert "hooks" in content

    def test_post_gen_metadata_hooks_install(self, changelog_render: Path) -> None:
        metadata_path = changelog_render / ".riso" / "post_gen_metadata.json"
        assert metadata_path.exists()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        pre_commit = metadata["pre_commit"]
        assert pre_commit["install_command"] == "make hooks"
        assert "commit-msg" in pre_commit["hooks"]

    def test_render_precommit_script_passes_changelog(self) -> None:
        import subprocess

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
