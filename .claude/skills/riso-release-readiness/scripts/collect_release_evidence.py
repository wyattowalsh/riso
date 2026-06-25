#!/usr/bin/env python3
"""Collect a compact release-readiness evidence summary."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
TODO = ROOT / "tmp" / "riso-prod-ready-release-todo.md"
SPEC = ROOT / "specs" / "016-prod-release-readiness"


def main() -> None:
    evidence = {
        "todo_exists": TODO.exists(),
        "spec_files": sorted(
            str(path.relative_to(ROOT)) for path in SPEC.rglob("*") if path.is_file()
        ),
        "skill_source": ".agents/skills/riso-release-readiness",
        "skill_mirror": ".claude/skills/riso-release-readiness",
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
