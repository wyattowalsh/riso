#!/usr/bin/env python3
"""Execute quality suite commands for CI and emit artifacts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
DURATION_FILE = REPO_ROOT / ".riso" / "quality-durations.json"
PARITY_SCRIPT = REPO_ROOT / "scripts" / "ci" / "check_quality_parity.py"


def run_command(label: str, command: List[str], env: Dict[str, str], log_dir: Path) -> Dict[str, object]:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{label}.log"
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
    )
    log_path.write_text(result.stdout + ("\n" + result.stderr if result.stderr else ""), encoding="utf-8")
    return {
        "label": label,
        "command": command,
        "returncode": result.returncode,
        "log": str(log_path.relative_to(REPO_ROOT)),
    }


def load_durations() -> Dict[str, float]:
    if not DURATION_FILE.exists():
        return {}
    return json.loads(DURATION_FILE.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["standard", "strict"], default="standard")
    parser.add_argument("--log-dir", default="quality-artifacts")
    args = parser.parse_args()

    log_dir = (REPO_ROOT / args.log_dir).resolve()
    env = {
        "QUALITY_PROFILE": args.profile,
    }

    sync = subprocess.run(
        ["uv", "sync", "--group", "quality", "--group", "test"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    if sync.returncode != 0:
        sys.stderr.write(sync.stdout + sync.stderr)
        return sync.returncode

    results: List[Dict[str, object]] = []
    for label, command in (
        ("make-quality", ["make", "quality"]),
        ("uv-task-quality", ["uv", "run", "task", "quality"]),
    ):
        result_entry = run_command(label, command, env, log_dir)
        if result_entry["returncode"] != 0:
            sys.stderr.write(f"{label} failed; see {result_entry['log']}\n")
            results.append(result_entry)
            break
        results.append(result_entry)

    parity = subprocess.run([sys.executable, str(PARITY_SCRIPT)], cwd=REPO_ROOT)
    parity_ok = parity.returncode == 0

    payload = {
        "profile": args.profile,
        "results": results,
        "parity_passed": parity_ok,
        "quality_durations": load_durations(),
    }
    (log_dir / "quality-results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if not parity_ok:
        return parity.returncode

    for result in results:
        if result["returncode"] != 0:
            return int(result["returncode"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
