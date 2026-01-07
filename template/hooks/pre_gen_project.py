"""Pre-generation hook that validates and provisions local tooling.

The hook attempts a single auto-install pass using ``mise`` (for Node.js and
pnpm) and records every attempt in ``.riso/toolchain_provisioning.jsonl``. When
tooling is still missing after the attempt, the hook exits with actionable
instructions so renders never proceed in a partially configured state.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

LOG_PATH = Path(".riso/toolchain_provisioning.jsonl")

sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))

try:
    from hooks.quality_tool_check import ensure_python_quality_tools, ToolCheck
except ModuleNotFoundError:  # pragma: no cover - during template linting
    ensure_python_quality_tools = lambda: []  # type: ignore
    ToolCheck = None  # type: ignore

# Valid configuration values
VALID_DOCS_SITES = {"fumadocs", "sphinx-shibuya", "docusaurus", "none"}
VALID_CI_PLATFORMS = {"github-actions", "none"}
VALID_PROJECT_LAYOUTS = {"single-package", "monorepo"}
VALID_QUALITY_PROFILES = {"standard", "strict"}


class ProvisionResult(dict):
    """Typed helper for logging provisioning attempts."""

    def __init__(
        self,
        *,
        tool_name: str,
        version_requested: str,
        status: str,
        stderr: str | None = None,
        next_steps: str | None = None,
        retry_command: str | None = None,
    ) -> None:
        super().__init__(
            tool_name=tool_name,
            version_requested=version_requested,
            status=status,
            timestamp=_dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
        )
        if stderr:
            self["stderr"] = stderr
        if next_steps:
            self["next_steps"] = next_steps
        if retry_command:
            self["retry_command"] = retry_command


def _load_from_env(
    key: str,
    valid_values: set[str] | None = None,
    default: str = "",
) -> str:
    """Load a configuration value from copier environment variables.

    Args:
        key: The configuration key to look for (e.g., 'docs_site')
        valid_values: Optional set of allowed values for validation
        default: Default value if key not found or invalid

    Returns:
        The configuration value or default
    """
    candidates = (
        "COPIER_ANSWERS",
        "COPIER_JINJA2_CONTEXT",
        "COPIER_RENDER_CONTEXT",
    )
    for env_key in candidates:
        raw = os.environ.get(env_key)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            value = data.get(key)
            if isinstance(value, str) and value:
                if valid_values is None or value in valid_values:
                    return value
    return default


def _load_docs_site(default: str = "fumadocs") -> str:
    """Best-effort retrieval of the selected documentation variant."""
    return _load_from_env("docs_site", VALID_DOCS_SITES, default)


def _load_ci_platform(default: str = "github-actions") -> str:
    """Best-effort retrieval of the selected CI platform."""
    return _load_from_env("ci_platform", VALID_CI_PLATFORMS, default)


def _load_copier_context() -> dict:
    """Load full copier context for validation."""
    candidates = (
        "COPIER_ANSWERS",
        "COPIER_JINJA2_CONTEXT",
        "COPIER_RENDER_CONTEXT",
    )
    for key in candidates:
        raw = os.environ.get(key)
        if not raw:
            continue
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    return {}


def _validate_saas_starter(context: dict) -> list[dict]:
    """Validate SaaS Starter module configuration."""
    if context.get("saas_starter_module") != "enabled":
        return []
    
    issues = []
    
    # Error-level incompatibilities (blocking)
    error_incompatibilities = [
        {
            "combination": ["neon", "supabase-storage"],
            "message": (
                "Cannot use Neon database with Supabase Storage. "
                "Choose either:\n"
                "  1. Full Supabase (database + storage)\n"
                "  2. Neon database + Cloudflare R2 storage"
            ),
        },
    ]
    
    # Warning-level incompatibilities (non-blocking)
    warning_incompatibilities = [
        {
            "combination": ["cloudflare", "prisma"],
            "message": (
                "⚠️  Prisma requires TCP connections, which Cloudflare Workers don't support.\n"
                "You'll need to use Prisma Data Proxy (adds latency and cost).\n"
                "Recommendation: Use Drizzle ORM for better edge compatibility."
            ),
        },
        {
            "combination": ["vercel", "r2"],
            "message": (
                "⚠️  Cloudflare R2 works with Vercel but egress bandwidth charges apply."
            ),
        },
    ]
    
    # Info-level notices
    info_notices = [
        {
            "combination": ["supabase", "clerk"],
            "message": (
                "ℹ️  You've selected both Supabase and Clerk.\n"
                "Supabase Auth will be disabled in favor of Clerk."
            ),
        },
    ]
    
    # Extract selected values
    selected_values = [
        context.get(f"saas_{key}") for key in
        ["runtime", "hosting", "database", "orm", "auth", "storage", "cicd"]
    ]
    
    # Check error-level incompatibilities
    for rule in error_incompatibilities:
        combo = rule["combination"]
        if all(item in selected_values for item in combo):
            issues.append({
                "severity": "error",
                "message": rule["message"],
            })
    
    # Check warning-level incompatibilities
    for rule in warning_incompatibilities:
        combo = rule["combination"]
        if all(item in selected_values for item in combo):
            issues.append({
                "severity": "warning",
                "message": rule["message"],
            })
    
    # Check info-level notices
    for rule in info_notices:
        combo = rule["combination"]
        if all(item in selected_values for item in combo):
            issues.append({
                "severity": "info",
                "message": rule["message"],
            })
    
    return issues


def _log_attempt(entry: ProvisionResult) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry))
        fh.write("\n")


def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


def _attempt_install(tool: str, version: str, mise_spec: str | None) -> ProvisionResult:
    """Attempt to provision ``tool`` and return the result payload."""

    next_steps = {
        "uv": "Install uv from https://github.com/astral-sh/uv or ensure it is available on PATH.",
        "node": "Install Node.js 20 LTS (https://nodejs.org/) or enable mise auto-install.",
        "pnpm": "Install pnpm 8+ from https://pnpm.io/installation or enable mise auto-install.",
    }

    if shutil.which(tool):
        return ProvisionResult(tool_name=tool, version_requested=version, status="already_present")

    # Prefer mise-based installation when possible.
    if mise_spec and shutil.which("mise"):
        result = _run_command(["mise", "install", mise_spec])
        if result.returncode == 0 and shutil.which(tool):
            return ProvisionResult(tool_name=tool, version_requested=version, status="installed")
        return ProvisionResult(
            tool_name=tool,
            version_requested=version,
            status="failed",
            stderr=(result.stderr or result.stdout).strip(),
            next_steps=next_steps.get(tool),
            retry_command=f"mise install {mise_spec}",
        )

    return ProvisionResult(
        tool_name=tool,
        version_requested=version,
        status="failed",
        next_steps=next_steps.get(tool),
    )


def _install_required_tools(tool_matrix: list[tuple[str, str, str | None]]) -> list[ProvisionResult]:
    """Install required tools from the tool matrix.

    Args:
        tool_matrix: List of (tool_name, version, mise_spec) tuples

    Returns:
        List of failed ProvisionResult objects
    """
    failures = []
    for tool, version, mise_spec in tool_matrix:
        result = _attempt_install(tool, version, mise_spec)
        _log_attempt(result)
        if result["status"] == "failed":
            failures.append(result)
    return failures


def _check_python_quality_tools() -> list[ProvisionResult]:
    """Check availability of Python quality tools.

    Returns:
        List of failed ProvisionResult objects for unavailable tools
    """
    failures = []
    if ToolCheck is not None:
        for check in ensure_python_quality_tools():
            entry = ProvisionResult(
                tool_name=check.name,
                version_requested="quality-suite",
                status=check.status,
                stderr=getattr(check, "stderr", None),
                next_steps=getattr(check, "next_steps", None),
            )
            _log_attempt(entry)
            if entry["status"] not in {"present", "installed"}:
                failures.append(entry)
    return failures


def _check_and_log_actionlint(ci_platform: str) -> None:
    """Check and log actionlint availability for GitHub Actions.

    Args:
        ci_platform: The CI platform being used (github_actions, gitlab_ci, etc.)
    """
    # Add actionlint check if GitHub Actions CI platform selected
    if ci_platform == "github-actions":
        # Check actionlint availability but don't fail on missing
        # (post-generation hook will handle validation gracefully)
        if not shutil.which("actionlint"):
            _log_attempt(ProvisionResult(
                tool_name="actionlint",
                version_requested="latest",
                status="not_found",
                next_steps="Install actionlint for workflow validation: brew install actionlint (macOS) or see https://github.com/rhysd/actionlint"
            ))
            sys.stderr.write(
                "⚠️  actionlint not found - workflow validation will be skipped\n"
                "   Install: brew install actionlint (macOS)\n"
                "   Or see: https://github.com/rhysd/actionlint\n"
            )
        else:
            _log_attempt(ProvisionResult(
                tool_name="actionlint",
                version_requested="latest",
                status="already_present"
            ))


def _validate_and_report_saas_starter(context: dict) -> bool:
    """Validate SaaS starter configuration and report errors.

    Args:
        context: The Copier context dictionary

    Returns:
        True if validation passed (no errors), False otherwise
    """
    if context.get("saas_starter_module") != "enabled":
        return True

    sys.stderr.write("\n🔍 Validating SaaS Starter configuration...\n")
    issues = _validate_saas_starter(context)

    # Report errors (blocking)
    errors = [i for i in issues if i["severity"] == "error"]
    if errors:
        sys.stderr.write("\n❌ Configuration errors found:\n\n")
        for error in errors:
            sys.stderr.write(f"  {error['message']}\n\n")
        return False

    # Report warnings (non-blocking)
    warnings = [i for i in issues if i["severity"] == "warning"]
    if warnings:
        sys.stderr.write("\n⚠️  Configuration warnings:\n\n")
        for warning in warnings:
            sys.stderr.write(f"  {warning['message']}\n\n")

    # Report info notices
    infos = [i for i in issues if i["severity"] == "info"]
    if infos:
        sys.stderr.write("\nℹ️  Configuration notes:\n\n")
        for info in infos:
            sys.stderr.write(f"  {info['message']}\n\n")

    sys.stderr.write("✅ SaaS Starter configuration validated successfully!\n\n")
    return True


def _report_failures_and_exit(failures: list[ProvisionResult]) -> None:
    """Report all failures and exit with error code.

    Args:
        failures: List of failed ProvisionResult objects

    Note:
        This function does not return - it calls sys.exit(1)
    """
    if not failures:
        return

    sys.stderr.write(
        "Riso template prerequisite check failed. Please install the "
        "following tooling before re-running copier:\n"
    )
    for failure in failures:
        sys.stderr.write(f"- {failure['tool_name']} (requested {failure['version_requested']}):\n")
        if failure.get("stderr"):
            sys.stderr.write(f"  stderr: {failure['stderr']}\n")
        if failure.get("retry_command"):
            sys.stderr.write(f"  retry: {failure['retry_command']}\n")
        if failure.get("next_steps"):
            sys.stderr.write(f"  help: {failure['next_steps']}\n")
    sys.exit(1)


def _build_tool_matrix(docs_site: str, context: dict) -> list[tuple[str, str, str | None]]:
    """Build the matrix of required tools with versions.

    Args:
        docs_site: The documentation site type (sphinx, fumadocs, etc.)
        context: The Copier context dictionary

    Returns:
        List of (tool_name, version, mise_spec) tuples
    """
    tool_matrix: list[tuple[str, str, str | None]] = [
        ("uv", "0.4", "uv@0.4"),
    ]

    if docs_site != "none" or context.get("saas_starter_module") == "enabled":
        tool_matrix.extend(
            [
                ("node", "20", "node@20"),
                ("pnpm", "8", "pnpm@8"),
            ]
        )

    return tool_matrix


def main() -> None:
    docs_site = _load_docs_site()
    ci_platform = _load_ci_platform()
    context = _load_copier_context()

    # Validate SaaS Starter configuration if enabled
    if not _validate_and_report_saas_starter(context):
        sys.exit(1)

    tool_matrix = _build_tool_matrix(docs_site, context)

    # Check and log actionlint availability
    _check_and_log_actionlint(ci_platform)

    failures = _install_required_tools(tool_matrix)

    # Check Python quality tools
    failures.extend(_check_python_quality_tools())

    _report_failures_and_exit(failures)


if __name__ == "__main__":  # pragma: no cover - invoked by Copier
    main()
