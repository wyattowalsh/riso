"""Post-generation hook for the Riso template.

The hook emits guidance for next steps without invoking network-dependent
commands so that renders remain deterministic and constitution-compliant.
"""

from __future__ import annotations

import ast
import json
import os
import pathlib
import re
import sys
from datetime import datetime, timezone

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

from lib.removed_answer_keys import (  # noqa: E402
    REMOVED_ANSWER_KEYS,
    apply_removed_key_remaps,
)

try:
    from hooks.quality_tool_check import (
        ensure_node_quality_tools,
        ensure_python_quality_tools,
    )
    from hooks.workflow_validator import validate_workflows_directory

    _TOOL_CHECK_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - template lint

    def ensure_python_quality_tools(*, install: bool = True):  # type: ignore[misc]
        raise ModuleNotFoundError("quality_tool_check unavailable")

    def ensure_node_quality_tools(required: bool):  # type: ignore[misc]
        raise ModuleNotFoundError("quality_tool_check unavailable")

    def validate_workflows_directory(workflows_dir, strict: bool = False):  # type: ignore[misc]
        raise ModuleNotFoundError("workflow_validator unavailable")

    _TOOL_CHECK_AVAILABLE = False


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
    "go/api",
    "go/cli",
    "go/mcp",
    "graphql",
    "logic",
    "mcp",
    "node",
    "node/apps/api-node",
    "node/mcp",
    "node/release",
    "node/saas",
    "openspec",
    "python",
    "python/docs",
    "python/mcp",
    "python/release",
    "python/tests/codegen",
    "python/tests/graphql",
    "python/tests/websocket",
    "rust",
    "rust/api",
    "rust/cli",
    "rust/mcp",
    "saas-starter",
    "scripts/hooks",
    "scripts/release",
    "tauri",
    "testing",
    "tests/integration",
    "tests",
]

# Package-relative optional subtrees (filled with package import name at cleanup).
EMPTY_PACKAGE_SCAFFOLD_DIRS = (
    "python/src/{package}/codegen",
    "python/src/{package}/graphql_api",
    "python/src/{package}/websocket",
)


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
    """Apply known remaps in place, then fail on leftover removed keys."""
    remapped = dict(apply_removed_key_remaps(answers).answers)
    answers.clear()
    answers.update(remapped)
    leftover = sorted(key for key in REMOVED_ANSWER_KEYS if key in answers)
    if not leftover:
        return

    sys.stderr.write("Removed Copier answer keys are no longer supported:\n")
    for key in leftover:
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


def sanitize_package_name(name: str) -> str:
    """Normalize a package import name like derived project names."""
    package = re.sub(r"[^0-9A-Za-z_]+", "_", name).strip("_").lower()
    return package


def package_for_answers(destination: pathlib.Path, answers: dict[str, object]) -> str:
    """Resolve the package import name for guidance."""
    explicit = answer_text(answers, "package_name", "", lower=False).strip()
    if explicit:
        return sanitize_package_name(explicit) or destination.name.replace("-", "_")
    project_name = answer_text(answers, "project_name", destination.name, lower=False)
    package = sanitize_package_name(project_name)
    return package or destination.name.replace("-", "_")


def _empty_scaffold_candidates(package: str | None = None) -> list[str]:
    """Return known empty-scaffold relative paths, deepest first."""
    candidates = list(EMPTY_SCAFFOLD_DIRS)
    if package:
        candidates.extend(
            pattern.format(package=package) for pattern in EMPTY_PACKAGE_SCAFFOLD_DIRS
        )
    # Deepest paths first so nested empty trees collapse before parents.
    return sorted(set(candidates), key=lambda path: path.count("/"), reverse=True)


def _resolved_under_root(path: pathlib.Path, root: pathlib.Path) -> pathlib.Path | None:
    """Return resolved *path* when it stays under *root*, else ``None``."""
    try:
        resolved = path.resolve()
    except (OSError, ValueError):
        return None
    if not resolved.is_relative_to(root):
        return None
    return resolved


