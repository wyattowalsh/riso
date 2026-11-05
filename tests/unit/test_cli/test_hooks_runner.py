"""Unit tests for hooks_runner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from riso.core.errors import CopierOperationError, OperationTimeoutError
from riso.template.hooks_runner import (
    find_post_gen_script,
    run_post_gen,
    should_skip_post_gen,
)


def test_should_skip_post_gen_flag_and_env() -> None:
    """Explicit flags and supported environment values skip managed hooks."""
    assert should_skip_post_gen(skip_flag=True) is True
    assert should_skip_post_gen(env={"RISO_SKIP_POST_GEN": "1"}) is True
    assert should_skip_post_gen(env={"RISO_SKIP_POST_GEN": "true"}) is True
    assert should_skip_post_gen(env={}) is False


def test_find_post_gen_script_in_repo() -> None:
    """Default discovery selects the checked-in bundled post-generation hook."""
    path = find_post_gen_script()
    assert path is not None
    assert path.name == "post_gen_project.py"
    assert path.is_file()


def test_run_post_gen_success_stub(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A trusted stub executes in the destination and writes its marker."""
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    script = hook_dir / "post_gen_project.py"
    script.write_text(
        "from pathlib import Path\n"
        "Path('.riso').mkdir(exist_ok=True)\n"
        "Path('.riso/marker').write_text('ok', encoding='utf-8')\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.template.hooks_runner.bundled_template_path", lambda: tmp_path
    )
    run_post_gen(dest, template_hint=tmp_path)
    assert (dest / ".riso" / "marker").read_text(encoding="utf-8") == "ok"


def test_run_post_gen_propagates_systemexit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nonzero hook exit codes surface as Copier operation failures."""
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    (hook_dir / "post_gen_project.py").write_text(
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.template.hooks_runner.bundled_template_path", lambda: tmp_path
    )
    with pytest.raises(CopierOperationError, match="post_gen"):
        run_post_gen(dest, template_hint=tmp_path)


def test_external_template_hook_is_rejected_without_execution(tmp_path: Path) -> None:
    """An external hook hint is rejected before any child process starts."""
    external = tmp_path / "external"
    hooks = external / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "post_gen_project.py").write_text("raise RuntimeError('untrusted')\n")
    dest = tmp_path / "dest"
    dest.mkdir()

    assert find_post_gen_script(external) is None
    with patch("riso.template._copier_worker.run_argv_with_timeout") as child:
        with pytest.raises(CopierOperationError, match="Trusted"):
            run_post_gen(dest, template_hint=external)
    child.assert_not_called()


def test_bundled_hook_directory_cannot_symlink_outside_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Bundled-hook discovery rejects a directory symlink to external code."""
    bundled = tmp_path / "bundled"
    external = tmp_path / "external"
    bundled.mkdir()
    external.mkdir()
    (external / "post_gen_project.py").write_text("raise RuntimeError('untrusted')\n")
    (bundled / "hooks").symlink_to(external, target_is_directory=True)
    monkeypatch.setattr(
        "riso.template.hooks_runner.bundled_template_path", lambda: bundled
    )

    assert find_post_gen_script(bundled) is None


def test_hook_changes_only_child_environment_cwd_and_argv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hook mutations leave the calling process environment, cwd, and argv intact."""
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "post_gen_project.py").write_text(
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "Path('observed.json').write_text(json.dumps({'extra': "
        "os.environ.get('RISO_TEST_CHILD_ONLY'), 'argv': sys.argv}))\n"
        "os.environ['RISO_TEST_CHILD_ONLY'] = 'modified'\n"
        "sys.argv[:] = ['modified']\n"
        "os.chdir('..')\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.template.hooks_runner.bundled_template_path", lambda: tmp_path
    )
    monkeypatch.delenv("RISO_TEST_CHILD_ONLY", raising=False)
    parent_env, parent_cwd, parent_argv = dict(os.environ), Path.cwd(), list(sys.argv)

    run_post_gen(dest, extra_env={"RISO_TEST_CHILD_ONLY": "supplied"}, timeout=5)

    observed = json.loads((dest / "observed.json").read_text(encoding="utf-8"))
    assert observed["extra"] == "supplied"
    assert observed["argv"] == [str(hooks / "post_gen_project.py")]
    assert dict(os.environ) == parent_env
    assert Path.cwd() == parent_cwd
    assert sys.argv == parent_argv


def test_hook_timeout_is_reported_as_operation_timeout(tmp_path: Path) -> None:
    """Child timeouts retain the requested limit and domain-specific error."""
    with patch(
        "riso.template._copier_worker.run_argv_with_timeout",
        side_effect=subprocess.TimeoutExpired(cmd="hook", timeout=1),
    ) as child:
        with pytest.raises(OperationTimeoutError):
            run_post_gen(tmp_path, timeout=1)
    assert child.call_args.kwargs["timeout"] == 1
    assert child.call_args.kwargs["cwd"] == tmp_path.resolve()


@pytest.mark.skipif(os.name != "posix", reason="Process-group kill requires POSIX")
def test_hook_timeout_terminates_spawned_children(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A timeout kills descendants even when they ignore the first signal."""
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "post_gen_project.py").write_text(
        "import subprocess, sys, time\n"
        "from pathlib import Path\n"
        "subprocess.Popen([sys.executable, '-c', \"import signal, time; "
        "from pathlib import Path; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "time.sleep(2); Path('escaped').write_text('alive')\"])\n"
        "Path('spawned').touch()\n"
        "time.sleep(30)\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.template.hooks_runner.bundled_template_path", lambda: tmp_path
    )

    with pytest.raises(OperationTimeoutError):
        run_post_gen(dest, timeout=1)

    assert (dest / "spawned").is_file()
    time.sleep(1.3)
    assert not (dest / "escaped").exists()


def test_run_post_gen_missing_dest() -> None:
    """Missing destinations fail before a bundled hook can execute."""
    with pytest.raises(FileNotFoundError):
        run_post_gen(Path("/nonexistent/riso-dest-xyz"))
