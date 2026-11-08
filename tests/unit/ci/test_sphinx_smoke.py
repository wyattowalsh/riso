"""Verify Sphinx smoke commands and builder-independent autosummary startup."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.lib.sphinx_smoke import sphinx_linkcheck_command

pytestmark = pytest.mark.unit

RENDER_SAMPLES = Path(__file__).resolve().parents[3] / "scripts" / "render-samples.sh"


def test_just_dest_uses_just_linkcheck(tmp_path: Path) -> None:
    """Honor an explicit or detected Just task runner."""
    python_cwd = tmp_path / "python"
    python_cwd.mkdir()
    (python_cwd / "justfile").write_text("linkcheck:\n    true\n", encoding="utf-8")
    assert sphinx_linkcheck_command(python_cwd, "just") == ["just", "linkcheck"]
    assert sphinx_linkcheck_command(python_cwd, None) == ["just", "linkcheck"]


def test_makefile_dest_uses_make_linkcheck(tmp_path: Path) -> None:
    """Run Make through uv for rendered Makefile projects."""
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
    """Use Sphinx directly when no rendered task runner exists."""
    python_cwd = tmp_path / "python"
    python_cwd.mkdir()
    command = sphinx_linkcheck_command(python_cwd, "just")
    assert command[0:3] == ["uv", "run", "--group"]
    assert "make" not in command
    assert "sphinx-build" in command


def test_render_samples_wires_helper_not_hardcoded_make() -> None:
    """Keep official sample smoke checks on the shared runner selector."""
    text = RENDER_SAMPLES.read_text(encoding="utf-8")
    assert "from scripts.lib.sphinx_smoke import sphinx_linkcheck_command" in text
    assert 'docs_command = ["uv", "run", "make", "linkcheck"]' not in text


def test_autosummary_renderer_keeps_real_translation_extension() -> None:
    """Configured mocks must not replace Jinja before non-HTML builder startup."""
    if importlib.util.find_spec("sphinx") is None:
        pytest.skip("Sphinx is available in the optional docs dependency group")

    # A fresh process prevents HTML's earlier Jinja extension import from masking
    # the mock collision that breaks linkcheck's autosummary renderer.
    script = """
import ast
import sys
from gettext import NullTranslations
from pathlib import Path
from types import SimpleNamespace

from sphinx.ext.autodoc.mock import mock
from sphinx.ext.autosummary.generate import AutosummaryRenderer

config_path = Path(sys.argv[1])
config_tree = ast.parse(config_path.read_text(encoding="utf-8"))
mock_imports = next(
    ast.literal_eval(node.value)
    for node in config_tree.body
    if isinstance(node, ast.Assign)
    and any(
        isinstance(target, ast.Name) and target.id == "autodoc_mock_imports"
        for target in node.targets
    )
)
app = SimpleNamespace(
    srcdir=config_path.parent,
    config=SimpleNamespace(templates_path=[]),
    translator=NullTranslations(),
)
with mock(mock_imports):
    renderer = AutosummaryRenderer(app)
    result = renderer.env.from_string("{{ _('ready') }}").render()
    assert result == "ready", result
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(RENDER_SAMPLES.parents[1] / "docs/conf.py")],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
