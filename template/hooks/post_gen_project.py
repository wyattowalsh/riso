"""Post-generation hook for the Riso template.

The hook emits guidance for next steps without invoking network-dependent
commands so that renders remain deterministic and constitution-compliant.
"""

from __future__ import annotations
import json
import pathlib
import sys
from datetime import datetime

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

try:
    from hooks.quality_tool_check import (
        ensure_node_quality_tools,
        ensure_python_quality_tools,
        ToolCheck,
    )
    from hooks.workflow_validator import validate_workflows_directory
except ModuleNotFoundError:  # pragma: no cover - template lint
    ensure_python_quality_tools = lambda: []  # type: ignore
    ensure_node_quality_tools = lambda _: []  # type: ignore
    ToolCheck = None  # type: ignore
    validate_workflows_directory = lambda *_: 0  # type: ignore

DEFAULT_GUIDANCE = [
    "Create a virtual environment with `uv venv` (or activate an existing one).",
    "Install dependencies via `uv sync`.",
    "Run the baseline quickstart script: `uv run python -m {package}.quickstart`.",
    "Review docs/modules/prompt-reference.md for module-specific commands.",
]


def record_metadata(destination: pathlib.Path, data: dict[str, object]) -> None:
    """Record post-generation metadata to a JSON file.

    Args:
        destination: Root directory of the rendered project.
        data: Metadata dictionary to write to the file.
    """
    metadata_file = destination / ".riso" / "post_gen_metadata.json"
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_answers(destination: pathlib.Path) -> dict[str, str]:
    """Load answers from YAML file safely."""
    answers_path = destination / ".copier-answers.yml"
    if not answers_path.exists():
        return {}
    try:
        import yaml
        with answers_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                return {k: str(v) for k, v in data.items() if v is not None}
            return {}
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to parse answers file: {e}\n")
        return {}


def layout_guidance(layout: str) -> list[str]:
    """Generate layout-specific setup guidance.

    Args:
        layout: Project layout type (e.g., "monorepo", "single-package").

    Returns:
        List of guidance strings for the specified layout.
    """
    if layout == "monorepo":
        return [
            "Install workspace dependencies: `pnpm install`.",
            "Run Python validations: `uv run pytest`.",
            "Execute Node API smoke tests: `pnpm --filter api-node test`.",
            "Build documentation (if enabled): `pnpm --filter docs-fumadocs build`.",
        ]
    return []


def docs_guidance(answers: dict[str, str]) -> list[str]:
    """Generate documentation-specific setup guidance.

    Args:
        answers: Dictionary of copier answers containing project configuration.

    Returns:
        List of guidance strings for the configured documentation site.
    """
    docs_site = answers.get("docs_site", "fumadocs").lower()
    if docs_site == "fumadocs":
        return [
            "Fumadocs preview: `pnpm --filter docs-fumadocs dev`.",
            "Fumadocs production build: `pnpm --filter docs-fumadocs build`.",
        ]
    if docs_site == "sphinx-shibuya":
        return [
            "Sphinx build: `uv run sphinx-build docs dist/docs`.",
            "Link check: `uv run sphinx-build -b linkcheck docs dist/docs-linkcheck`.",
        ]
    if docs_site == "docusaurus":
        return [
            "Docusaurus preview: `pnpm --filter docs-docusaurus dev`.",
            "Docusaurus build: `pnpm --filter docs-docusaurus build`.",
        ]
    return [
        "Documentation scaffolding skipped (`docs_site=none`). Review docs/guidance/none.md for enabling docs later.",
    ]


def optional_module_guidance(answers: dict[str, str]) -> list[str]:
    """Generate guidance for optional modules based on project configuration.

    Args:
        answers: Dictionary of copier answers containing module enablement flags.

    Returns:
        List of guidance strings for enabled optional modules (CLI, API, MCP).
    """
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


def render_guidance(package: str, answers: dict[str, str]) -> str:
    """Render complete next-steps guidance based on project configuration.

    Args:
        package: Name of the generated package.
        answers: Dictionary of copier answers containing project configuration.

    Returns:
        Formatted multi-line string with all applicable guidance.
    """
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
    """Execute post-generation hook to validate tools and display guidance.

    Validates Python and Node quality tools, validates generated workflows,
    records metadata, and prints next-steps guidance to stdout.
    """
    destination = pathlib.Path.cwd()
    package = destination.name.replace("-", "_")
    answers = load_answers(destination)
    quality_checks = ensure_python_quality_tools() if ToolCheck is not None else []
    node_checks = []
    if ToolCheck is not None:
        node_required = answers.get("api_tracks", "none").lower() in {"node", "python+node"}
        node_checks = ensure_node_quality_tools(node_required)

    # Validate generated workflows if CI platform is GitHub Actions
    ci_platform = answers.get("ci_platform", "github-actions").lower()
    workflow_validation_status = "skipped"
    if ci_platform == "github-actions":
        workflows_dir = destination / ".github" / "workflows"
        # Run validation but don't fail render on validation failures
        exit_code = validate_workflows_directory(workflows_dir, strict=False)
        workflow_validation_status = "pass" if exit_code == 0 else "fail"

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
            "quality": {
                "profile": answers.get("quality_profile", "standard"),
                "tool_install_attempts": [
                    check.to_dict() if hasattr(check, "to_dict") else dict(check.__dict__)
                    for check in quality_checks + node_checks
                ],
            },
            "ci_platform": ci_platform,
            "workflow_validation": workflow_validation_status,
        },
    )

    guidance = render_guidance(package, answers)
    sys.stdout.write(guidance + "\n")


if __name__ == "__main__":
    main()
