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


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_COPIER = REPO_ROOT / "template" / "copier.yml"
SAMPLES_DIR = REPO_ROOT / "samples"
METADATA_DIR = SAMPLES_DIR / "metadata"
RENDER_MATRIX = METADATA_DIR / "render_matrix.json"
OUTPUT_FILE = METADATA_DIR / "matrix-data.json"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_prompt(key: str, prompt: Any, defaults: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(prompt, dict):
        return {
            "key": key,
            "type": None,
            "choices": None,
            "default": defaults.get(key),
            "when": None,
            "help": None,
        }

    return {
        "key": key,
        "type": prompt.get("type"),
        "choices": prompt.get("choices"),
        "default": defaults.get(key, prompt.get("default")),
        "when": prompt.get("when"),
        "help": prompt.get("help"),
    }


def collect_prompts(copier_data: dict[str, Any]) -> dict[str, Any]:
    defaults = copier_data.get("defaults", {}) or {}
    prompts = copier_data.get("prompts", {}) or {}

    prompt_entries = [
        normalize_prompt(key, prompt, defaults) for key, prompt in prompts.items()
    ]
    prompt_entries.sort(key=lambda item: item["key"])

    saas_prompts = [
        prompt for prompt in prompt_entries if prompt["key"].startswith("saas_")
    ]

    return {
        "defaults": defaults,
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
    for answers_file in sorted(SAMPLES_DIR.glob("*/copier-answers.yml")):
        variant = answers_file.parent.name
        answers = load_yaml(answers_file)
        variants.append(
            {
                "variant": variant,
                "answers_file": str(answers_file),
                "answers": answers,
            }
        )

    return {"source": "samples/*/copier-answers.yml", "variants": variants}


def main() -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    copier_data = load_yaml(TEMPLATE_COPIER)
    render_matrix = load_json(RENDER_MATRIX)

    payload: dict[str, Any] = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sources": {
            "template": str(TEMPLATE_COPIER),
            "render_matrix": str(RENDER_MATRIX) if render_matrix else None,
        },
        "template": {
            "metadata": copier_data.get("metadata", {}),
            **collect_prompts(copier_data),
        },
        "samples": collect_samples(render_matrix),
    }

    OUTPUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Matrix data written to {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI error surface
        raise SystemExit(str(exc)) from exc
