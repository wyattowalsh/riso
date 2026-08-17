"""Tests for app._normalize_argv (global flags after subcommands)."""

# pylint: disable=missing-function-docstring

from __future__ import annotations

import pytest

from riso.cli.app import _GLOBAL_FLAGS, _normalize_argv

pytestmark = pytest.mark.unit


def test_normalize_argv_moves_json_before_subcommand() -> None:
    assert _normalize_argv(["doctor", "--json"]) == ["--json", "doctor"]


def test_normalize_argv_moves_quiet_and_verbose() -> None:
    assert _normalize_argv(["catalog", "modules", "-q", "-v"]) == [
        "-q",
        "-v",
        "catalog",
        "modules",
    ]


def test_normalize_argv_moves_template_path_with_value() -> None:
    assert _normalize_argv(
        ["validate", "--template-path", "/tmp/t", "-f", "a.yml"]
    ) == ["--template-path", "/tmp/t", "validate", "-f", "a.yml"]


def test_normalize_argv_handles_equals_form_timeout() -> None:
    assert _normalize_argv(["copy", "./out", "--timeout=12"]) == [
        "--timeout=12",
        "copy",
        "./out",
    ]


def test_normalize_argv_moves_skip_post_gen() -> None:
    assert _normalize_argv(["copy", "./out", "--skip-post-gen"]) == [
        "--skip-post-gen",
        "copy",
        "./out",
    ]


def test_global_flags_keep_skip_post_gen() -> None:
    assert "--skip-post-gen" in _GLOBAL_FLAGS


def test_normalize_argv_does_not_hoist_help() -> None:
    assert _normalize_argv(["migrate", "--help"]) == ["migrate", "--help"]
    assert _normalize_argv(["migrate", "-h"]) == ["migrate", "-h"]
    assert "--help" not in _GLOBAL_FLAGS
    assert "-h" not in _GLOBAL_FLAGS


def test_normalize_argv_empty_and_passthrough() -> None:
    # Explicit empty-list equality is the contract (not just falsey).
    assert _normalize_argv([]) == []  # pylint: disable=use-implicit-booleaness-not-comparison
    assert _normalize_argv(["variants", "list"]) == ["variants", "list"]
