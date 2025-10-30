"""Post-generation hook for the Riso template.

The hook emits guidance for next steps without invoking network-dependent
commands so that renders remain deterministic and constitution-compliant.
"""

from __future__ import annotations
import json
import pathlib
import sys
from datetime import datetime
from typing import Dict

DEFAULT_GUIDANCE = [
    "Create a virtual environment with `uv venv` (or activate an existing one).",
    "Install dependencies via `uv sync`.",
    "Run the baseline quickstart script: `uv run python -m {package}.quickstart`.",
    "Review docs/modules/prompt-reference.md for module-specific commands.",
]


def record_metadata(destination: pathlib.Path, data: dict[str, object]) -> None:
    metadata_file = destination / ".riso" / "post_gen_metadata.json"
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_answers(destination: pathlib.Path) -> Dict[str, str]:
    answers_path = destination / ".copier-answers.yml"
    if not answers_path.exists():
        return {}
    answers: Dict[str, str] = {}
    for raw_line in answers_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        answers[key.strip()] = value.strip()
    return answers


def layout_guidance(layout: str) -> list[str]:
    if layout == "monorepo":
        return [
            "Install workspace dependencies: `pnpm install`.",
            "Run Python validations: `uv run pytest`.",
            "Execute Node API smoke tests: `pnpm --filter api-node test`.",
            "Build documentation (if enabled): `pnpm --filter docs-fumadocs build`.",
        ]
    return []


def docs_guidance(answers: Dict[str, str]) -> list[str]:
    docs_site = answers.get("docs_site", "fumadocs").lower()
    if docs_site == "fumadocs":
        return [
            "Fumadocs preview: `pnpm --filter docs-fumadocs dev`.",
            "Fumadocs production build: `pnpm --filter docs-fumadocs build`.",
        ]
    if docs_site == "sphinx-shibuya":
        return [
            "Sphinx build: `uv run make docs`.",
            "Link check: `uv run make linkcheck`.",
        ]
    if docs_site == "docusaurus":
        return [
            "Docusaurus preview: `pnpm --filter docs-docusaurus dev`.",
            "Docusaurus build: `pnpm --filter docs-docusaurus build`.",
        ]
    return [
        "Documentation scaffolding skipped (`docs_site=none`). Review docs/guidance/none.md for enabling docs later.",
    ]


def optional_module_guidance(answers: Dict[str, str]) -> list[str]:
    guidance: list[str] = []
    if answers.get("cli_module", "").lower() == "enabled":
        guidance.append("Typer CLI ready: `uv run python -m {package}.cli --help`.")
    api_tracks = answers.get("api_tracks", "").lower()
    if api_tracks in {"python", "python+node"}:
        guidance.append("FastAPI service: `uv run uvicorn {package}.api.main:app --reload`.")  # noqa: S608
    if api_tracks in {"node", "python+node"}:
        guidance.append("Fastify service: `pnpm --filter api-node run dev`.")
    if answers.get("mcp_module", "").lower() == "enabled":
        guidance.append("List MCP tools: `uv run python -c \"from shared.mcp import tooling; print(tooling.list_tools())\"`.")
    return guidance


def render_guidance(package: str, answers: Dict[str, str]) -> str:
    layout = answers.get("project_layout", "single-package").lower()
    lines = ["Next steps:"]
    for item in DEFAULT_GUIDANCE:
        lines.append(f"- {item.format(package=package)}")
    for item in layout_guidance(layout):
        lines.append(f"- {item.format(package=package)}")
    for item in docs_guidance(answers):
        lines.append(f"- {item.format(package=package)}")
    for item in optional_module_guidance(answers):
        lines.append(f"- {item.format(package=package)}")
    return "\n".join(lines)


def main() -> None:
    destination = pathlib.Path.cwd()
    package = destination.name.replace("-", "_")
    answers = load_answers(destination)

    record_metadata(
        destination,
        {
            "rendered_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "destination": str(destination),
            "project_layout": answers.get("project_layout", "single-package"),
            "modules": {
                "cli_module": answers.get("cli_module", "disabled"),
                "api_tracks": answers.get("api_tracks", "none"),
                "mcp_module": answers.get("mcp_module", "disabled"),
                "docs_site": answers.get("docs_site", "fumadocs"),
                "shared_logic": answers.get("shared_logic", "disabled"),
            },
        },
    )

    guidance = render_guidance(package, answers)
    sys.stdout.write(guidance + "\n")


if __name__ == "__main__":
    main()
