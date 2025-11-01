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


def _load_docs_site(default: str = "fumadocs") -> str:
    """Best-effort retrieval of the selected documentation variant."""

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
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            value = data.get("docs_site")
            if isinstance(value, str) and value:
                return value
    return default


def _load_ci_platform(default: str = "github-actions") -> str:
    """Best-effort retrieval of the selected CI platform."""

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
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            value = data.get("ci_platform")
            if isinstance(value, str) and value:
                return value
    return default


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


def main() -> None:
    docs_site = _load_docs_site()
    ci_platform = _load_ci_platform()

    tool_matrix: list[tuple[str, str, str | None]] = [
        ("uv", "0.4", "uv@0.4"),
    ]

    if docs_site != "none":
        tool_matrix.extend(
            [
                ("node", "20", "node@20"),
                ("pnpm", "8", "pnpm@8"),
            ]
        )
    
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

    failures: list[ProvisionResult] = []
    for tool, version, mise_spec in tool_matrix:
        result = _attempt_install(tool, version, mise_spec)
        _log_attempt(result)
        if result["status"] == "failed":
            failures.append(result)

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

    if failures:
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


if __name__ == "__main__":  # pragma: no cover - invoked by Copier
    main()
