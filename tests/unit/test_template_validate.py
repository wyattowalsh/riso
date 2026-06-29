"""Unit tests for template answer validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from riso.core.errors import PermissionDeniedError
from riso.core.names import validate_identity_fields
from riso.core.paths import resolve_template_path
from riso.template import run_generator, validate_answers

pytestmark = pytest.mark.unit


def test_multiselect_accepts_valid_choices() -> None:
    template = resolve_template_path()
    result = validate_answers(
        {
            "api_module": "enabled",
            "api_languages": ["python", "go"],
        },
        template,
    )
    assert result.valid
    assert not any("api_languages" in err for err in result.errors)


def test_multiselect_rejects_invalid_choice() -> None:
    template = resolve_template_path()
    result = validate_answers(
        {
            "api_module": "enabled",
            "api_languages": ["python", "not-a-language"],
        },
        template,
    )
    assert not result.valid
    assert any("api_languages: invalid choice" in err for err in result.errors)


def test_multiselect_requires_list() -> None:
    template = resolve_template_path()
    result = validate_answers(
        {
            "api_module": "enabled",
            "api_languages": "python",
        },
        template,
    )
    assert not result.valid
    assert any(
        "api_languages: expected list for multiselect" in err for err in result.errors
    )


def test_validate_identity_fields_rejects_package_name_with_dotdot() -> None:
    errors = validate_identity_fields({"package_name": "bad..name"})
    assert any("package_name: must not contain '..'" in err for err in errors)


def test_run_generator_rejects_dangerous_destination() -> None:
    template = resolve_template_path()
    with pytest.raises(PermissionDeniedError):
        run_generator(
            destination=Path("/etc/riso-test"),
            data={"project_name": "demo"},
            template_path=template,
            force=True,
        )
