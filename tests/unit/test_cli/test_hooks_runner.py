"""Unit tests for hooks_runner."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.core.errors import CopierOperationError
from riso.template.hooks_runner import (
    find_post_gen_script,
    run_post_gen,
    should_skip_post_gen,
)


def test_should_skip_post_gen_flag_and_env() -> None:
    assert should_skip_post_gen(skip_flag=True) is True
    assert should_skip_post_gen(env={"RISO_SKIP_POST_GEN": "1"}) is True
    assert should_skip_post_gen(env={"RISO_SKIP_POST_GEN": "true"}) is True
    assert should_skip_post_gen(env={}) is False


def test_find_post_gen_script_in_repo() -> None:
    path = find_post_gen_script()
    assert path is not None
    assert path.name == "post_gen_project.py"
    assert path.is_file()


def test_run_post_gen_success_stub(tmp_path: Path) -> None:
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
    run_post_gen(dest, template_hint=tmp_path)
    assert (dest / ".riso" / "marker").read_text(encoding="utf-8") == "ok"


def test_run_post_gen_propagates_systemexit(tmp_path: Path) -> None:
    hook_dir = tmp_path / "hooks"
    hook_dir.mkdir()
    (hook_dir / "post_gen_project.py").write_text(
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    dest.mkdir()
    with pytest.raises(CopierOperationError, match="post_gen"):
        run_post_gen(dest, template_hint=tmp_path)


def test_run_post_gen_missing_dest() -> None:
    with pytest.raises(FileNotFoundError):
        run_post_gen(Path("/nonexistent/riso-dest-xyz"))
