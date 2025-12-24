#!/usr/bin/env python3
"""Aggregate module success metrics from sample smoke logs."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, MutableMapping


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

    def to_dict(self) -> dict[str, float | int]:
        data = asdict(self)
        data["success_rate"] = round(self.success_rate(), 4)
        data["total_recorded"] = self.total()
        return data


@dataclass
class CacheMetrics:
    cache_hit_rate: float = 0.0
    average_runtime_with_cache_seconds: float | None = None
    average_runtime_without_cache_seconds: float | None = None
    cache_efficiency_ratio: float | None = None
    total_cache_checks: int = 0
    note: str = "Cache metrics tracked from GitHub Actions workflow runs when ci_platform=github-actions"

    def to_dict(self) -> dict[str, float | int | str | None]:
        return asdict(self)


@dataclass
class ContainerMetrics:
    total_checked: int = 0
    files_present: int = 0
    validated: int = 0
    lint_errors: int = 0
    files_missing: int = 0
    not_applicable: int = 0
    success_rate: float = 0.0
    note: str = "Container metrics tracked from rendered samples with api_tracks or docs_site"

    def to_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


class ModuleSuccessRecorder:
    """Tracks module-level success metrics across rendered variants."""

    def __init__(self) -> None:
        self.modules: dict[str, ModuleStats] = {}
        self.variants: list[dict[str, object]] = []
        self.workflow_stats = ModuleStats()
        self.cache_metrics = CacheMetrics()
        self.container_metrics = ContainerMetrics()

    def record(self, module_name: str, status: str, variant: str) -> None:
        """Helper method to record a single module result.

        Args:
            module_name: Name of the module
            status: Status of the result (passed, failed, error, skipped)
            variant: Variant name for tracking
        """
        results = [{"name": module_name, "status": status}]
        self.update_from_results(variant, results)

    def update_workflow_validation(self, status: str) -> None:
        """Track workflow validation status."""
        if status == "pass":
            self.workflow_stats.passed += 1
        elif status == "fail":
            self.workflow_stats.failed += 1
        else:
            self.workflow_stats.skipped += 1
    
    def update_container_status(self, status: str) -> None:
        """Track container validation status."""
        self.container_metrics.total_checked += 1
        
        if status == "files_present":
            self.container_metrics.files_present += 1
        elif status == "validated":
            self.container_metrics.validated += 1
        elif status == "lint_errors":
            self.container_metrics.lint_errors += 1
        elif status == "files_missing":
            self.container_metrics.files_missing += 1
        elif status == "not_applicable":
            self.container_metrics.not_applicable += 1
        
        # Calculate success rate (validated / (total - not_applicable))
        applicable = self.container_metrics.total_checked - self.container_metrics.not_applicable
        if applicable > 0:
            self.container_metrics.success_rate = round(
                self.container_metrics.validated / applicable, 4
            )

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

    def to_dict(self) -> dict[str, object]:
        workflow_data: dict[str, object] = dict(self.workflow_stats.to_dict())
        workflow_data["ci_cache_performance"] = self.cache_metrics.to_dict()
        workflow_data["container_validation"] = self.container_metrics.to_dict()
        
        return {
            "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
            "modules": {name: stats.to_dict() for name, stats in self.modules.items()},
            "workflow_generation": workflow_data,
            "variants": self.variants,
        }

    def write(self, destination: Path) -> dict[str, object]:
        payload = self.to_dict()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload


def iter_smoke_logs(samples_dir: Path) -> Iterable[tuple[str, list[MutableMapping[str, object]]]]:
    for answers_file in sorted(samples_dir.glob("*/smoke-results.json")):
        variant = answers_file.parent.name
        data = json.loads(answers_file.read_text(encoding="utf-8"))
        results = data.get("results", [])
        yield variant, list(results)


def update_support_ticket_metrics(destination: Path) -> None:
    path = destination.parent / "support_tickets.json"
    baseline = {
        "quality_tooling_setup": {
            "tickets_last_30_days": 0,
            "variance_percent": 0.0,
            "notes": "Updated by record_module_success.py",
        }
    }
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = baseline
    else:
        payload = baseline
    payload.setdefault("quality_tooling_setup", baseline["quality_tooling_setup"])
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


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

    result_path = Path(args.output)
    recorder.write(result_path)
    update_support_ticket_metrics(result_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
