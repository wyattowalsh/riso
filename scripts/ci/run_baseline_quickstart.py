#!/usr/bin/env python3
"""Record baseline quickstart evidence without fabricating command success."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from scripts.lib.paths import repo_root  # noqa: E402

REPO_ROOT = repo_root()

try:
    from scripts.lib.logger import configure_logging, logger
except ModuleNotFoundError:
    scripts_dir = REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from lib.logger import configure_logging, logger

EVIDENCE_DIR = REPO_ROOT / "samples" / "default"
RESULT_FILE = EVIDENCE_DIR / "baseline_quickstart_metrics.json"


def run() -> dict[str, object]:
    """Build a neutral metrics payload (no sham mypy/ok status)."""
    package = "<package>"
    answers_file = EVIDENCE_DIR / "copier-answers.yml"
    if answers_file.exists():
        for line in answers_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("package_name:"):
                package = line.split(":", 1)[1].strip().strip("'\"")
                break

    return {
        "status": "not_executed",
        "note": (
            "Baseline quickstart timings are not simulated here. "
            "Use render/smoke automation and local `just quality` for evidence."
        ),
        "package_name": package,
        "documented_commands": [
            ["uv", "sync"],
            ["uv", "run", "pytest"],
            ["uv", "run", "ruff", "check"],
            ["uv", "run", "ty", "check", f"src/{package}"],
            ["uv", "run", "pylint", package, "tests"],
        ],
    }


def main() -> None:
    configure_logging()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    data = run()
    RESULT_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Baseline quickstart metrics written to %s", RESULT_FILE)


if __name__ == "__main__":
    main()
