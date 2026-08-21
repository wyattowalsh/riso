"""Maintainer workflows: pnpm 11 requires Node 22+ (node:sqlite)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

pytestmark = pytest.mark.unit


def _package_manager() -> str:
    data = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    return str(data.get("packageManager") or "")


def _pnpm_major(package_manager: str) -> int | None:
    if not package_manager.startswith("pnpm@"):
        return None
    version = package_manager.split("@", 1)[1]
    try:
        return int(version.split(".", 1)[0])
    except ValueError:
        return None


def _step_pnpm_action_major(step: dict) -> int | None:
    uses = str(step.get("uses") or "")
    if "pnpm/action-setup" not in uses:
        return None
    version = str((step.get("with") or {}).get("version") or "").strip()
    if not version:
        return None
    try:
        return int(version.split(".", 1)[0])
    except ValueError:
        return None


def _job_uses_pnpm11(job: dict, default_major: int | None) -> bool:
    steps = job.get("steps") or []
    saw_pnpm11_setup = False
    saw_older_pnpm_setup = False
    saw_corepack = False
    for step in steps:
        if not isinstance(step, dict):
            continue
        major = _step_pnpm_action_major(step)
        uses = str(step.get("uses") or "")
        if "pnpm/action-setup" in uses:
            if major == 11:
                saw_pnpm11_setup = True
            elif major is None and default_major == 11:
                saw_pnpm11_setup = True
            elif major is not None and major < 11:
                saw_older_pnpm_setup = True
        run = str(step.get("run") or "")
        if "corepack enable" in run:
            saw_corepack = True
    if saw_pnpm11_setup:
        return True
    return bool(saw_corepack and default_major == 11 and not saw_older_pnpm_setup)


def _job_node_version(job: dict) -> str | None:
    for step in job.get("steps") or []:
        if not isinstance(step, dict):
            continue
        if "actions/setup-node" not in str(step.get("uses") or ""):
            continue
        version = (step.get("with") or {}).get("node-version")
        if version is not None:
            return str(version).strip().strip("'\"")
    return None


def test_package_manager_is_pnpm_11() -> None:
    assert _pnpm_major(_package_manager()) == 11


def test_pnpm11_maintainer_jobs_pin_node_22() -> None:
    default_major = _pnpm_major(_package_manager())
    failures: list[str] = []
    scanned = 0
    for path in sorted(WORKFLOWS.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        jobs = data.get("jobs") or {}
        for name, job in jobs.items():
            if not isinstance(job, dict):
                continue
            if not _job_uses_pnpm11(job, default_major):
                continue
            scanned += 1
            node = _job_node_version(job)
            if node != "22" and not str(node or "").startswith("22."):
                failures.append(f"{path.name} / {name}: node-version={node!r}")
    assert scanned >= 1
    assert not failures, "pnpm 11 requires Node 22+ (node:sqlite):\n" + "\n".join(
        failures
    )