def _tree_has_files(path: pathlib.Path) -> bool:
    """Return True when *path* contains any non-symlink file."""
    try:
        return any(
            entry.is_file() and not entry.is_symlink() for entry in path.rglob("*")
        )
    except OSError:
        return True


def _remove_empty_tree(path: pathlib.Path, root: pathlib.Path) -> list[str]:
    """Remove *path* only when it is a file-free empty shell.

    *root* must already be ``.resolve()``d. If any real file exists under
    *path*, leave the tree untouched (populated modules may contain empty
    subdirs that are not in the candidate list). File-free shells left by
    Copier excludes are removed bottom-up.
    """
    removed: list[str] = []
    if path.is_symlink() or not path.is_dir():
        return removed
    resolved = _resolved_under_root(path, root)
    if resolved is None or _tree_has_files(path):
        return removed

    for child in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if child.is_symlink() or not child.is_dir():
            continue
        child_resolved = _resolved_under_root(child, root)
        if child_resolved is None:
            continue
        try:
            child.rmdir()
        except OSError:
            continue
        removed.append(str(child_resolved.relative_to(root)))

    try:
        path.rmdir()
    except OSError:
        return removed
    removed.append(str(resolved.relative_to(root)))
    return removed


def cleanup_empty_scaffold_dirs(
    destination: pathlib.Path, package: str | None = None
) -> list[str]:
    """Remove known empty scaffold directories left after conditional excludes."""
    removed: list[str] = []
    root = destination.resolve()
    for relative_path in _empty_scaffold_candidates(package):
        path = root / relative_path
        removed.extend(_remove_empty_tree(path, root))
    # Stable unique order for metadata / tests.
    seen: set[str] = set()
    unique: list[str] = []
    for item in removed:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def cleanup_empty_rendered_files(destination: pathlib.Path) -> list[str]:
    """Remove zero-byte stubs left by conditional Jinja templates."""
    removed: list[str] = []
    root = destination.resolve()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        try:
            if not path.is_relative_to(root):
                continue
        except ValueError:
            continue
        if not path.is_file() or path.name == ".gitkeep":
            continue
        if path.stat().st_size != 0:
            continue
        path.unlink()
        removed.append(str(path.relative_to(root)))
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
    riso_dir = destination / ".riso"
    if riso_dir.is_symlink():
        sys.stderr.write(
            "Error: .riso must not be a symlink before writing metadata.\n"
        )
        raise SystemExit(1)
    metadata_file = riso_dir / "post_gen_metadata.json"
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_answers(destination: pathlib.Path) -> dict[str, object]:
    """Load answers from YAML file safely."""
    answers_path = destination / ".copier-answers.yml"
    if not answers_path.is_file():
        return {}
    try:
        import yaml
    except ImportError as exc:
        sys.stderr.write(
            "Error: PyYAML is required to read .copier-answers.yml during post-generation.\n"
        )
        raise SystemExit(1) from exc
    try:
        with answers_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        sys.stderr.write(f"Error: Failed to parse answers file: {e}\n")
        raise SystemExit(1) from e
    if isinstance(data, dict):
        return {str(k): v for k, v in data.items() if v is not None}
    return {}


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _require_hook_tooling() -> None:
    if _TOOL_CHECK_AVAILABLE or _env_flag("RISO_SKIP_HOOK_TOOLS"):
        return
    sys.stderr.write(
        "Error: Riso hook helper scripts are unavailable. "
        "Set RISO_SKIP_HOOK_TOOLS=1 only for isolated lint runs.\n"
    )
    raise SystemExit(1)


