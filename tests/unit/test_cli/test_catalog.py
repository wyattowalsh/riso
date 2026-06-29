"""Tests for module catalog loading."""

from __future__ import annotations

import pytest

from riso.core.paths import resolve_template_path
from riso.template import get_module_catalog

pytestmark = pytest.mark.unit


def test_get_module_catalog_finds_modules_at_template_files_path() -> None:
    template = resolve_template_path()
    catalog_path = template / "files" / "module_catalog.json.jinja"
    assert catalog_path.exists()

    catalog = get_module_catalog(template)

    assert "error" not in catalog
    module_names = {module["name"] for module in catalog["modules"]}
    assert "quality" in module_names
    assert "cli" in module_names
