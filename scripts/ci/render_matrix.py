#!/usr/bin/env python3
"""Render matrix orchestration for the Riso template.

The script discovers sample variants via ``samples/**/copier-answers.yml`` and
invokes ``scripts/render-samples.sh`` for each one. Nested trees keep a path
relative to ``samples/`` (dest is ``<answers_dir>/render``). It records metadata
that other CI helpers (success-rate recorder, doc tracker) can consume.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import TypedDict, cast

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

try:
    from scripts.lib.paths import iter_sample_answer_files, repo_root  # noqa: E402
except ModuleNotFoundError:  # pragma: no cover
    scripts_dir = _REPO / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from lib.paths import iter_sample_answer_files, repo_root  # type: ignore[no-redef]  # noqa: E402

REPO_ROOT = repo_root()

try:
    from scripts.lib.logger import configure_logging, logger
except ModuleNotFoundError:
    scripts_dir = REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from lib.logger import configure_logging, logger

try:  # pragma: no cover - import behaviour depends on invocation style
    from record_module_success import (
        ModuleResult,
        ModuleSuccessRecorder,
        smoke_payload_to_results,
    )
except (
    ModuleNotFoundError
):  # pragma: no cover - fallback for `python path/to/script.py`
    sys.path.append(str(Path(__file__).resolve().parent))
    from record_module_success import (
        ModuleResult,
        ModuleSuccessRecorder,
        smoke_payload_to_results,
    )


def _module_results(payload: dict[str, object]) -> list[ModuleResult]:
    return smoke_payload_to_results(payload)


class VariantResult(TypedDict, total=False):
    """Result metadata from rendering a single variant."""

    variant: str
    answers: str
    destination: str
    smoke_results: dict[str, object] | None
    workflow_validation: str
    container_status: str
    render_status: str
    render_returncode: int


class RenderSummary(TypedDict, total=False):
    """Complete render matrix summary with all variant results."""

    variants: list[VariantResult]
    module_success: dict[str, object]
    quality_runs: list[dict[str, object]]
    quality_retention_days: int


SAMPLES_DIR = REPO_ROOT / "samples"
RENDER_SCRIPT = REPO_ROOT / "scripts" / "render-samples.sh"
METADATA_DIR = REPO_ROOT / "samples" / "metadata"


def _is_discoverable_answers(answers_file: Path) -> bool:
    """Return True when *answers_file* is a sample answers file, not metadata/render."""
    try:
        rel = answers_file.parent.relative_to(SAMPLES_DIR)
    except ValueError:
        return False
    return "render" not in rel.parts and "metadata" not in rel.parts


def discover_variants() -> list[tuple[str, Path]]:
    """Discover sample variants by scanning for ``copier-answers.yml`` files.

    Nested trees (for example ``samples/saas-starter/vercel-starter/``) keep a
    path relative to ``samples/`` so dest stays ``<answers_dir>/render``.

    Returns:
        List of tuples containing (variant_name, answers_file_path), sorted by variant name.
    """
    variants: list[tuple[str, Path]] = []
    if not SAMPLES_DIR.is_dir():
        return variants
    for answers_file in iter_sample_answer_files(SAMPLES_DIR):
        if not _is_discoverable_answers(answers_file):
            continue
        variant = answers_file.parent.relative_to(SAMPLES_DIR).as_posix()
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
        status, and container validation status. Render script failures are recorded rather
        than aborting the full matrix so remaining variants still run.
    """
    destination = answers_file.parent / "render"
    cmd = [str(RENDER_SCRIPT), "--variant", variant, "--answers", str(answers_file)]
    env = {**os.environ, "COPIER_CMD": os.environ.get("COPIER_CMD", "copier")}
    completed = subprocess.run(cmd, check=False, cwd=REPO_ROOT, env=env)
    render_status = "ok" if completed.returncode == 0 else "failed"
    if completed.returncode != 0:
        logger.error(
            "Render script failed for variant {} (exit {}); continuing matrix",
            variant,
            completed.returncode,
        )

    metadata = load_post_gen_metadata(answers_file)
    workflow_status = "unknown"
    container_status = "not_applicable"

    if metadata:
        workflow_status = str(metadata.get("workflow_validation", "unknown"))

        # Check if variant should have container support
        answers_data = {}
        if answers_file.exists():
            try:
                import yaml

                with open(answers_file, encoding="utf-8") as f:
                    answers_data = yaml.safe_load(f) or {}
            except (ImportError, OSError) as e:
                # YAML module not available or file read error - skip container checks
                sys.stderr.write(
                    f"Warning: Could not load answers file {answers_file}: {e}\n"
                )
            except Exception as e:
                # Catch yaml.YAMLError and other YAML parsing errors
                # Can't import yaml.YAMLError without yaml being available
                sys.stderr.write(
                    f"Warning: Failed to parse YAML from {answers_file}: {e}\n"
                )

        api_module = str(answers_data.get("api_module", "disabled")).lower()
        raw_api_languages = answers_data.get("api_languages", [])
        if isinstance(raw_api_languages, list):
            api_languages = {str(item).lower() for item in raw_api_languages}
        elif isinstance(raw_api_languages, str):
            api_languages = {
                item.strip().lower()
                for item in raw_api_languages.split(",")
                if item.strip()
            }
        else:
            api_languages = set()
        docs_module = str(answers_data.get("docs_module", "disabled")).lower()
        docs_framework = str(answers_data.get("docs_framework", "none")).lower()

        # Container support enabled for API or docs projects
        has_containers = (api_module == "enabled" and bool(api_languages)) or (
            docs_module == "enabled" and docs_framework == "fumadocs"
        )

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
                            check=False,
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
        render_status=render_status,
        render_returncode=int(completed.returncode),
    )


