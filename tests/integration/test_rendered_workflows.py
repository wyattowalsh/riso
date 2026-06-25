"""Integration checks for rendered GitHub Actions workflows (CI audit W3-14)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[2]

GITHUB_ACTION_VARIANTS = (
    "default",
    "changelog-python",
    "full-stack",
)

LEAKED_WORKFLOW_NAMES = frozenset({"template-ci.yml", "quality-matrix.yml"})
JINJA_MARKERS = ("{%", "%}")


def _actionlint_available() -> bool:
    try:
        proc = subprocess.run(
            ["actionlint", "-version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        return proc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _render_root(variant: str) -> Path:
    return REPO_ROOT / "samples" / variant / "render"


@pytest.fixture(scope="module")
def require_actionlint() -> None:
    if not _actionlint_available():
        pytest.skip("actionlint not installed")


@pytest.mark.parametrize("variant", GITHUB_ACTION_VARIANTS)
def test_rendered_workflows_exclude_maintainer_leaks(
    variant: str,
) -> None:
    workflows_dir = _render_root(variant) / ".github" / "workflows"
    if not workflows_dir.is_dir():
        pytest.skip(f"{variant} render missing; run ./scripts/render-samples.sh")

    names = {path.name for path in workflows_dir.glob("*.yml")}
    leaked = names & LEAKED_WORKFLOW_NAMES
    assert not leaked, f"{variant} leaked maintainer workflows: {sorted(leaked)}"


@pytest.mark.parametrize("variant", GITHUB_ACTION_VARIANTS)
def test_rendered_workflows_have_no_jinja_remnants(variant: str) -> None:
    workflows_dir = _render_root(variant) / ".github" / "workflows"
    if not workflows_dir.is_dir():
        pytest.skip(f"{variant} render missing; run ./scripts/render-samples.sh")

    for workflow in sorted(workflows_dir.glob("*.yml")):
        content = workflow.read_text(encoding="utf-8")
        for marker in JINJA_MARKERS:
            assert marker not in content, (
                f"{variant}/{workflow.name} contains Jinja marker {marker!r}"
            )


@pytest.mark.parametrize("variant", GITHUB_ACTION_VARIANTS)
def test_rendered_workflows_pass_actionlint(
    variant: str,
    require_actionlint: None,
) -> None:
    workflows_dir = _render_root(variant) / ".github" / "workflows"
    if not workflows_dir.is_dir():
        pytest.skip(f"{variant} render missing; run ./scripts/render-samples.sh")

    workflow_files = sorted(workflows_dir.glob("*.yml"))
    if not workflow_files:
        pytest.skip(f"{variant} has no rendered workflows")

    proc = subprocess.run(
        ["actionlint", *[str(path) for path in workflow_files]],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"actionlint failed for {variant}:\n{proc.stdout}\n{proc.stderr}"
    )


def test_changelog_release_workflow_has_quality_job() -> None:
    release_workflow = (
        _render_root("changelog-python") / ".github" / "workflows" / "riso-release.yml"
    )
    if not release_workflow.is_file():
        pytest.skip("changelog-python render missing; run ./scripts/render-samples.sh")

    content = release_workflow.read_text(encoding="utf-8")
    assert "quality:" in content
    assert "needs: [quality]" in content or "needs:\n      - quality" in content


def test_validate_release_configs_passes_changelog_render() -> None:
    render_dir = _render_root("changelog-python")
    if not render_dir.is_dir():
        pytest.skip("changelog-python render missing; run ./scripts/render-samples.sh")

    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ci" / "validate_release_configs.py"),
            "--project-dir",
            str(render_dir),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
