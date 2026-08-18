"""Integration tests for riso CLI."""

# pylint: disable=missing-function-docstring,consider-using-with

from __future__ import annotations

import json
import os
import signal
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_cli(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    proc = subprocess.Popen(
        ["uv", "run", "riso", *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        stdout, stderr = proc.communicate()
        raise subprocess.TimeoutExpired(
            proc.args,
            timeout,
            output=stdout,
            stderr=stderr,
        ) from None
    return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)


@pytest.mark.integration
def test_doctor_json() -> None:
    proc = _run_cli("doctor", "--json")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["data"]["ready"] is True


@pytest.mark.integration
def test_variants_list_json() -> None:
    proc = _run_cli("variants", "list", "--json")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["data"]["count"] >= 1


@pytest.mark.integration
def test_validate_default_answers() -> None:
    answers = REPO_ROOT / "samples/default/copier-answers.yml"
    proc = _run_cli("validate", "--answers-file", str(answers), "--json")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["data"]["valid"] is True


@pytest.mark.integration
def test_validate_rejects_removed_key() -> None:
    proc = _run_cli(
        "validate",
        "--data",
        "project_name=Test",
        "--data",
        "saas_auth=firebase",
        "--json",
    )
    assert proc.returncode == 2
    payload = json.loads(proc.stderr)
    assert payload["ok"] is False
    assert any("saas_auth" in err for err in payload["errors"])


@pytest.mark.integration
def test_prompts_json() -> None:
    proc = _run_cli("prompts", "--json")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert "prompts" in payload["data"]


@pytest.mark.integration
def test_validate_warnings_in_envelope() -> None:
    proc = _run_cli(
        "validate",
        "--schema-only",
        "--data",
        "project_name=Test",
        "--data",
        "unknown_key_for_test=1",
        "--json",
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["data"]["valid"] is True
    assert payload["warnings"]
    assert any("unknown_key_for_test" in warning for warning in payload["warnings"])


@pytest.mark.integration
@pytest.mark.slow
def test_copy_dry_run_json(tmp_path: Path) -> None:
    answers = REPO_ROOT / "samples/default/copier-answers.yml"
    dest = tmp_path / "dry-run-target"
    proc = _run_cli(
        "copy",
        str(dest),
        "--answers-file",
        str(answers),
        "--dry-run",
        "--json",
        timeout=300,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert "summary" in payload["data"] or "files" in payload["data"]


@pytest.mark.integration
@pytest.mark.slow
def test_diff_copy_json() -> None:
    answers = REPO_ROOT / "samples/default/copier-answers.yml"
    dest = REPO_ROOT / "samples/default/render"
    proc = _run_cli(
        "diff",
        str(dest),
        "--answers-file",
        str(answers),
        "--operation",
        "copy",
        "--json",
        timeout=300,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True


@pytest.mark.integration
@pytest.mark.slow
def test_update_dry_run_json() -> None:
    dest = REPO_ROOT / "samples/default/render"
    if not dest.exists():
        pytest.skip("default render not present")
    proc = _run_cli("update", str(dest), "--dry-run", "--json", timeout=300)
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True


@pytest.mark.integration
def test_recopy_dry_run_json() -> None:
    dest = REPO_ROOT / "samples/default/render"
    if not dest.exists():
        pytest.skip("default render not present")
    answers = dest / ".copier-answers.yml"
    original = answers.read_bytes() if answers.exists() else None
    proc = _run_cli("recopy", str(dest), "--dry-run", "--json", timeout=60)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    data = payload["data"]
    assert data["operation"] == "recopy"
    assert data["dry_run"] is True
    assert data["preview_engine"] == "answers"
    if original is not None:
        assert answers.read_bytes() == original


@pytest.mark.integration
def test_export_cli_alias_json() -> None:
    answers = REPO_ROOT / "samples/default/copier-answers.yml"
    proc = _run_cli("export-cli", "--answers-file", str(answers), "--json")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert "copier_command" in payload["data"]
    assert "riso_command" in payload["data"]
