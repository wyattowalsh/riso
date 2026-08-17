"""Sphinx official smoke honors task_runner instead of dest-root make."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.lib.sphinx_smoke import sphinx_linkcheck_command

pytestmark = pytest.mark.unit

RENDER_SAMPLES = Path(__file__).resolve().parents[3] / "scripts" / "render-samples.sh"


def test_just_dest_uses_just_linkcheck(tmp_path: Path) -> None:
    python_cwd = tmp_path / "python"
    python_cwd.mkdir()
    (python_cwd / "justfile").write_text("linkcheck:\n    true\n", encoding="utf-8")
    assert sphinx_linkcheck_command(python_cwd, "just") == ["just", "linkcheck"]
    assert sphinx_linkcheck_command(python_cwd, None) == ["just", "linkcheck"]


def test_makefile_dest_uses_make_linkcheck(tmp_path: Path) -> None:
    python_cwd = tmp_path / "python"
    python_cwd.mkdir()
    (python_cwd / "Makefile").write_text("linkcheck:\n\ttrue\n", encoding="utf-8")
    assert sphinx_linkcheck_command(python_cwd, "makefile") == [
        "uv",
        "run",
        "make",
        "linkcheck",
    ]


def test_fallback_is_sphinx_build_not_make(tmp_path: Path) -> None:
    python_cwd = tmp_path / "python"
    python_cwd.mkdir()
    command = sphinx_linkcheck_command(python_cwd, "just")
    assert command[0:3] == ["uv", "run", "--group"]
    assert "make" not in command
    assert "sphinx-build" in command


def test_render_samples_wires_helper_not_hardcoded_make() -> None:
    text = RENDER_SAMPLES.read_text(encoding="utf-8")
    assert "from scripts.lib.sphinx_smoke import sphinx_linkcheck_command" in text
    assert 'docs_command = ["uv", "run", "make", "linkcheck"]' not in text
