#!/usr/bin/env python3
"""Provision quality tooling (ruff, mypy, pylint, coverage) via uv tools."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List

QUALITY_TOOLS = ["ruff", "mypy", "pylint", "coverage"]


@dataclass
class ToolCheck:
    name: str
    status: str
    command: str
    stderr: str | None = None
    next_steps: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        return {k: v for k, v in payload.items() if v is not None}


def _run(command: Iterable[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
    )


def _ensure_tool(tool: str) -> ToolCheck:
    if shutil.which("uv") is None:
        return ToolCheck(
            name=tool,
            status="uv-missing",
            command="uv",
            next_steps="Install uv from https://github.com/astral-sh/uv",
        )
    check = _run(["uv", "tool", "run", tool, "--version"])
    if check.returncode == 0:
        return ToolCheck(name=tool, status="present", command="uv tool run")
    install = _run(["uv", "tool", "install", tool])
    if install.returncode == 0:
        return ToolCheck(name=tool, status="installed", command="uv tool install")
    stderr = install.stderr or install.stdout
    return ToolCheck(
        name=tool,
        status="failed",
        command="uv tool install",
        stderr=stderr.strip(),
        next_steps=f"Install {tool} manually or ensure uv can install it.",
    )


def ensure_python_quality_tools() -> List[ToolCheck]:
    return [_ensure_tool(tool) for tool in QUALITY_TOOLS]


def ensure_node_quality_tools(required: bool) -> List[ToolCheck]:
    if not required:
        return [
            ToolCheck(
                name="pnpm",
                status="skipped",
                command="corepack pnpm install",
                next_steps="Node API track disabled; skipping pnpm quality provisioning.",
            )
        ]

    if shutil.which("pnpm") is None:
        enable = _run(["corepack", "enable"])
        if enable.returncode != 0:
            stderr = enable.stderr or enable.stdout
            return [
                ToolCheck(
                    name="pnpm",
                    status="failed",
                    command="corepack enable",
                    stderr=stderr.strip(),
                    next_steps="Ensure corepack is available to manage pnpm (Node.js 18+).",
                )
            ]

    install = _run(["corepack", "pnpm", "install"])
    if install.returncode == 0:
        return [
            ToolCheck(
                name="pnpm",
                status="installed",
                command="corepack pnpm install",
            )
        ]
    stderr = install.stderr or install.stdout
    return [
        ToolCheck(
            name="pnpm",
            status="failed",
            command="corepack pnpm install",
            stderr=stderr.strip(),
            next_steps="Run pnpm install manually before re-running quality commands.",
        )
    ]


def write_metadata(destination: Path, checks: List[ToolCheck]) -> None:
    payload = [check.to_dict() for check in checks]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")

__all__ = [
    "ToolCheck",
    "ensure_python_quality_tools",
    "ensure_node_quality_tools",
    "write_metadata",
]
