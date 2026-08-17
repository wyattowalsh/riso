#!/usr/bin/env python3
"""Generate a consolidated matrix data snapshot for reuse across the repo."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - dependency wiring
    raise SystemExit("PyYAML is required to generate matrix data.") from exc

from riso.template import get_defaults, get_prompts, load_copier_config


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = REPO_ROOT / "template"
TEMPLATE_COPIER = TEMPLATE_DIR / "copier.yml"
SAMPLES_DIR = REPO_ROOT / "samples"
METADATA_DIR = SAMPLES_DIR / "metadata"
RENDER_MATRIX = METADATA_DIR / "render_matrix.json"
OUTPUT_FILE = METADATA_DIR / "matrix-data.json"
WEB_OUTPUT = REPO_ROOT / "web" / "src" / "data" / "matrix-data.json"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def template_defaults_block(copier_data: dict[str, Any]) -> dict[str, Any]:
    """Return raw ``_defaults`` / legacy ``defaults`` from copier.yml."""
    return dict(copier_data.get("_defaults", copier_data.get("defaults", {})) or {})


def template_metadata(copier_data: dict[str, Any]) -> dict[str, Any]:
    return dict(copier_data.get("_metadata", copier_data.get("metadata", {})) or {})


def normalize_prompt(key: str, prompt: Any, defaults: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(prompt, dict):
        return {
            "key": key,
            "type": None,
            "choices": None,
            "default": defaults.get(key),
            "when": None,
            "help": None,
            "multiselect": None,
        }

    return {
        "key": key,
        "type": prompt.get("type"),
        "choices": prompt.get("choices"),
        "default": defaults.get(key, prompt.get("default")),
        "when": prompt.get("when"),
        "help": prompt.get("help"),
        "multiselect": prompt.get("multiselect"),
    }


def collect_prompts(template_path: Path) -> dict[str, Any]:
    copier_data = load_copier_config(template_path)
    raw_defaults = template_defaults_block(copier_data)
    effective_defaults = get_defaults(template_path)
    prompts = get_prompts(template_path)

    prompt_entries = [
        normalize_prompt(key, prompt, effective_defaults)
        for key, prompt in sorted(prompts.items())
    ]

    saas_prompts = [
        prompt for prompt in prompt_entries if prompt["key"].startswith("saas_")
    ]

    return {
        "_defaults": raw_defaults,
        "defaults": effective_defaults,
        "prompts": prompt_entries,
        "saas_prompts": saas_prompts,
    }


def collect_samples(render_matrix: dict[str, Any] | None) -> dict[str, Any]:
    if render_matrix:
        return {
            "source": str(RENDER_MATRIX),
            "render_matrix": render_matrix,
        }

    variants: list[dict[str, Any]] = []
    if SAMPLES_DIR.is_dir():
        from scripts.lib.paths import iter_sample_answer_files

        for answers_file in iter_sample_answer_files(SAMPLES_DIR):
            try:
                rel = answers_file.parent.relative_to(SAMPLES_DIR)
            except ValueError:
                continue
            if "render" in rel.parts or "metadata" in rel.parts:
                continue
            variant = rel.as_posix()
            answers = load_yaml(answers_file)
            variants.append(
                {
                    "variant": variant,
                    "answers_file": str(answers_file),
                    "answers": answers,
                }
            )

    return {"source": "samples/**/copier-answers.yml", "variants": variants}


def main() -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    render_matrix = load_json(RENDER_MATRIX)
    prompt_bundle = collect_prompts(TEMPLATE_DIR)

    payload: dict[str, Any] = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sources": {
            "template": str(TEMPLATE_COPIER),
            "render_matrix": str(RENDER_MATRIX) if render_matrix else None,
        },
        "template": {
            "metadata": template_metadata(load_copier_config(TEMPLATE_DIR)),
            **prompt_bundle,
        },
        "samples": collect_samples(render_matrix),
    }

    text = json.dumps(payload, indent=2) + "\n"
    OUTPUT_FILE.write_text(text, encoding="utf-8")
    prompt_count = len(prompt_bundle["prompts"])
    print(f"Matrix data written to {OUTPUT_FILE} ({prompt_count} prompts)")
    if WEB_OUTPUT.parent.is_dir():
        WEB_OUTPUT.write_text(text, encoding="utf-8")
        print(f"Matrix data dual-written to {WEB_OUTPUT}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI error surface
        raise SystemExit(str(exc)) from exc
