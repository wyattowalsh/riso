"""Unit tests for hooks_runner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from riso.core.errors import CopierOperationError, OperationTimeoutError
from riso.core.paths import resolve_template_path
from riso.template.hooks_runner import (
    find_post_gen_script,
    find_pre_gen_script,
    run_post_gen,
    run_pre_gen,
    should_skip_hooks,
    should_skip_post_gen,
)


def test_should_skip_post_gen_flag_and_env() -> None:
    """Explicit flags and supported environment values skip managed hooks."""
    assert should_skip_post_gen(skip_flag=True) is True
    assert should_skip_post_gen(env={"RISO_SKIP_POST_GEN": "1"}) is True
    assert should_skip_post_gen(env={"RISO_SKIP_POST_GEN": "true"}) is True
    assert should_skip_post_gen(env={}) is False


def test_should_skip_hooks_shares_post_gen_escape_hatch() -> None:
    """Hook coordination recognizes the established post-gen skip signal."""
    assert should_skip_hooks(skip_flag=True) is True
    assert should_skip_hooks(env={"RISO_SKIP_POST_GEN": "1"}) is True
    assert should_skip_hooks(env={"RISO_SKIP_POST_GEN": "yes"}) is True
    assert should_skip_hooks(env={"RISO_SKIP_POST_GEN": "on"}) is True
    assert should_skip_hooks(env={}) is False
    assert should_skip_hooks(env={"RISO_SKIP_POST_GEN": "0"}) is False


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
    script = hook_dir / "post_gen_project.py"
    script.write_text("raise SystemExit(1)\n", encoding="utf-8")
    dest = tmp_path / "dest"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.template.hooks_runner.find_post_gen_script",
        lambda template_hint=None: script,
    )
    with pytest.raises(CopierOperationError, match="post_gen"):
        run_post_gen(dest, template_hint=tmp_path)


def test_run_post_gen_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A real sleeping post-gen process stops at its configured timeout."""
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    script = hook_dir / "post_gen_project.py"
    script.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
    dest = tmp_path / "dest"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.template.hooks_runner.find_post_gen_script",
        lambda template_hint=None: script,
    )
    with pytest.raises(OperationTimeoutError, match="post_gen"):
        run_post_gen(dest, template_hint=tmp_path, timeout=1)


