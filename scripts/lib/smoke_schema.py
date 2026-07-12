"""Canonical smoke-results.json schema helpers for CI scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Mapping

# Canonical statuses for module smoke entries.
FAILURE_STATUSES = frozenset({"failed", "error"})
KNOWN_STATUSES = frozenset({"passed", "failed", "error", "skipped"})


def load_smoke(path: Path | str) -> dict[str, Any]:
    """Load smoke-results JSON from disk."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"smoke results must be an object: {path}")
    return data


def is_canonical(payload: Mapping[str, Any]) -> bool:
    """Return True if payload uses the producer ``modules`` object shape."""
    modules = payload.get("modules")
    return isinstance(modules, dict)


def iter_modules(payload: Mapping[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield ``(name, entry)`` from canonical or legacy smoke payloads.

    Canonical::
        {"modules": {"cli": {"status": "passed", ...}}}

    Legacy (read-only migration)::
        {"results": [{"name"|"module": "cli", "status": "passed"}, ...]}
    """
    modules = payload.get("modules")
    if isinstance(modules, dict):
        for name, entry in modules.items():
            if isinstance(entry, dict):
                yield str(name), entry
            else:
                yield str(name), {"status": str(entry)}
        return

    # Legacy list under "results".
    raw = payload.get("results", [])
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("module") or "?"
            yield str(name), item
        return

    # Bare module map without wrapper (older fixture shape).
    if payload and all(isinstance(v, dict) and "status" in v for v in payload.values()):
        for name, entry in payload.items():
            if name in {"variant", "timestamp"}:
                continue
            if isinstance(entry, dict):
                yield str(name), entry


def failure_count(payload: Mapping[str, Any]) -> int:
    """Count modules with failed/error status."""
    count = 0
    for _, entry in iter_modules(payload):
        status = str(entry.get("status", "")).lower()
        if status in FAILURE_STATUSES:
            count += 1
    return count


def module_names(payload: Mapping[str, Any]) -> list[str]:
    """Return module names in iteration order."""
    return [name for name, _ in iter_modules(payload)]


def build_canonical(
    *,
    variant: str,
    modules: Mapping[str, Mapping[str, Any]],
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a canonical smoke-results payload for writers/tests."""
    payload: dict[str, Any] = {
        "variant": variant,
        "modules": {key: dict(value) for key, value in modules.items()},
    }
    if timestamp is not None:
        payload["timestamp"] = timestamp
    return payload


def assert_no_failures(payload: Mapping[str, Any]) -> None:
    """Raise ValueError if any module failed/errored."""
    n = failure_count(payload)
    if n:
        failed = [
            name
            for name, entry in iter_modules(payload)
            if str(entry.get("status", "")).lower() in FAILURE_STATUSES
        ]
        raise ValueError(f"{n} smoke module(s) failed: {', '.join(failed)}")


__all__ = [
    "FAILURE_STATUSES",
    "KNOWN_STATUSES",
    "assert_no_failures",
    "build_canonical",
    "failure_count",
    "is_canonical",
    "iter_modules",
    "load_smoke",
    "module_names",
]
