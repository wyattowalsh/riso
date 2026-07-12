"""Unit tests for scripts.lib.smoke_schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    from scripts.lib.smoke_schema import (  # noqa: E402
        assert_no_failures,
        build_canonical,
        failure_count,
        is_canonical,
        iter_modules,
        load_smoke,
        module_names,
    )
except ModuleNotFoundError:  # pragma: no cover
    SCRIPTS = REPO / "scripts"
    if str(SCRIPTS) not in sys.path:
        sys.path.append(str(SCRIPTS))
    from lib.smoke_schema import (  # type: ignore[no-redef]  # noqa: E402
        assert_no_failures,
        build_canonical,
        failure_count,
        is_canonical,
        iter_modules,
        load_smoke,
        module_names,
    )

FIXTURES = REPO / "tests" / "fixtures" / "json_samples"


def test_load_canonical_pass_fixture() -> None:
    payload = load_smoke(FIXTURES / "smoke_results_pass.json")
    assert is_canonical(payload)
    assert failure_count(payload) == 0
    assert set(module_names(payload)) == {"cli", "api"}


def test_load_canonical_failures_fixture() -> None:
    payload = load_smoke(FIXTURES / "smoke_results_failures.json")
    assert is_canonical(payload)
    assert failure_count(payload) == 1
    with pytest.raises(ValueError, match="failed"):
        assert_no_failures(payload)


def test_iter_modules_legacy_results_list() -> None:
    legacy = {
        "results": [
            {"module": "cli", "status": "passed"},
            {"name": "api", "status": "failed"},
        ]
    }
    items = list(iter_modules(legacy))
    assert items[0][0] == "cli"
    assert items[1][1]["status"] == "failed"
    assert failure_count(legacy) == 1
    assert is_canonical(legacy) is False


def test_build_canonical() -> None:
    payload = build_canonical(
        variant="x",
        timestamp="t",
        modules={"cli": {"status": "passed"}},
    )
    assert payload == {
        "variant": "x",
        "timestamp": "t",
        "modules": {"cli": {"status": "passed"}},
    }
    assert is_canonical(payload)


def test_load_smoke_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(ValueError, match="object"):
        load_smoke(path)
