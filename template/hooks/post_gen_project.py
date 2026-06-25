"""Post-generation hook for the Riso template.

The hook emits guidance for next steps without invoking network-dependent
commands so that renders remain deterministic and constitution-compliant.
"""

from __future__ import annotations

import ast
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

try:
    from hooks.quality_tool_check import (
        ensure_node_quality_tools,
        ensure_python_quality_tools,
        ToolCheck,
    )
    from hooks.workflow_validator import validate_workflows_directory
except ModuleNotFoundError:  # pragma: no cover - template lint

    def ensure_python_quality_tools():
        return []

    def ensure_node_quality_tools(_):
        return []

    ToolCheck = None  # type: ignore[assignment]

    def validate_workflows_directory(*args, **kwargs):  # noqa: ARG001
        return 0


DEFAULT_GUIDANCE = [
    "Read AGENTS.md for AI agent instructions and project commands.",
    "Create a virtual environment with `uv venv` (or activate an existing one).",
    "Install dependencies via `uv sync`.",
    "Install pre-commit hooks via `{hooks_cmd}` from the project root.",
    "Run the baseline quickstart script: `uv run python -m {package}.quickstart`.",
    "Review docs/modules/prompt-reference.md for module-specific commands.",
]

EMPTY_SCAFFOLD_DIRS = [
    ".circleci",
    ".claude",
    ".gitlab",
    "build",
    "electron",
    "frontend",
    "go",
    "graphql",
    "logic",
    "mcp",
    "node",
    "python",
    "rust",
    "saas-starter",
    "scripts/hooks",
    "tauri",
    "testing",
    "tests/graphql",
    "tests/integration",
    "tests",
]

REMOVED_ANSWER_KEYS = {
    "api_tracks": "Use api_module plus api_languages.",
    "api_language": "Use api_languages.",
    "docs_site": "Use docs_module plus docs_framework.",
    "mcp_language": "Use mcp_languages.",
    "saas_starter_module": "Use saas_infra_module.",
    "saas_auth": "Use saas_auth_module plus saas_auth_provider.",
    "saas_billing": "Use saas_billing_module plus saas_billing_provider.",
}


def answer_text(
    answers: dict[str, object], key: str, default: object = "", *, lower: bool = True
) -> str:
    """Return an answer value as normalized text."""
    value = answers.get(key, default)
    text = str(value)
    return text.lower() if lower else text


def answer_enabled(answers: dict[str, object], key: str) -> bool:
    """Return whether an enabled/disabled answer is enabled."""
    return answer_text(answers, key) == "enabled"


def answer_list(
    answers: dict[str, object], key: str, default: list[str] | None = None
) -> list[str]:
    """Return an answer value as a lower-case string list."""
    value = answers.get(key, default or [])
    if isinstance(value, list):
        return [str(item).lower() for item in value]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            parsed = []
        if isinstance(parsed, list):
            return [str(item).lower() for item in parsed]
    separator = "+" if "+" in text else ","
    return [item.strip().lower() for item in text.split(separator) if item.strip()]


def validate_removed_answer_keys(answers: dict[str, object]) -> None:
    """Fail renders that still carry removed Copier answer keys."""
    removed = sorted(key for key in REMOVED_ANSWER_KEYS if key in answers)
    if not removed:
        return

    sys.stderr.write("Removed Copier answer keys are no longer supported:\n")
    for key in removed:
        sys.stderr.write(f"- {key}: {REMOVED_ANSWER_KEYS[key]}\n")
    raise SystemExit(1)


def docs_framework_for_answers(answers: dict[str, object]) -> str:
    """Resolve the selected docs framework from canonical answers."""
    if answer_enabled(answers, "docs_module"):
        return answer_text(answers, "docs_framework", "fumadocs")
    return "none"


def api_languages_for_answers(answers: dict[str, object]) -> list[str]:
    """Resolve selected API languages from canonical answers."""
    if not answer_enabled(answers, "api_module"):
        return []
    return answer_list(answers, "api_languages", ["python"])