def _revalidate_saas_answers(answers: dict[str, object]) -> None:
    """Re-run SaaS / generation gate checks after render."""
    try:
        from riso.core.generation_gates import validate_answers_for_generation
    except ImportError:
        if answers.get("saas_infra_module") != "enabled":
            return
        hook_dir = pathlib.Path(__file__).resolve().parent
        if str(hook_dir) not in sys.path:
            sys.path.insert(0, str(hook_dir))
        from pre_gen_project import _validate_saas_starter  # noqa: PLC0415

        issues = _validate_saas_starter(answers)
        errors = [item for item in issues if item["severity"] == "error"]
        if errors:
            sys.stderr.write("\n❌ SaaS configuration errors after generation:\n\n")
            for error in errors:
                sys.stderr.write(f"  {error['message']}\n")
            raise SystemExit(1)
        return

    result = validate_answers_for_generation(answers)
    if not result.ok:
        sys.stderr.write("\n❌ Post-generation answer validation failed:\n\n")
        for err in result.errors:
            sys.stderr.write(f"  {err}\n")
        raise SystemExit(1)


def should_install_node_dependencies(answers: dict[str, object]) -> bool:
    """Return True when post-gen should run pnpm install."""
    if os.environ.get("RISO_POST_GEN_INSTALL_NODE") == "1":
        return True
    value = answers.get("post_gen_install_node")
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "enabled", "on"}


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
                "i18n: Generate translations with "
                "`pnpm --filter docs-docusaurus write-translations`."
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
        "Documentation scaffolding skipped (`docs_module=disabled`). "
        "Review docs/guidance/none.md for enabling docs later.",
    ]


def ai_tools_guidance(answers: dict[str, object]) -> list[str]:
    """Generate guidance when AI tools harness is enabled."""
    if not answer_enabled(answers, "ai_tools_module"):
        return []
    return [
        "AI harness: edit AGENTS.md for agent instructions; "
        "see docs/ai-tools.md for MCP setup and the wyattowalsh/agents plugin.",
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
            "List MCP tools: `uv run python -c "
            '"from shared.mcp import tooling; print(tooling.list_tools())"`.'
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
    _require_hook_tooling()
    destination = pathlib.Path.cwd()
    answers = load_answers(destination)
    validate_removed_answer_keys(answers)
    _revalidate_saas_answers(answers)
    package = package_for_answers(destination, answers)
    # Zero-byte dual-gate stubs first so package optional dirs can rmdir.
    removed_empty_files = cleanup_empty_rendered_files(destination)
    removed_empty_dirs = cleanup_empty_scaffold_dirs(destination, package=package)
    removed_legacy_files = cleanup_legacy_root_pyproject(destination)
    install_python_tools = _env_flag("RISO_POST_GEN_INSTALL_TOOLS")
    quality_checks = (
        ensure_python_quality_tools(install=install_python_tools)
        if _TOOL_CHECK_AVAILABLE
        else []
    )
    node_checks = []
    if _TOOL_CHECK_AVAILABLE:
        node_track = "node" in api_languages_for_answers(answers)
        node_required = node_track and should_install_node_dependencies(answers)
        node_checks = ensure_node_quality_tools(node_required)

    quality_profile = answer_text(answers, "quality_profile", "standard")
    strict_hooks = _env_flag("RISO_STRICT_HOOKS") or quality_profile == "strict"

    # Validate generated workflows if CI platform is GitHub Actions
    ci_platform = answer_text(answers, "ci_platform", "github-actions")
    workflow_validation_status = "skipped"
    if ci_platform == "github-actions":
        workflows_dir = destination / ".github" / "workflows"
        changelog_enabled = (
            answer_text(answers, "changelog_module", "disabled") == "enabled"
        )
        workflow_strict = strict_hooks or changelog_enabled
        exit_code, workflow_validation_status = validate_workflows_directory(
            workflows_dir, strict=workflow_strict
        )
        if strict_hooks and (
            workflow_validation_status in {"fail", "tool_missing"} or exit_code != 0
        ):
            raise SystemExit(exit_code or 1)

    # Record pre-commit setup guidance (manual install; no hook mutation)
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
