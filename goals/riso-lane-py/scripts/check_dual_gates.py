#!/usr/bin/env python3
"""Structural check: GraphQL/WebSocket python payload files carry dual-gates.

Drives the real template tree under template/files/python (no reimplementation of
Copier). Exit 0 when every graphql_api / websocket jinja file mentions the legacy
module flag or api_features in its opening section; exit 1 with paths otherwise.

Usage (from repo root):
    uv run python goals/riso-lane-py/scripts/check_dual_gates.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "template" / "files" / "python").is_dir():
            return parent
    raise SystemExit("Could not locate repo root containing template/files/python")


def head(text: str, n: int = 400) -> str:
    return text[:n]


def main() -> int:
    root = repo_root() / "template" / "files" / "python"
    if not root.is_dir():
        print(f"missing tree: {root}", file=sys.stderr)
        return 1

    missing: list[str] = []
    checked = 0
    for path in sorted(root.rglob("*.jinja")):
        rel_parts = path.relative_to(root).parts
        is_gql = "graphql_api" in rel_parts
        is_ws = "websocket" in rel_parts or path.name == "websocket_endpoints.py.jinja"
        if not (is_gql or is_ws):
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        h = head(text)
        if is_gql and ("graphql_api_module" not in h and "api_features" not in h):
            missing.append(str(path.relative_to(repo_root())))
        if is_ws and ("websocket_module" not in h and "api_features" not in h):
            missing.append(str(path.relative_to(repo_root())))

    if checked == 0:
        print("no graphql/websocket jinja files found", file=sys.stderr)
        return 1

    if missing:
        print(f"dual-gate gaps ({len(missing)}/{checked}):", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1

    print(f"dual-gates ok: checked {checked} graphql/websocket jinja files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
