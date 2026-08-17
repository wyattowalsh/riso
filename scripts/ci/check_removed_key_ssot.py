#!/usr/bin/env python3
"""Check 3-way removed-key SSOT parity (core, scripts.lib fallback, web TS).

Compares ``REMOVED_ANSWER_KEYS`` (replacement prose) and ``ANSWER_KEY_REMAPS``
(old, new_keys, action) across:

* ``src/riso/core/removed_answer_keys.py``
* ``scripts/lib/removed_answer_keys.py`` (``_FALLBACK_*`` twin)
* ``web/src/lib/removedAnswerKeys.ts``

scripts.lib public names rebind to the packaged SSOT when ``riso`` is
importable; this gate always reads the local fallback tables.

Exit codes:
    0 - three-way key+op parity
    1 - drift, parse error, or missing surface
"""

from __future__ import annotations

import importlib
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = REPO_ROOT / "src" / "riso" / "core" / "removed_answer_keys.py"
_SCRIPTS_DIR = str(REPO_ROOT / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
LIB_PATH = REPO_ROOT / "scripts" / "lib" / "removed_answer_keys.py"
TS_PATH = REPO_ROOT / "web" / "src" / "lib" / "removedAnswerKeys.ts"
TASKGRAPH_PATH = REPO_ROOT / "goals" / "riso-v2-release-ready" / "plan.taskgraph.json"

EXPECTED_KEYS = (
    "api_tracks",
    "api_language",
    "docs_site",
    "mcp_language",
    "saas_starter_module",
    "saas_auth",
    "saas_billing",
    "include_admin",
)
ALLOWED_ACTIONS = frozenset({"wrap-list", "derive", "rename", "split", "rename-bool"})
CANONICAL_OPS: dict[str, tuple[str, tuple[str, ...], str]] = {
    "api_tracks": ("api_tracks", ("api_module", "api_languages"), "derive"),
    "api_language": ("api_language", ("api_languages",), "wrap-list"),
    "docs_site": ("docs_site", ("docs_module", "docs_framework"), "derive"),
    "mcp_language": ("mcp_language", ("mcp_languages",), "wrap-list"),
    "saas_starter_module": ("saas_starter_module", ("saas_infra_module",), "rename"),
    "saas_auth": ("saas_auth", ("saas_auth_module", "saas_auth_provider"), "split"),
    "saas_billing": (
        "saas_billing",
        ("saas_billing_module", "saas_billing_provider"),
        "split",
    ),
    "include_admin": ("include_admin", ("saas_admin_dashboard",), "rename-bool"),
}

_TS_KV = re.compile(
    r"""(?P<key>[A-Za-z_][\w]*)\s*:\s*'(?P<val>(?:\\'|[^'])*)'""",
)
_TS_REMAP = re.compile(
    r"""
    (?P<key>[A-Za-z_][\w]*)\s*:\s*\{
    (?P<body>[^{}]+)
    \}
    """,
    re.VERBOSE | re.DOTALL,
)
_TS_OLD = re.compile(r"old\s*:\s*'(?P<old>[^']+)'")
_TS_ACTION = re.compile(r"action\s*:\s*'(?P<action>[^']+)'")
_TS_NEW_KEYS = re.compile(r"new_keys\s*:\s*\[(?P<items>[^\]]*)\]")
_TS_STR = re.compile(r"'([^']+)'")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def remap_payload(
    table: Mapping[str, Any],
) -> dict[str, tuple[str, tuple[str, ...], str]]:
    """Normalize a remap table to ``{key: (old, new_keys, action)}``."""
    out: dict[str, tuple[str, tuple[str, ...], str]] = {}
    for key, spec in table.items():
        if isinstance(spec, Mapping):
            old = str(spec["old"])
            new_keys = tuple(spec["new_keys"])
            action = str(spec["action"])
        else:
            old = str(spec.old)
            new_keys = tuple(spec.new_keys)
            action = str(spec.action)
        out[str(key)] = (old, new_keys, action)
    return out


def load_core() -> tuple[dict[str, str], dict[str, tuple[str, tuple[str, ...], str]]]:
    from riso.core.removed_answer_keys import ANSWER_KEY_REMAPS, REMOVED_ANSWER_KEYS

    return dict(REMOVED_ANSWER_KEYS), remap_payload(ANSWER_KEY_REMAPS)


def load_scripts_fallback() -> tuple[
    dict[str, str], dict[str, tuple[str, tuple[str, ...], str]]
]:
    scripts_dir = str(REPO_ROOT / "scripts")
    inserted = False
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
        inserted = True
    saved = {name: sys.modules.get(name) for name in ("lib", "lib.removed_answer_keys")}
    try:
        for name in saved:
            sys.modules.pop(name, None)
        mod = importlib.import_module("lib.removed_answer_keys")
        keys = getattr(mod, "_FALLBACK_REMOVED_ANSWER_KEYS", None)
        remaps = getattr(mod, "_FALLBACK_ANSWER_KEY_REMAPS", None)
        if not isinstance(keys, dict) or remaps is None:
            raise RuntimeError(
                "scripts/lib twin missing _FALLBACK_REMOVED_ANSWER_KEYS "
                "or _FALLBACK_ANSWER_KEY_REMAPS"
            )
        return dict(keys), remap_payload(remaps)
    finally:
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
        if inserted and scripts_dir in sys.path:
            sys.path.remove(scripts_dir)


def _extract_ts_object(text: str, name: str) -> str:
    marker = f"export const {name}"
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"{name} export not found in {_rel(TS_PATH)}")
    brace = text.find("{", start)
    if brace < 0:
        raise ValueError(f"{name} object brace not found in {_rel(TS_PATH)}")
    depth = 0
    for index, char in enumerate(text[brace:], start=brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1 : index]
    raise ValueError(f"{name} object not closed in {_rel(TS_PATH)}")


