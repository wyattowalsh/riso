#!/usr/bin/env python3
"""Smoke-check rendered AGENTS.md answers agent onboarding questions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

QUESTIONS: list[tuple[str, str]] = [
    ("project_identity", r"(?m)^# AGENTS\.md"),
    ("package_name", r"`[a-z][a-z0-9_]*`"),
    ("human_docs_pointer", r"README\.md"),
    ("quick_reference_table", r"\| Task \| Command \|"),
    ("boundaries_section", r"## Boundaries"),
]

MERGED_ROW_PATTERN = re.compile(r"\|\|")


def evaluate(agents_text: str) -> dict[str, object]:
    """Return pass/fail results for each smoke question."""
    checks: list[dict[str, object]] = []
    for question_id, pattern in QUESTIONS:
        matched = re.search(pattern, agents_text) is not None
        checks.append(
            {
                "id": question_id,
                "pattern": pattern,
                "passed": matched,
            }
        )

    merged_rows = MERGED_ROW_PATTERN.search(agents_text) is not None
    checks.append(
        {
            "id": "table_rows_not_merged",
            "pattern": "no '||' row merges in quick-reference table",
            "passed": not merged_rows,
        }
    )

    passed = sum(1 for check in checks if check["passed"])
    return {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "overall_passed": passed == len(checks),
    }


def main() -> int:
    """Run AGENTS.md smoke checks against a render directory."""
    parser = argparse.ArgumentParser(description="Smoke-test rendered AGENTS.md")
    parser.add_argument(
        "render_dir",
        type=Path,
        nargs="?",
        default=REPO_ROOT / "samples" / "default" / "render",
        help="Path to a Copier render directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON results",
    )
    args = parser.parse_args()

    agents_path = args.render_dir / "AGENTS.md"
    if not agents_path.is_file():
        sys.stderr.write(f"agent-smoke: missing {agents_path}\n")
        return 1

    result = evaluate(agents_path.read_text(encoding="utf-8"))
    if args.json:
        payload = {"render_dir": str(args.render_dir), **result}
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        checks = result.get("checks", [])
        if not isinstance(checks, list):
            checks = []
        for check in checks:
            if not isinstance(check, dict):
                continue
            status = "PASS" if check.get("passed") else "FAIL"
            sys.stdout.write(f"[{status}] {check.get('id', 'unknown')}\n")
        sys.stdout.write(
            f"agent-smoke: {result['passed']}/{result['total']} checks passed\n"
        )

    return 0 if result["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