def _validate_variant_entry(entry: object, index: int) -> VariantResult:
    """Validate the complete record emitted by ``render_variant``."""
    description = f"Invalid render matrix variant at index {index}"
    if not isinstance(entry, dict):
        raise ValueError(f"{description}: expected an object")
    for field in (
        "variant",
        "answers",
        "destination",
        "workflow_validation",
        "container_status",
    ):
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{description}: {field} must be a nonempty string")
    smoke_results = entry.get("smoke_results")
    if "smoke_results" not in entry or (
        smoke_results is not None and not isinstance(smoke_results, dict)
    ):
        raise ValueError(f"{description}: smoke_results must be an object or null")
    status = entry.get("render_status")
    if status not in ("ok", "failed"):
        raise ValueError(f"{description}: render_status must be 'ok' or 'failed'")
    returncode = entry.get("render_returncode")
    if isinstance(returncode, bool) or not isinstance(returncode, int):
        raise ValueError(f"{description}: render_returncode must be an integer")
    if (status == "ok") != (returncode == 0):
        raise ValueError(f"{description}: render_status contradicts render_returncode")
    return cast(VariantResult, entry)


def load_render_summary(path: Path) -> RenderSummary:
    """Load nonempty render evidence before any derived metadata is rewritten."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Invalid render matrix: expected an object")
    variants = payload.get("variants")
    if not isinstance(variants, list) or not variants:
        raise ValueError("Invalid render matrix: variants must be a nonempty list")
    names: set[str] = set()
    for index, entry in enumerate(variants):
        variant = _validate_variant_entry(entry, index)
        name = variant["variant"]
        if name in names:
            raise ValueError(f"Invalid render matrix: duplicate variant {name!r}")
        names.add(name)
    return cast(RenderSummary, payload)


def load_quality_runs(artifacts: list[str]) -> list[dict[str, object]]:
    """Load completed maintainer profile results, rejecting missing evidence."""
    runs: list[dict[str, object]] = []
    for artifact in artifacts:
        payload = json.loads(Path(artifact).read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("profile") not in {
            "standard",
            "strict",
        }:
            raise ValueError(f"Invalid quality profile artifact: {artifact}")
        durations = payload.get("durations")
        if (
            not isinstance(durations, dict)
            or not durations
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
                for value in durations.values()
            )
        ):
            raise ValueError(f"Invalid quality durations: {artifact}")
        runs.append(payload)
    return runs


def main() -> None:
    """Orchestrate rendering of all discovered variants and aggregate metadata.

    Command-line arguments:
        --skip-render: Reuse an existing nonempty, valid render_matrix.json.
        --quality-artifacts: List of paths to quality run artifact JSON files.
        --retention-days: Number of days to retain quality artifacts (default: 90).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--skip-render", action="store_true")
    mode.add_argument(
        "--quality-only",
        action="store_true",
        help="Consolidate quality artifacts without producing render evidence",
    )
    parser.add_argument("--quality-artifacts", nargs="*", default=[])
    parser.add_argument("--retention-days", type=int, default=90)
    args = parser.parse_args()

    if args.retention_days <= 0:
        parser.error("--retention-days must be positive")
    if args.quality_only:
        if not args.quality_artifacts:
            parser.error("--quality-only requires --quality-artifacts")
        try:
            runs = load_quality_runs(args.quality_artifacts)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        quality_file = METADATA_DIR / "quality_summary.json"
        quality_file.write_text(
            json.dumps(
                {
                    "kind": "quality-only",
                    "quality_runs": runs,
                    "quality_retention_days": args.retention_days,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        logger.info(
            "Quality artifacts consolidated without rendering: {}", quality_file
        )
        return

    output_file = METADATA_DIR / "render_matrix.json"

    if args.skip_render and not output_file.is_file():
        parser.error(
            "--skip-render requires existing render_matrix.json; no render was started"
        )
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.skip_render:
        try:
            summary: RenderSummary = load_render_summary(output_file)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
        recorder = ModuleSuccessRecorder()
        for variant_entry in summary.get("variants", []):
            results = variant_entry.get("smoke_results", {})
            if results:
                recorder.update_from_results(
                    variant_entry.get("variant", "unknown"),
                    _module_results(results),
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
                    _module_results(smoke_results),
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
    logger.info(f"Render matrix complete. Metadata saved to {output_file}")

    failed = [
        v.get("variant", "?")
        for v in summary.get("variants", [])
        if v.get("render_status") == "failed"
    ]
    if failed:
        logger.error("Matrix completed with render failures: {}", ", ".join(failed))
        raise SystemExit(1)


if __name__ == "__main__":
    configure_logging()

    if not RENDER_SCRIPT.exists():
        logger.error("render-samples.sh not found; run from repository root.")
        sys.exit(1)
    main()
