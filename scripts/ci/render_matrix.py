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
from typing import TypedDict

try:  # pragma: no cover - import behaviour depends on invocation style
    from record_module_success import ModuleSuccessRecorder
except ModuleNotFoundError:  # pragma: no cover - fallback for `python path/to/script.py`
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.append(str(_Path(__file__).resolve().parent))
    from record_module_success import ModuleSuccessRecorder


class VariantResult(TypedDict):
    """Result metadata from rendering a single variant."""
    variant: str
    answers: str
    destination: str
    smoke_results: dict[str, object] | None
    workflow_validation: str
    container_status: str


class RenderSummary(TypedDict, total=False):
    """Complete render matrix summary with all variant results."""
    variants: list[dict[str, object]]
    module_success: dict[str, object]
    quality_runs: list[dict[str, object]]
    quality_retention_days: int


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = REPO_ROOT / "samples"
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render-samples.sh"
METADATA_DIR = REPO_ROOT / "samples" / "metadata"


def discover_variants() -> list[tuple[str, Path]]:
    """Discover all sample variants by scanning for copier-answers.yml files.

    Returns:
        List of tuples containing (variant_name, answers_file_path), sorted by variant name.
    """
    variants: list[tuple[str, Path]] = []
    for answers_file in SAMPLES_DIR.glob("*/copier-answers.yml"):
        variant = answers_file.parent.name
        variants.append((variant, answers_file))
    return sorted(variants)


def load_smoke_results(answers_file: Path) -> dict[str, object] | None:
    """Load smoke test results for a rendered variant.

    Args:
        answers_file: Path to the copier-answers.yml file for the variant.

    Returns:
        Dictionary containing smoke test results, or None if results file doesn't exist.
    """
    log_path = answers_file.parent / "smoke-results.json"
    if not log_path.exists():
        return None
    return json.loads(log_path.read_text(encoding="utf-8"))


def load_post_gen_metadata(answers_file: Path) -> dict[str, object] | None:
    """Load post-generation metadata including workflow validation status."""
    render_dir = answers_file.parent / "render"
    metadata_path = render_dir / ".riso" / "post_gen_metadata.json"
    if not metadata_path.exists():
        return None
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def render_variant(variant: str, answers_file: Path) -> VariantResult:
    """Render a single variant and collect metadata about the render.

    Args:
        variant: Name of the variant to render.
        answers_file: Path to the copier-answers.yml file for the variant.

    Returns:
        Dictionary containing variant metadata including smoke results, workflow validation
        status, and container validation status.

    Raises:
        subprocess.CalledProcessError: If the render script fails.
    """
    destination = answers_file.parent / "render"
    cmd = [str(RENDER_SCRIPT), "--variant", variant, "--answers", str(answers_file)]
    env = {**os.environ, "COPIER_CMD": os.environ.get("COPIER_CMD", "copier")}
    subprocess.run(cmd, check=True, cwd=REPO_ROOT, env=env)
    
    metadata = load_post_gen_metadata(answers_file)
    workflow_status = "unknown"
    container_status = "not_applicable"
    
    if metadata:
        workflow_status = metadata.get("workflow_validation", "unknown")
        
        # Check if variant should have container support
        answers_data = {}
        if answers_file.exists():
            try:
                import yaml
                with open(answers_file, encoding="utf-8") as f:
                    answers_data = yaml.safe_load(f) or {}
            except (ImportError, OSError) as e:
                # YAML module not available or file read error - skip container checks
                sys.stderr.write(f"Warning: Could not load answers file {answers_file}: {e}\n")
            except Exception as e:
                # Catch yaml.YAMLError and other YAML parsing errors
                # Can't import yaml.YAMLError without yaml being available
                sys.stderr.write(f"Warning: Failed to parse YAML from {answers_file}: {e}\n")
        
        api_tracks = answers_data.get("api_tracks", "none")
        docs_site = answers_data.get("docs_site", "none")
        
        # Container support enabled for API or docs projects
        has_containers = api_tracks in ["python", "node", "python+node"] or docs_site == "fumadocs"
        
        if has_containers:
            # Validate container files exist
            docker_file = destination / ".docker" / "Dockerfile"
            compose_file = destination / "docker-compose.yml"
            
            if docker_file.exists() and compose_file.exists():
                container_status = "files_present"
                
                # Optional: Run hadolint validation
                try:
                    with docker_file.open("rb") as f:
                        hadolint_result = subprocess.run(
                            ["docker", "run", "--rm", "-i", "hadolint/hadolint"],
                            stdin=f,
                            capture_output=True,
                            timeout=30,
                        )
                    if hadolint_result.returncode == 0:
                        container_status = "validated"
                    else:
                        container_status = "lint_errors"
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    # hadolint not available or timeout, keep files_present status
                    pass
            else:
                container_status = "files_missing"
        else:
            container_status = "not_applicable"

    return VariantResult(
        variant=variant,
        answers=str(answers_file),
        destination=str(destination),
        smoke_results=load_smoke_results(answers_file),
        workflow_validation=workflow_status,
        container_status=container_status,
    )


def main() -> None:
    """Orchestrate rendering of all discovered variants and aggregate metadata.

    Command-line arguments:
        --skip-render: Skip rendering and reuse existing render_matrix.json if available.
        --quality-artifacts: List of paths to quality run artifact JSON files.
        --retention-days: Number of days to retain quality artifacts (default: 90).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--quality-artifacts", nargs="*", default=[])
    parser.add_argument("--retention-days", type=int, default=90)
    args = parser.parse_args()

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = METADATA_DIR / "render_matrix.json"

    if args.skip_render and output_file.exists():
        summary: RenderSummary = json.loads(output_file.read_text(encoding="utf-8"))
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
        summary: RenderSummary = {"variants": []}
        recorder = ModuleSuccessRecorder()

        for variant, answers_file in discover_variants():
            variant_summary = render_variant(variant, answers_file)
            summary["variants"].append(variant_summary)
            
            # Track workflow validation status
            workflow_status = variant_summary.get("workflow_validation", "unknown")
            recorder.update_workflow_validation(workflow_status)
            
            # Track container validation status
            container_status = variant_summary.get("container_status", "not_applicable")
            recorder.update_container_status(container_status)
            
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