def package_for_answers(destination: pathlib.Path, answers: dict[str, object]) -> str:
    """Resolve the package import name for guidance."""
    explicit = answer_text(answers, "package_name", "", lower=False).strip()
    if explicit:
        return explicit
    project_name = answer_text(answers, "project_name", destination.name, lower=False)
    package = re.sub(r"[^0-9A-Za-z_]+", "_", project_name).strip("_").lower()
    return package or destination.name.replace("-", "_")


def cleanup_empty_scaffold_dirs(destination: pathlib.Path) -> list[str]:
    """Remove known empty scaffold directories left after conditional excludes."""
    removed: list[str] = []
    for relative_path in sorted(
        EMPTY_SCAFFOLD_DIRS, key=lambda path: path.count("/"), reverse=True
    ):
        path = destination / relative_path
        if not path.is_dir():
            continue
        try:
            path.rmdir()
        except OSError:
            continue
        removed.append(relative_path)
    return removed


def cleanup_empty_rendered_files(destination: pathlib.Path) -> list[str]:
    """Remove zero-byte stubs left by conditional Jinja templates."""
    removed: list[str] = []
    for path in sorted(destination.rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        if path.stat().st_size != 0:
            continue
        path.unlink()
        removed.append(str(path.relative_to(destination)))
    return removed


def cleanup_legacy_root_pyproject(destination: pathlib.Path) -> list[str]:
    """Remove obsolete root pyproject.toml when python/pyproject.toml is canonical."""
    removed: list[str] = []
    root_pyproject = destination / "pyproject.toml"
    python_pyproject = destination / "python" / "pyproject.toml"
    if not root_pyproject.is_file() or not python_pyproject.is_file():
        return removed
    content = root_pyproject.read_text(encoding="utf-8")
    if "[tool.uv.tasks]" not in content or "[project]" in content:
        return removed
    if "{%" in content or "mypy" in content:
        root_pyproject.unlink()
        removed.append("pyproject.toml")
    return removed


def record_metadata(destination: pathlib.Path, data: dict[str, object]) -> None:
    """Record post-generation metadata to a JSON file.

    Args:
        destination: Root directory of the rendered project.
        data: Metadata dictionary to write to the file.
    """
    metadata_file = destination / ".riso" / "post_gen_metadata.json"
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_answers(destination: pathlib.Path) -> dict[str, object]:
    """Load answers from YAML file safely."""
    answers_path = destination / ".copier-answers.yml"
    if not answers_path.exists():
        return {}
    try:
        import yaml

        with answers_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                return {str(k): v for k, v in data.items() if v is not None}
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


def docs_guidance(answers: dict[str, object]) -> list[str]:
    """Generate documentation-specific setup guidance.

    Args:
        answers: Dictionary of copier answers containing project configuration.

    Returns:
        List of guidance strings for the configured documentation site.
    """
    docs_framework = docs_framework_for_answers(answers)
    if docs_framework == "fumadocs":
        return [
            "Fumadocs preview: `pnpm --filter docs-fumadocs dev`.",
            "Fumadocs production build: `pnpm --filter docs-fumadocs build`.",
        ]
    if docs_framework == "sphinx-shibuya":
        return [
            "Sphinx build: `uv run sphinx-build docs dist/docs`.",
            "Link check: `uv run sphinx-build -b linkcheck docs dist/docs-linkcheck`.",
        ]
    if docs_framework == "docusaurus":
        guidance = [
            "Docusaurus preview: `pnpm --filter docs-docusaurus start`.",
            "Docusaurus build: `pnpm --filter docs-docusaurus build`.",
        ]
        # Add feature-specific guidance
        if answer_enabled(answers, "docusaurus_llms_txt"):
            guidance.append(
                "AI docs: After build, find `llms.txt` and `llms-full.txt` in `build/`."
            )
        if answer_enabled(answers, "docusaurus_faster"):
            guidance.append("Performance: Rspack + SWC enabled for 2-4x faster builds.")
        if answer_enabled(answers, "docusaurus_i18n"):
            guidance.append(
                "i18n: Generate translations with `pnpm --filter docs-docusaurus write-translations`."
            )
        if answer_enabled(answers, "docusaurus_openapi"):
            guidance.append(
                "OpenAPI: Update `openapi/openapi.yaml` to regenerate API docs."
            )
        if answer_enabled(answers, "docusaurus_mermaid"):
            guidance.append(
                "Diagrams: Use ```mermaid code blocks for flowcharts, sequence diagrams, etc."
            )
        if answer_enabled(answers, "docusaurus_math"):
            guidance.append(
                "Math: Use $inline$ or $$block$$ LaTeX syntax for equations."
            )
        if answer_enabled(answers, "docusaurus_show_last_update"):
            guidance.append(
                "Git timestamps: Use `fetch-depth: 0` in CI for accurate 'Last updated' times."
            )
        if answer_enabled(answers, "docusaurus_pwa"):
            guidance.append(
                "PWA: Update `static/manifest.json` with your app details for offline support."
            )
        if answer_text(answers, "docusaurus_comments") == "giscus":
            guidance.append(
                "Comments: Configure Giscus repo/category IDs in `src/components/GiscusComments/`."
            )
        if answer_enabled(answers, "docusaurus_redirects"):
            guidance.append(
                "Redirects: Add URL redirects in `docusaurus.config.ts` plugin config."
            )
        if answer_enabled(answers, "docusaurus_announcement_bar"):
            guidance.append(
                "Announcement: Edit banner content in `docusaurus.config.ts` themeConfig."
            )
        if answer_enabled(answers, "docusaurus_sitemap"):
            guidance.append(
                "Sitemap: sitemap.xml generated automatically at build time."
            )
        return guidance
    return [
        "Documentation scaffolding skipped (`docs_module=disabled`). Review docs/guidance/none.md for enabling docs later.",
    ]


def ai_tools_guidance(answers: dict[str, object]) -> list[str]:
    """Generate guidance when AI tools harness is enabled."""
    if not answer_enabled(answers, "ai_tools_module"):
        return []
    return [
        "AI harness: edit AGENTS.md for agent instructions; see docs/ai-tools.md for MCP setup.",
    ]


def optional_module_guidance(answers: dict[str, object]) -> list[str]:
    """Generate guidance for optional modules based on project configuration.

    Args:
        answers: Dictionary of copier answers containing module enablement flags.

    Returns:
        List of guidance strings for enabled optional modules (CLI, API, MCP).
    """
    guidance: list[str] = []
    if answer_enabled(answers, "cli_module"):
        guidance.append(
            "Typer CLI ready: `uv sync --group cli` then "
            "`uv run python -m {package}.cli --help`."
        )
    api_languages = set(api_languages_for_answers(answers))
    if "python" in api_languages:
        guidance.append(
            "FastAPI service: `uv run uvicorn {package}.api.main:app --reload`."
        )  # noqa: S608
    if "node" in api_languages:
        guidance.append("Fastify service: `pnpm --filter api-node run dev`.")
    if answer_enabled(answers, "mcp_module"):
        guidance.append(
            'List MCP tools: `uv run python -c "from shared.mcp import tooling; print(tooling.list_tools())"`.'
        )
    return guidance


def render_guidance(package: str, answers: dict[str, object]) -> str:
    """Render complete next-steps guidance based on project configuration.

    Args:
        package: Name of the generated package.
        answers: Dictionary of copier answers containing project configuration.

    Returns:
        Formatted multi-line string with all applicable guidance.
    """
    layout = answer_text(answers, "project_layout", "single-package")
    task_runner = answer_text(answers, "task_runner", "just")
    hooks_cmd = hooks_install_command(task_runner)
    lines = ["Next steps:"]
    for item in DEFAULT_GUIDANCE:
        lines.append(f"- {item.format(package=package, hooks_cmd=hooks_cmd)}")
    for item in layout_guidance(layout):
        lines.append(f"- {item.format(package=package)}")
    for item in docs_guidance(answers):
        lines.append(f"- {item.format(package=package)}")
    for item in optional_module_guidance(answers):
        lines.append(f"- {item.format(package=package)}")
    for item in ai_tools_guidance(answers):
        lines.append(f"- {item.format(package=package)}")
    return "\n".join(lines)


def hooks_install_command(task_runner: str) -> str:
    """Return the preferred pre-commit install command for the task runner."""
    if task_runner in {"just", "both"}:
        return "just hooks"
    if task_runner == "makefile":
        return "make hooks"
    return "uv run pre-commit install --install-hooks"


def pre_commit_setup_guidance(
    quality_profile: str, changelog_module: str, task_runner: str = "just"
) -> dict[str, object]:
    """Describe hook setup without mutating the generated repository."""
    hook_types = ["pre-commit"]
    if changelog_module == "enabled" or quality_profile == "strict":
        hook_types.append("commit-msg")
    if quality_profile == "strict":
        hook_types.append("pre-push")

    return {
        "status": "manual",
        "hooks": hook_types,
        "install_command": hooks_install_command(task_runner),
    }


def main() -> None:
    """Execute post-generation hook to validate tools and display guidance.

    Validates Python and Node quality tools, validates generated workflows,
    records metadata, and prints next-steps guidance to stdout.
    """
    destination = pathlib.Path.cwd()
    answers = load_answers(destination)
    validate_removed_answer_keys(answers)
    package = package_for_answers(destination, answers)
    removed_empty_dirs = cleanup_empty_scaffold_dirs(destination)
    removed_empty_files = cleanup_empty_rendered_files(destination)
    removed_legacy_files = cleanup_legacy_root_pyproject(destination)
    quality_checks = ensure_python_quality_tools() if ToolCheck is not None else []
    node_checks = []
    if ToolCheck is not None:
        node_required = "node" in api_languages_for_answers(answers)
        node_checks = ensure_node_quality_tools(node_required)

    # Validate generated workflows if CI platform is GitHub Actions
    ci_platform = answer_text(answers, "ci_platform", "github-actions")
    workflow_validation_status = "skipped"
    if ci_platform == "github-actions":
        workflows_dir = destination / ".github" / "workflows"
        changelog_enabled = (
            answer_text(answers, "changelog_module", "disabled") == "enabled"
        )
        exit_code = validate_workflows_directory(
            workflows_dir, strict=changelog_enabled
        )
        workflow_validation_status = "pass" if exit_code == 0 else "fail"

    # Record pre-commit setup guidance (manual install; no hook mutation)
    quality_profile = answer_text(answers, "quality_profile", "standard")
    changelog_module = answer_text(answers, "changelog_module", "disabled")
    task_runner = answer_text(answers, "task_runner", "just")
    pre_commit_result = pre_commit_setup_guidance(
        quality_profile, changelog_module, task_runner
    )

    record_metadata(
        destination,
        {
            "rendered_at": datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "destination": str(destination),
            "project_layout": answers.get("project_layout", "single-package"),
            "modules": {
                "cli_module": answers.get("cli_module", "disabled"),
                "api_module": answers.get("api_module", "disabled"),
                "api_languages": api_languages_for_answers(answers),
                "mcp_module": answers.get("mcp_module", "disabled"),
                "mcp_languages": answer_list(answers, "mcp_languages", ["python"]),
                "docs_module": answers.get("docs_module", "disabled"),
                "docs_framework": answers.get("docs_framework", "fumadocs"),
                "shared_logic": answers.get("shared_logic", "disabled"),
                "desktop_module": answers.get("desktop_module", "disabled"),
                "saas_infra_module": answers.get("saas_infra_module", "disabled"),
                "ai_tools_module": answers.get("ai_tools_module", "disabled"),
            },
            "quality": {
                "profile": quality_profile,
                "tool_install_attempts": [
                    check.to_dict()
                    if hasattr(check, "to_dict")
                    else dict(check.__dict__)
                    for check in quality_checks + node_checks
                ],
            },
            "pre_commit": pre_commit_result,
            "ci_platform": ci_platform,
            "workflow_validation": workflow_validation_status,
            "cleanup": {
                "removed_empty_dirs": removed_empty_dirs,
                "removed_empty_files": removed_empty_files,
                "removed_legacy_files": removed_legacy_files,
            },
        },
    )

    guidance = render_guidance(package, answers)
    sys.stdout.write(guidance + "\n")


if __name__ == "__main__":
    main()
