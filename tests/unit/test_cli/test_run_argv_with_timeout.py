"""Unit tests for process-group timeout helper."""

from __future__ import annotations

import os
import signal
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from riso.template._copier_worker import run_argv_with_timeout

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(os.name != "posix", reason="killpg requires POSIX"),
]


def test_timeout_sends_sigterm_to_process_group() -> None:
    """The first timeout signal addresses the child's entire process group."""
    proc = MagicMock()
    proc.pid = 4242
    proc.returncode = None
    proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd=["x"], timeout=1),
        ("", ""),
    ]

    with (
        patch("riso.template._copier_worker.subprocess.Popen", return_value=proc),
        patch("riso.template._copier_worker.os.killpg") as killpg,
        patch("riso.template._copier_worker.os.kill"),
    ):
        with pytest.raises(subprocess.TimeoutExpired):
            run_argv_with_timeout(["true"], timeout=1)

    assert any(
        call.args[0] == 4242 and call.args[1] == signal.SIGTERM
        for call in killpg.call_args_list
    )


def test_timeout_escalates_to_sigkill_when_wait_fails() -> None:
    """A process that outlives graceful termination triggers group SIGKILL."""
    proc = MagicMock()
    proc.pid = 5150
    proc.returncode = None
    proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd=["x"], timeout=1),
        ("", ""),
    ]
    proc.wait.side_effect = subprocess.TimeoutExpired(cmd=["x"], timeout=2)

    with (
        patch("riso.template._copier_worker.subprocess.Popen", return_value=proc),
        patch("riso.template._copier_worker.os.killpg") as killpg,
    ):
        with pytest.raises(subprocess.TimeoutExpired):
            run_argv_with_timeout(["true"], timeout=1)

    signals = [call.args[1] for call in killpg.call_args_list]
    assert signal.SIGTERM in signals
    assert signal.SIGKILL in signals


def test_timeout_kills_remaining_group_after_parent_exits() -> None:
    """A reaped parent does not mean descendants honored SIGTERM."""
    proc = MagicMock()
    proc.pid = 6161
    proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd=["x"], timeout=1),
        ("", ""),
    ]
    with (
        patch("riso.template._copier_worker.subprocess.Popen", return_value=proc),
        patch("riso.template._copier_worker.os.killpg") as killpg,
    ):
        with pytest.raises(subprocess.TimeoutExpired):
            run_argv_with_timeout(["true"], timeout=1)
    assert [call.args[1] for call in killpg.call_args_list] == [
        signal.SIGTERM,
        signal.SIGKILL,
    ]


def test_success_returns_completed_process() -> None:
    """Successful commands preserve captured output and their exit status."""
    proc = MagicMock()
    proc.pid = 7
    proc.returncode = 0
    proc.communicate.return_value = ("out", "err")

    with patch("riso.template._copier_worker.subprocess.Popen", return_value=proc):
        completed = run_argv_with_timeout(["echo", "hi"], timeout=5)

    assert completed.returncode == 0
    assert completed.stdout == "out"
    assert completed.stderr == "err"
