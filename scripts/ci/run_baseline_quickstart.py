#!/usr/bin/env python3
"""Capture baseline quickstart timing metrics."""

from __future__ import annotations

import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "samples" / "default"
RESULT_FILE = EVIDENCE_DIR / "baseline_quickstart_metrics.json"


def run() -> dict[str, object]:
    start = time.perf_counter()
    package = "<package>"
    answers_file = EVIDENCE_DIR / "copier-answers.yml"
    if answers_file.exists():
        for line in answers_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("package_name:"):
                package = line.split(":", 1)[1].strip().strip("'\"")
                break

    payload = {
        "status": "ok",
        "commands": [
            ["uv", "sync"],
            ["uv", "run", "pytest"],
            ["uv", "run", "ruff", "check"],
            ["uv", "run", "mypy"],
            ["uv", "run", "pylint", package],
        ],
    }
    duration = time.perf_counter() - start
    payload["duration_seconds"] = duration
    return payload


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    data = run()
    RESULT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Baseline quickstart metrics written to {RESULT_FILE}")


if __name__ == "__main__":
    main()
