"""Unit tests for hooks_runner."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
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
    assert should_skip_post_gen(skip_flag=True) is True
    assert should_skip_post_gen(env={"RISO_SKIP_POST_GEN": "1"}) is True
    assert should_skip_post_gen(env={"RISO_SKIP_POST_GEN": "true"}) is True
    assert should_skip_post_gen(env={}) is False


def test_should_skip_hooks_shares_post_gen_escape_hatch() -> None:
    assert should_skip_hooks(skip_flag=True) is True
    assert should_skip_hooks(env={"RISO_SKIP_POST_GEN": "1"}) is True
    assert should_skip_hooks(env={"RISO_SKIP_POST_GEN": "yes"}) is True
    assert should_skip_hooks(env={"RISO_SKIP_POST_GEN": "on"}) is True
    assert should_skip_hooks(env={}) is False
    assert should_skip_hooks(env={"RISO_SKIP_POST_GEN": "0"}) is False


def test_find_post_gen_script_in_repo() -> None:
    path = find_post_gen_script()
    assert path is not None
    assert path.name == "post_gen_project.py"
    assert path.is_file()


def test_find_post_gen_script_ignores_untrusted_hint(tmp_path: Path) -> None:
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    (hook_dir / "post_gen_project.py").write_text("raise SystemExit(99)\n")
    found = find_post_gen_script(tmp_path)
    bundled = find_post_gen_script()
    assert found == bundled
    assert found is not None
    assert found != (hook_dir / "post_gen_project.py").resolve()


def test_run_post_gen_success_stub(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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
        "riso.template.hooks_runner.find_post_gen_script",
        lambda template_hint=None: script,
    )
    run_post_gen(dest, template_hint=tmp_path)
    assert (dest / ".riso" / "marker").read_text(encoding="utf-8") == "ok"


def test_run_post_gen_propagates_systemexit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    evil = hook_dir / "post_gen_project.py"
    evil.write_text(
        "from pathlib import Path\nPath('EVIL').write_text('x')\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    captured: dict[str, list[str]] = {}

    def fake_run(
        argv: list[str],
        *,
        timeout: int | None,
        cwd: object = None,
        env: object = None,
    ) -> subprocess.CompletedProcess[str]:
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, "", "")

    with patch(
        "riso.template._copier_worker.run_argv_with_timeout",
        side_effect=fake_run,
    ):
        run_post_gen(dest, template_hint=tmp_path)

    assert captured["argv"][-1] != str(evil.resolve())
    assert captured["argv"][-1].endswith("post_gen_project.py")
    assert not (dest / "EVIL").exists()


def test_find_post_gen_script_bundled_hint_uses_template() -> None:
    bundled = resolve_template_path()
    path = find_post_gen_script(bundled)
    assert path is not None
    assert path == bundled / "hooks" / "post_gen_project.py"


def test_run_post_gen_missing_dest() -> None:
    with pytest.raises(FileNotFoundError):
        run_post_gen(Path("/nonexistent/riso-dest-xyz"))


def test_find_pre_gen_script_in_repo() -> None:
    path = find_pre_gen_script()
    assert path is not None
    assert path.name == "pre_gen_project.py"
    assert path.is_file()


def test_find_pre_gen_script_ignores_untrusted_hint(tmp_path: Path) -> None:
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    (hook_dir / "pre_gen_project.py").write_text("raise SystemExit(99)\n")
    found = find_pre_gen_script(tmp_path)
    bundled = find_pre_gen_script()
    assert found == bundled
    assert found is not None
    assert found != (hook_dir / "pre_gen_project.py").resolve()


def test_find_pre_gen_script_bundled_hint_uses_template() -> None:
    bundled = resolve_template_path()
    path = find_pre_gen_script(bundled)
    assert path is not None
    assert path == bundled / "hooks" / "pre_gen_project.py"


def test_run_pre_gen_sets_copier_answers_from_dest_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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

    def fake_run(
        argv: list[str],
        *,
        timeout: int | None,
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

    def fake_run(
        argv: list[str],
        *,
        timeout: int | None,
        cwd: object = None,
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
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    evil = hook_dir / "pre_gen_project.py"
    evil.write_text(
        "from pathlib import Path\nPath('EVIL').write_text('x')\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    captured: dict[str, list[str]] = {}

    def fake_run(
        argv: list[str],
        *,
        timeout: int | None,
        cwd: object = None,
        env: object = None,
    ) -> subprocess.CompletedProcess[str]:
        captured["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, "", "")

    with patch(
        "riso.template._copier_worker.run_argv_with_timeout",
        side_effect=fake_run,
    ):
        run_pre_gen(dest, template_hint=tmp_path)

    assert captured["argv"][-1] != str(evil.resolve())
    assert captured["argv"][-1].endswith("pre_gen_project.py")
    assert not (dest / "EVIL").exists()


def test_run_pre_gen_missing_dest() -> None:
    with pytest.raises(FileNotFoundError):
        run_pre_gen(Path("/nonexistent/riso-dest-xyz"))
