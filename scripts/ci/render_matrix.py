#!/usr/bin/env python3
"""Render matrix orchestration for the Riso template.

The script discovers sample variants in ``samples/*/copier-answers.yml`` and
invokes ``scripts/render-samples.sh`` for each one. It records metadata that
other CI helpers (success-rate recorder, doc tracker) can consume.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:  # pragma: no cover - import behaviour depends on invocation style
    from record_module_success import ModuleSuccessRecorder
except ModuleNotFoundError:  # pragma: no cover - fallback for `python path/to/script.py`
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.append(str(_Path(__file__).resolve().parent))
    from record_module_success import ModuleSuccessRecorder

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = REPO_ROOT / "samples"
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render-samples.sh"
METADATA_DIR = REPO_ROOT / "samples" / "metadata"


def discover_variants() -> list[tuple[str, Path]]:
    variants: list[tuple[str, Path]] = []
    for answers_file in SAMPLES_DIR.glob("*/copier-answers.yml"):
        variant = answers_file.parent.name
        variants.append((variant, answers_file))
    return sorted(variants)


def load_smoke_results(answers_file: Path) -> dict[str, object] | None:
    log_path = answers_file.parent / "smoke-results.json"
    if not log_path.exists():
        return None
    return json.loads(log_path.read_text(encoding="utf-8"))


def render_variant(variant: str, answers_file: Path) -> dict[str, object]:
    destination = answers_file.parent / "render"
    cmd = [str(RENDER_SCRIPT), "--variant", variant, "--answers", str(answers_file)]
    env = {**os.environ, "COPIER_CMD": os.environ.get("COPIER_CMD", "copier")}
    subprocess.run(cmd, check=True, cwd=REPO_ROOT, env=env)
    return {
        "variant": variant,
        "answers": str(answers_file),
        "destination": str(destination),
        "smoke_results": load_smoke_results(answers_file),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--quality-artifacts", nargs="*", default=[])
    parser.add_argument("--retention-days", type=int, default=90)
    args = parser.parse_args()

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = METADATA_DIR / "render_matrix.json"

    if args.skip_render and output_file.exists():
        summary = json.loads(output_file.read_text(encoding="utf-8"))
        recorder = ModuleSuccessRecorder()
        for variant_entry in summary.get("variants", []):
            results = variant_entry.get("smoke_results", {})
            if results:
                recorder.update_from_results(
                    variant_entry.get("variant", "unknown"),
                    results.get("results", []),  # type: ignore[arg-type]
                )
        module_metrics = recorder.write(METADATA_DIR / "module_success.json")
        summary["module_success"] = module_metrics
    else:
        summary: dict[str, object] = {"variants": []}
        recorder = ModuleSuccessRecorder()

        for variant, answers_file in discover_variants():
            variant_summary = render_variant(variant, answers_file)
            summary["variants"].append(variant_summary)
            smoke_results = variant_summary.get("smoke_results")
            if smoke_results:
                recorder.update_from_results(
                    variant_summary["variant"],
                    smoke_results.get("results", []),  # type: ignore[arg-type]
                )

        module_metrics = recorder.write(METADATA_DIR / "module_success.json")
        summary["module_success"] = module_metrics

    if args.quality_artifacts:
        quality_runs: list[dict[str, object]] = []
        for artifact in args.quality_artifacts:
            path = Path(artifact)
            if not path.exists():
                continue
            quality_runs.append(json.loads(path.read_text(encoding="utf-8")))
        if quality_runs:
            summary["quality_runs"] = quality_runs
            summary["quality_retention_days"] = args.retention_days

    output_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Render matrix complete. Metadata saved to {output_file}")


if __name__ == "__main__":
    if not RENDER_SCRIPT.exists():
        sys.stderr.write("render-samples.sh not found; run from repository root.\n")
        sys.exit(1)
    main()
