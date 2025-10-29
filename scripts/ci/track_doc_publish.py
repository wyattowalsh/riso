#!/usr/bin/env python3
"""Track documentation publish timestamps for governance automation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def load_existing(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, help="Documentation site identifier (e.g., shibuya, fumadocs).")
    parser.add_argument(
        "--status",
        default="unknown",
        choices=["pass", "fail", "pending", "unknown"],
        help="Publish status recorded for the site.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Optional build duration in seconds to support SLA tracking.",
    )
    parser.add_argument(
        "--output",
        default="samples/metadata/doc_publish.json",
        help="File used to persist publish history.",
    )
    parser.add_argument("--notes", default=None, help="Optional notes or remediation guidance.")
    args = parser.parse_args(argv)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    records = load_existing(output)
    records.append(
        {
            "site": args.site,
            "status": args.status,
            "duration_seconds": args.duration,
            "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
            "notes": args.notes,
        }
    )
    output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
