#!/usr/bin/env python3
"""Aggregate module success metrics from sample smoke logs."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, MutableMapping


@dataclass
class ModuleStats:
    passed: int = 0
    failed: int = 0
    errored: int = 0
    skipped: int = 0

    def total(self) -> int:
        return self.passed + self.failed + self.errored

    def success_rate(self) -> float:
        total = self.total()
        return 0.0 if total == 0 else self.passed / total

    def to_dict(self) -> Dict[str, float | int]:
        data = asdict(self)
        data["success_rate"] = round(self.success_rate(), 4)
        data["total_recorded"] = self.total()
        return data


class ModuleSuccessRecorder:
    """Tracks module-level success metrics across rendered variants."""

    def __init__(self) -> None:
        self.modules: Dict[str, ModuleStats] = {}
        self.variants: List[Dict[str, object]] = []

    def update_from_results(self, variant: str, results: Iterable[MutableMapping[str, object]]) -> None:
        variant_summary = {"variant": variant, "results": []}
        for entry in results:
            name = str(entry.get("name", "unknown"))
            status = str(entry.get("status", "skipped"))
            record = self.modules.setdefault(name, ModuleStats())

            if status == "passed":
                record.passed += 1
            elif status == "failed":
                record.failed += 1
            elif status == "error":
                record.errored += 1
            else:
                record.skipped += 1

            variant_summary["results"].append(
                {
                    "name": name,
                    "status": status,
                }
            )
        self.variants.append(variant_summary)

    def to_dict(self) -> Dict[str, object]:
        return {
            "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
            "modules": {name: stats.to_dict() for name, stats in self.modules.items()},
            "variants": self.variants,
        }

    def write(self, destination: Path) -> Dict[str, object]:
        payload = self.to_dict()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload


def iter_smoke_logs(samples_dir: Path) -> Iterable[tuple[str, List[MutableMapping[str, object]]]]:
    for answers_file in sorted(samples_dir.glob("*/smoke-results.json")):
        variant = answers_file.parent.name
        data = json.loads(answers_file.read_text(encoding="utf-8"))
        results = data.get("results", [])
        yield variant, list(results)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples-dir", default="samples", help="Directory containing rendered sample variants.")
    parser.add_argument(
        "--output",
        default="samples/metadata/module_success.json",
        help="Destination for aggregated module success metrics.",
    )
    args = parser.parse_args(argv)

    samples_dir = Path(args.samples_dir)
    recorder = ModuleSuccessRecorder()

    for variant, results in iter_smoke_logs(samples_dir):
        recorder.update_from_results(variant, results)

    recorder.write(Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