def parse_ts_ssot(
    text: str,
) -> tuple[dict[str, str], dict[str, tuple[str, tuple[str, ...], str]]]:
    keys: dict[str, str] = {}
    for match in _TS_KV.finditer(_extract_ts_object(text, "REMOVED_ANSWER_KEYS")):
        keys[match.group("key")] = match.group("val").replace(r"\'", "'")

    remaps: dict[str, tuple[str, tuple[str, ...], str]] = {}
    for match in _TS_REMAP.finditer(_extract_ts_object(text, "ANSWER_KEY_REMAPS")):
        body = match.group("body")
        old_match = _TS_OLD.search(body)
        action_match = _TS_ACTION.search(body)
        new_match = _TS_NEW_KEYS.search(body)
        if old_match is None or action_match is None or new_match is None:
            raise ValueError(
                f"incomplete remap row {match.group('key')!r} in {_rel(TS_PATH)}"
            )
        remaps[match.group("key")] = (
            old_match.group("old"),
            tuple(_TS_STR.findall(new_match.group("items"))),
            action_match.group("action"),
        )
    return keys, remaps


def load_ts() -> tuple[dict[str, str], dict[str, tuple[str, tuple[str, ...], str]]]:
    return parse_ts_ssot(TS_PATH.read_text(encoding="utf-8"))


def load_plan_remap_keys() -> tuple[str, ...] | None:
    if not TASKGRAPH_PATH.is_file():
        return None
    payload = json.loads(TASKGRAPH_PATH.read_text(encoding="utf-8"))
    keys = payload.get("remap_keys")
    if not isinstance(keys, list) or not all(isinstance(item, str) for item in keys):
        raise ValueError(f"{_rel(TASKGRAPH_PATH)} remap_keys must be a string list")
    return tuple(keys)


def _fmt_ops(ops: dict[str, tuple[str, tuple[str, ...], str]]) -> str:
    lines = []
    for key in EXPECTED_KEYS:
        if key not in ops:
            lines.append(f"    {key}: <missing>")
            continue
        old, new_keys, action = ops[key]
        dests = ", ".join(new_keys)
        lines.append(f"    {old}: {action} -> {dests}")
    extras = sorted(set(ops) - set(EXPECTED_KEYS))
    for key in extras:
        old, new_keys, action = ops[key]
        dests = ", ".join(new_keys)
        lines.append(f"    {old}: {action} -> {dests}  [extra]")
    return "\n".join(lines)


def check_surface(
    label: str,
    keys: Mapping[str, str],
    ops: Mapping[str, tuple[str, tuple[str, ...], str]],
) -> list[str]:
    errors: list[str] = []
    key_set = set(keys)
    expected = set(EXPECTED_KEYS)
    if key_set != expected:
        missing = sorted(expected - key_set)
        extra = sorted(key_set - expected)
        errors.append(
            f"{label} REMOVED_ANSWER_KEYS key set drift missing={missing} extra={extra}"
        )
    if set(ops) != set(keys):
        errors.append(
            f"{label} ANSWER_KEY_REMAPS keys {sorted(ops)} "
            f"!= REMOVED_ANSWER_KEYS keys {sorted(keys)}"
        )
    if len(keys) != 8:
        errors.append(f"{label} expected 8 removed keys, found {len(keys)}")
    if dict(ops) != CANONICAL_OPS:
        errors.append(f"{label} remap ops do not match the apply-then-reject contract")
        errors.append(f"{label} ops:\n{_fmt_ops(dict(ops))}")
    for key, spec in ops.items():
        _old, _new_keys, action = spec
        if action not in ALLOWED_ACTIONS:
            errors.append(f"{label} {key}: unknown action {action!r}")
    return errors