def test_run_post_gen_does_not_execute_untrusted_hint(tmp_path: Path) -> None:
    """External hints are rejected instead of executing even a bundled fallback."""
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    evil = hook_dir / "post_gen_project.py"
    evil.write_text(
        "from pathlib import Path\nPath('EVIL').write_text('x')\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    with patch("riso.template._copier_worker.run_argv_with_timeout") as worker:
        with pytest.raises(CopierOperationError, match="Trusted"):
            run_post_gen(dest, template_hint=tmp_path)
    worker.assert_not_called()
    assert not (dest / "EVIL").exists()


def test_find_post_gen_script_bundled_hint_uses_template() -> None:
    """A bundled hint selects the exact trusted post-gen file."""
    bundled = resolve_template_path()
    path = find_post_gen_script(bundled)
    assert path is not None
    assert path == bundled / "hooks" / "post_gen_project.py"


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


def test_find_pre_gen_script_in_repo() -> None:
    """Pre-gen discovery finds the shipped explicit operator helper."""
    path = find_pre_gen_script()
    assert path is not None
    assert path.name == "pre_gen_project.py"
    assert path.is_file()


def test_find_pre_gen_script_ignores_untrusted_hint(tmp_path: Path) -> None:
    """External pre-gen hints resolve to no eligible hook."""
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    (hook_dir / "pre_gen_project.py").write_text("raise SystemExit(99)\n")
    found = find_pre_gen_script(tmp_path)
    assert found is None


def test_find_pre_gen_script_bundled_hint_uses_template() -> None:
    """A bundled pre-gen hint selects the exact shipped script."""
    bundled = resolve_template_path()
    path = find_pre_gen_script(bundled)
    assert path is not None
    assert path == bundled / "hooks" / "pre_gen_project.py"


def test_run_pre_gen_sets_copier_answers_from_dest_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Explicit pre-gen receives serialized answers from saved project YAML."""
    script = tmp_path / "pre_gen_project.py"
    script.write_text("raise SystemExit(0)\n", encoding="utf-8")
    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "project_name: Demo\ncli_module: enabled\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "riso.template.hooks_runner.find_pre_gen_script",
        lambda template_hint=None: script,
    )
    captured: dict[str, Any] = {}

    # Retain named keyword parameters required by the patched subprocess helper.
    def fake_run(
        argv: list[str],
        *,
        timeout: int | None,  # pylint: disable=unused-argument
        cwd: object = None,
        env: object = None,
    ) -> subprocess.CompletedProcess[str]:
        captured["argv"] = argv
        captured["env"] = env
        captured["cwd"] = cwd
        return subprocess.CompletedProcess(argv, 0, "", "")

    with patch(
        "riso.template._copier_worker.run_argv_with_timeout",
        side_effect=fake_run,
    ):
        run_pre_gen(dest, template_hint=tmp_path)

    assert captured["cwd"] == dest.resolve()
    env = captured["env"]
    assert isinstance(env, dict)
    answers = json.loads(env["COPIER_ANSWERS"])
    assert answers["project_name"] == "Demo"
    assert answers["cli_module"] == "enabled"


def test_run_pre_gen_preserves_existing_copier_answers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Operator-supplied answers take precedence over saved project YAML."""
    script = tmp_path / "pre_gen_project.py"
    script.write_text("raise SystemExit(0)\n", encoding="utf-8")
    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "project_name: FromFile\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "riso.template.hooks_runner.find_pre_gen_script",
        lambda template_hint=None: script,
    )
    captured: dict[str, Any] = {}

    # Retain named keyword parameters required by the patched subprocess helper.
    def fake_run(
        argv: list[str],
        *,
        timeout: int | None,  # pylint: disable=unused-argument
        cwd: object = None,  # pylint: disable=unused-argument
        env: object = None,
    ) -> subprocess.CompletedProcess[str]:
        captured["env"] = env
        return subprocess.CompletedProcess(argv, 0, "", "")

    with patch(
        "riso.template._copier_worker.run_argv_with_timeout",
        side_effect=fake_run,
    ):
        run_pre_gen(
            dest,
            template_hint=tmp_path,
            extra_env={"COPIER_ANSWERS": '{"project_name": "Preset"}'},
        )

    env = captured["env"]
    assert isinstance(env, dict)
    assert json.loads(env["COPIER_ANSWERS"]) == {"project_name": "Preset"}


def test_run_pre_gen_propagates_systemexit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Explicit pre-gen reports nonzero child exits as operation failures."""
    script = tmp_path / "pre_gen_project.py"
    script.write_text("raise SystemExit(1)\n", encoding="utf-8")
    dest = tmp_path / "dest"
    dest.mkdir()
    monkeypatch.setattr(
        "riso.template.hooks_runner.find_pre_gen_script",
        lambda template_hint=None: script,
    )
    with pytest.raises(CopierOperationError, match="pre_gen"):
        run_pre_gen(dest, template_hint=tmp_path)


def test_run_pre_gen_does_not_execute_untrusted_hint(tmp_path: Path) -> None:
    """Explicit pre-gen also rejects an external hook without starting a child."""
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    evil = hook_dir / "pre_gen_project.py"
    evil.write_text(
        "from pathlib import Path\nPath('EVIL').write_text('x')\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    with patch("riso.template._copier_worker.run_argv_with_timeout") as worker:
        with pytest.raises(CopierOperationError, match="Trusted"):
            run_pre_gen(dest, template_hint=tmp_path)
    worker.assert_not_called()
    assert not (dest / "EVIL").exists()


def test_run_pre_gen_missing_dest() -> None:
    """Explicit pre-gen rejects a missing destination before starting a child."""
    with pytest.raises(FileNotFoundError):
        run_pre_gen(Path("/nonexistent/riso-dest-xyz"))
