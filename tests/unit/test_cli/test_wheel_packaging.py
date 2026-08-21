"""Wheel packaging: Copier template must ship in the installed distribution."""

from __future__ import annotations

import json
import os
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

from riso.core.paths import PACKAGED_TEMPLATE_DIRNAME

pytestmark = pytest.mark.unit

_REPO_ROOT = Path(__file__).resolve().parents[3]
_WHEEL_COPIER = f"riso/{PACKAGED_TEMPLATE_DIRNAME}/copier.yml"
_WHEEL_PRE_GEN = f"riso/{PACKAGED_TEMPLATE_DIRNAME}/hooks/pre_gen_project.py"


@pytest.fixture(scope="module")
def built_dist(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build sdist+wheel the same way Release CI does (``uv build --no-sources``)."""
    dist = tmp_path_factory.mktemp("dist")
    proc = subprocess.run(
        ["uv", "build", "--no-sources", "--out-dir", str(dist)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(
            "uv build --no-sources failed\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return dist


def _wheel_path(dist: Path) -> Path:
    wheels = sorted(dist.glob("*.whl"))
    assert wheels, f"no wheel in {dist}"
    return wheels[0]


def test_sdist_includes_checkout_template(built_dist: Path) -> None:
    sdists = sorted(built_dist.glob("*.tar.gz"))
    assert sdists, f"no sdist in {built_dist}"
    with tarfile.open(sdists[0], "r:gz") as archive:
        names = archive.getnames()
    assert any(name.endswith("template/copier.yml") for name in names), names[:20]


def test_wheel_includes_copier_template(built_dist: Path) -> None:
    with zipfile.ZipFile(_wheel_path(built_dist)) as archive:
        names = archive.namelist()
    assert _WHEEL_COPIER in names
    assert _WHEEL_PRE_GEN in names


def test_isolated_wheel_doctor_finds_template(built_dist: Path, tmp_path: Path) -> None:
    """Reproduce Release 'Smoke test wheel install' without a GitHub runner."""
    wheel = _wheel_path(built_dist)
    env = os.environ.copy()
    env.pop("RISO_TEMPLATE_PATH", None)
    env.pop("RISO_SAMPLES_PATH", None)
    proc = subprocess.run(
        [
            "uv",
            "run",
            "--isolated",
            "--with",
            str(wheel),
            "riso",
            "doctor",
            "--json",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        pytest.fail(
            "riso doctor --json did not emit JSON\n"
            f"exit={proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    checks = payload["data"]["checks"]
    assert checks["template_exists"] is True, payload
    assert checks.get("copier_config_valid") is True, payload
    assert payload["data"]["ready"] is True, payload
    assert proc.returncode == 0
    assert PACKAGED_TEMPLATE_DIRNAME in str(checks["template_path"])
