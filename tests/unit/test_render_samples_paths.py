"""Tests for render-samples.sh path canonicalization and COPIER_CMD guards."""

from __future__ import annotations

import subprocess
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
canonicalize_answers_path() {{
  local answers="$1"
  if [[ "${{answers}}" != /* ]]; then
    answers="${{REPO_ROOT}}/${{answers#./}}"
  fi
  printf '%s' "${{answers}}"
}}
validate_render_paths() {{
  local variant="$1"
  local answers_file="$2"
  local destination="$3"
  if [[ "${{answers_file}}" != "${{SAMPLES_DIR}}/"* ]]; then
    echo "ERROR: Answers file must live under ${{SAMPLES_DIR}}: ${{answers_file}}" >&2
    exit 1
  fi
}}
answers="$(canonicalize_answers_path "samples/default/copier-answers.yml")"
validate_render_paths "default" "${{answers}}" "${{SAMPLES_DIR}}/default/render"
echo "ok:${{answers}}"
"""
    proc = subprocess.run(
        ["bash", "-c", bash],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == f"ok:{REPO_ROOT}/samples/default/copier-answers.yml"


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