def compare_three_way(
    core_keys: Mapping[str, str],
    core_ops: Mapping[str, tuple[str, tuple[str, ...], str]],
    lib_keys: Mapping[str, str],
    lib_ops: Mapping[str, tuple[str, tuple[str, ...], str]],
    ts_keys: Mapping[str, str],
    ts_ops: Mapping[str, tuple[str, tuple[str, ...], str]],
) -> list[str]:
    errors: list[str] = []
    if dict(core_keys) != dict(lib_keys):
        errors.append("REMOVED_ANSWER_KEYS drift: core vs scripts.lib fallback")
        for key in sorted(set(core_keys) | set(lib_keys)):
            if core_keys.get(key) != lib_keys.get(key):
                errors.append(
                    f"  {key}: core={core_keys.get(key)!r} lib={lib_keys.get(key)!r}"
                )
    if dict(core_keys) != dict(ts_keys):
        errors.append("REMOVED_ANSWER_KEYS drift: core vs web TS")
        for key in sorted(set(core_keys) | set(ts_keys)):
            if core_keys.get(key) != ts_keys.get(key):
                errors.append(
                    f"  {key}: core={core_keys.get(key)!r} ts={ts_keys.get(key)!r}"
                )
    if dict(core_ops) != dict(lib_ops):
        errors.append("ANSWER_KEY_REMAPS drift: core vs scripts.lib fallback")
        errors.append(f"  core:\n{_fmt_ops(dict(core_ops))}")
        errors.append(f"  lib:\n{_fmt_ops(dict(lib_ops))}")
    if dict(core_ops) != dict(ts_ops):
        errors.append("ANSWER_KEY_REMAPS drift: core vs web TS")
        errors.append(f"  core:\n{_fmt_ops(dict(core_ops))}")
        errors.append(f"  ts:\n{_fmt_ops(dict(ts_ops))}")
    return errors


def scan_sample_answers_for_removed_keys() -> list[str]:
    """Fail if any official sample answers file still has a removed YAML key."""
    from lib.paths import (  # pylint: disable=import-error
        iter_sample_answer_files,
        samples_dir,
    )
    from riso.core.removed_answer_keys import REMOVED_ANSWER_KEYS

    try:
        import yaml
    except ModuleNotFoundError:
        return ["PyYAML is required to scan sample answers"]

    errors: list[str] = []
    for path in iter_sample_answer_files(samples_dir()):
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"{_rel(path)}: cannot parse ({exc})")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{_rel(path)}: answers root must be a mapping")
            continue
        leftovers = sorted(set(payload) & set(REMOVED_ANSWER_KEYS))
        if leftovers:
            errors.append(f"{_rel(path)}: leftover removed keys {leftovers}")
    return errors


def main() -> int:
    print("check_removed_key_ssot: 3-way key+op parity")
    print(f"  core:   {_rel(CORE_PATH)}")
    print(f"  twin:   {_rel(LIB_PATH)} (_FALLBACK_*)")
    print(f"  wizard: {_rel(TS_PATH)}")
    print()

    missing = [path for path in (CORE_PATH, LIB_PATH, TS_PATH) if not path.is_file()]
    if missing:
        for path in missing:
            print(f"error: missing SSOT file {_rel(path)}", file=sys.stderr)
        return 1

    try:
        core_keys, core_ops = load_core()
        lib_keys, lib_ops = load_scripts_fallback()
        ts_keys, ts_ops = load_ts()
        plan_keys = load_plan_remap_keys()
        leftover_errors = scan_sample_answers_for_removed_keys()
    except (
        OSError,
        ValueError,
        RuntimeError,
        ImportError,
        json.JSONDecodeError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    errors.extend(check_surface("core", core_keys, core_ops))
    errors.extend(check_surface("scripts.lib", lib_keys, lib_ops))
    errors.extend(check_surface("web TS", ts_keys, ts_ops))
    errors.extend(
        compare_three_way(core_keys, core_ops, lib_keys, lib_ops, ts_keys, ts_ops)
    )
    if plan_keys is not None and tuple(plan_keys) != EXPECTED_KEYS:
        errors.append(
            f"plan.taskgraph.json remap_keys {list(plan_keys)} "
            f"!= expected {list(EXPECTED_KEYS)}"
        )
    errors.extend(leftover_errors)

    print(f"keys ({len(core_keys)}): {', '.join(EXPECTED_KEYS)}")
    print("ops (core):")
    print(_fmt_ops(dict(core_ops)))
    print()

    if errors:
        print("FAIL: 3-way key+op parity", file=sys.stderr)
        for item in errors:
            print(item, file=sys.stderr)
        return 1

    print("ok: 3-way key+op parity (core == scripts.lib fallback == web TS)")
    print("ok: sample copier-answers.yml files have zero removed keys")
    return 0


if __name__ == "__main__":
    sys.exit(main())
