#!/usr/bin/env python3
"""Governance compliance checkpoints.

This script records the status of constitutional guardrails by posting evidence
to the automation API. It supports dry-run execution so contributors can review
payloads before making network requests.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

try:  # pragma: no cover - import resolution depends on invocation style
    from automation.render_client import APIError, RenderClient
except ModuleNotFoundError:  # pragma: no cover - fallback for `python path/to/script.py`
    from pathlib import Path as _Path

    sys.path.append(str(_Path(__file__).resolve().parents[1]))
    from automation.render_client import APIError, RenderClient

PRINCIPLES = [
    "template_sovereignty",
    "deterministic_generation",
    "minimal_baseline",
    "documented_scaffolds",
    "automation_governed",
]

STATUSES = ["pass", "fail", "needs_review"]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--principle", required=True, choices=PRINCIPLES, help="Governance principle.")
    parser.add_argument(
        "--status",
        required=True,
        choices=STATUSES,
        help="Checkpoint result as observed by the automation system.",
    )
    parser.add_argument("--evidence", required=True, help="Link or artifact reference supporting the status.")
    parser.add_argument("--base-url", default=None, help="Override automation API base URL.")
    parser.add_argument("--token", default=None, help="Optional bearer token for authenticated APIs.")
    parser.add_argument("--metadata", default=None, help="Path to JSON file providing additional metadata.")
    parser.add_argument("--dry-run", action="store_true", help="Do not make network requests; print payload instead.")
    return parser.parse_args(argv)


def load_metadata(path: str | None) -> Mapping[str, Any] | None:
    if not path:
        return None
    metadata_path = Path(path)
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    metadata = load_metadata(args.metadata)

    payload = {
        "principle": args.principle,
        "status": args.status,
        "evidence": args.evidence,
        "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
        "metadata": metadata or {},
    }

    if args.dry_run:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    client = RenderClient(base_url=args.base_url or RenderClient().base_url, token=args.token)
    try:
        client.record_compliance_checkpoint(
            principle=args.principle,
            status=args.status,
            evidence=args.evidence,
            metadata=payload["metadata"],
        )
    except APIError as exc:
        sys.stderr.write(f"[compliance] Failed to record checkpoint: {exc}\n")
        return 1

    sys.stdout.write("[compliance] Checkpoint recorded successfully.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
