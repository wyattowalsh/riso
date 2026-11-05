"""Tests for render-samples.sh path canonicalization and COPIER_CMD guards."""

from __future__ import annotations

import subprocess
import shlex
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render-samples.sh"


def _extract_bash_function(name: str) -> str:
    """Return a top-level `name() { ... }` body from render-samples.sh."""
    text = RENDER_SCRIPT.read_text(encoding="utf-8")
    header = f"{name}() {{"
    start = text.index(header)
    end = text.index("\n}\n", start) + 2
    return text[start:end]


def test_canonicalize_relative_answers_under_samples_dir() -> None:
    """Relative --answers paths resolve under REPO_ROOT before validation."""
    bash = f"""
set -euo pipefail
REPO_ROOT="{REPO_ROOT}"
SAMPLES_DIR="${{REPO_ROOT}}/samples"
{_extract_bash_function("log")}
{_extract_bash_function("canonicalize_answers_path")}
{_extract_bash_function("validate_render_paths")}
answers="$(canonicalize_answers_path "samples/default/copier-answers.yml")"
validate_render_paths "default" "${{answers}}" "${{SAMPLES_DIR}}/default/render"
echo "ok:${{answers}}"
"""
    proc = subprocess.run(
        ["bash", "-c", bash],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == f"ok:{REPO_ROOT}/samples/default/copier-answers.yml"


def _validate_paths(
    repo: Path, variant: str, answers: Path, destination: Path
) -> subprocess.CompletedProcess[str]:
    """Exercise the real destructive-operation guard without invoking a render."""
    bash = f"""
set -euo pipefail
REPO_ROOT={shlex.quote(str(repo))}
SAMPLES_DIR="${{REPO_ROOT}}/samples"
{_extract_bash_function("log")}
{_extract_bash_function("validate_render_paths")}
validate_render_paths \
    {shlex.quote(variant)} \
    {shlex.quote(str(answers))} \
    {shlex.quote(str(destination))}
"""
    return subprocess.run(
        ["bash", "-c", bash],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )


@pytest.mark.parametrize(
    "variant", ["../..", "default/../../outside", "./default", "default/.."]
)
def test_render_rejects_traversal_before_deleting(tmp_path: Path, variant: str) -> None:
    """Verify render rejects traversal before deleting."""
    sample = tmp_path / "samples" / "default"
    sample.mkdir(parents=True)
    answers = sample / "copier-answers.yml"
    answers.write_text("project_name: test\n", encoding="utf-8")
    outside = tmp_path / "render"
    outside.mkdir()
    sentinel = outside / "keep.txt"
    sentinel.write_text("unrelated work", encoding="utf-8")
    result = _validate_paths(
        tmp_path, variant, answers, tmp_path / "samples" / variant / "render"
    )
    assert result.returncode != 0
    assert sentinel.read_text(encoding="utf-8") == "unrelated work"


def test_render_rejects_symlinked_variant(tmp_path: Path) -> None:
    """Verify render rejects symlinked variant."""
    samples = tmp_path / "samples"
    samples.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    answers = outside / "copier-answers.yml"
    answers.write_text("project_name: test\n", encoding="utf-8")
    (samples / "escape").symlink_to(outside, target_is_directory=True)
    result = _validate_paths(tmp_path, "escape", answers, samples / "escape" / "render")
    assert result.returncode != 0
    assert not (outside / "render").exists()


def test_render_rejects_symlinked_destination(tmp_path: Path) -> None:
    """Verify render rejects symlinked destination."""
    sample = tmp_path / "samples" / "default"
    sample.mkdir(parents=True)
    answers = sample / "copier-answers.yml"
    answers.write_text("project_name: test\n", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    (sample / "render").symlink_to(outside, target_is_directory=True)
    result = _validate_paths(tmp_path, "default", answers, sample / "render")
    assert result.returncode != 0
    assert (sample / "render").is_symlink()


def test_render_rejects_mismatched_answers(tmp_path: Path) -> None:
    """Verify render rejects mismatched answers."""
    for name in ("default", "other"):
        sample = tmp_path / "samples" / name
        sample.mkdir(parents=True)
        (sample / "copier-answers.yml").write_text(
            "project_name: test\n", encoding="utf-8"
        )
    result = _validate_paths(
        tmp_path,
        "default",
        tmp_path / "samples/other/copier-answers.yml",
        tmp_path / "samples/default/render",
    )
    assert result.returncode != 0


def test_render_accepts_nested_variant(tmp_path: Path) -> None:
    """Verify render accepts nested variant."""
    sample = tmp_path / "samples" / "saas-starter" / "vercel-starter"
    sample.mkdir(parents=True)
    answers = sample / "copier-answers.yml"
    answers.write_text("project_name: test\n", encoding="utf-8")
    result = _validate_paths(
        tmp_path, "saas-starter/vercel-starter", answers, sample / "render"
    )
    assert result.returncode == 0, result.stderr


def test_copier_cmd_rejects_non_copier_executable() -> None:
    """Non-copier COPIER_CMD binaries fail in resolve_copier_cmd (no render)."""
    bash = f"""
set -euo pipefail
REPO_ROOT="{REPO_ROOT}"
COPIER_CMD="/bin/echo"
COPIER_CMD_ARR=()
{_extract_bash_function("resolve_copier_cmd")}
resolve_copier_cmd
"""
    proc = subprocess.run(
        ["bash", "-c", bash],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    assert proc.returncode != 0, proc.stderr
    combined = proc.stderr.lower()
    assert "copier binary" in combined or "invalid copier_cmd" in combined
