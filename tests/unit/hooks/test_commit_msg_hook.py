"""Tests for scripts/hooks/commit-msg.sh (commit-msg SSOT fallback)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_SCRIPT = REPO_ROOT / "scripts" / "hooks" / "commit-msg.sh"


pytestmark = pytest.mark.unit


def run_hook(
    message: str, *, cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    msg_file = (cwd or REPO_ROOT) / ".git" / "COMMIT_EDITMSG"
    msg_file.parent.mkdir(parents=True, exist_ok=True)
    msg_file.write_text(message, encoding="utf-8")
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"}
    return subprocess.run(
        ["bash", str(HOOK_SCRIPT), str(msg_file)],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


class TestCommitMsgHook:
    def test_hook_script_exists(self) -> None:
        assert HOOK_SCRIPT.exists()

    def test_accepts_conventional_message_without_commitlint(
        self, tmp_path: Path
    ) -> None:
        result = run_hook("feat(cli): add validate command\n", cwd=tmp_path)
        assert result.returncode == 0, result.stderr

    def test_rejects_invalid_message_without_commitlint(self, tmp_path: Path) -> None:
        result = run_hook("bad commit message\n", cwd=tmp_path)
        assert result.returncode != 0
        assert "conventional" in (result.stderr + result.stdout).lower()

    def test_rejects_missing_argument(self) -> None:
        result = subprocess.run(
            ["bash", str(HOOK_SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        assert "missing commit message" in result.stderr
