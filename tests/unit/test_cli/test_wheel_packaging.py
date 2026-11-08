"""Wheel packaging: Copier template must ship in the installed distribution."""

from __future__ import annotations

import json
import os
import sys
import tarfile
import textwrap
import zipfile
from pathlib import Path

import pytest

from riso.core.paths import PACKAGED_TEMPLATE_DIRNAME
from riso.template._copier_worker import run_argv_with_timeout

pytestmark = pytest.mark.unit

_REPO_ROOT = Path(__file__).resolve().parents[3]
_WHEEL_COPIER = f"riso/{PACKAGED_TEMPLATE_DIRNAME}/copier.yml"
_WHEEL_PRE_GEN = f"riso/{PACKAGED_TEMPLATE_DIRNAME}/hooks/pre_gen_project.py"


@pytest.fixture(scope="module", name="built_dist")
def _built_dist(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build sdist+wheel the same way Release CI does (``uv build --no-sources``)."""
    dist = tmp_path_factory.mktemp("dist")
    proc = run_argv_with_timeout(
        ["uv", "build", "--no-sources", "--out-dir", str(dist)],
        cwd=_REPO_ROOT,
        timeout=120,
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
    """The source archive retains the Copier template inputs."""
    sdists = sorted(built_dist.glob("*.tar.gz"))
    assert sdists, f"no sdist in {built_dist}"
    with tarfile.open(sdists[0], "r:gz") as archive:
        names = archive.getnames()
    assert any(name.endswith("template/copier.yml") for name in names), names[:20]


def test_wheel_includes_copier_template(built_dist: Path) -> None:
    """The installed wheel retains configuration and the explicit pre-gen helper."""
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
    proc = run_argv_with_timeout(
        [
            "uv",
            "run",
            "--isolated",
            "--python",
            sys.executable,
            "--with",
            str(wheel),
            "riso",
            "doctor",
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        timeout=120,
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


def test_isolated_wheel_copy_and_recopy_run_normal_hooks(
    built_dist: Path, tmp_path: Path
) -> None:
    """Installed generation exercises packaged post-gen helper imports end to end."""
    script = tmp_path / "installed_generation.py"
    script.write_text(
        textwrap.dedent(
            """\
            import json
            import sys
            from pathlib import Path

            import yaml
            import riso.cli
            from riso.template._copier_worker import run_argv_with_timeout

            def invoke(*args):
                result = run_argv_with_timeout(
                    [sys.executable, "-m", "riso.cli", "--json", *args],
                    cwd=Path.cwd(),
                    timeout=90,
                )
                assert result.returncode == 0, result.stderr or result.stdout
                payload = json.loads(result.stdout)
                assert payload["ok"] is True, payload

            answers = Path("answers.yml")
            answers.write_text(yaml.safe_dump({
                "project_name": "riso-installed-smoke",
                "cli_module": "enabled",
                "cli_languages": ["python"],
                "api_module": "disabled",
                "mcp_module": "disabled",
                "docs_module": "disabled",
                "desktop_module": "disabled",
                "saas_infra_module": "disabled",
                "ai_tools_module": "disabled",
                "quality_profile": "standard",
            }), encoding="utf-8")
            destination = Path("generated").resolve()
            invoke("copy", str(destination), "--answers-file", str(answers))
            metadata_path = destination / ".riso" / "post_gen_metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            assert metadata["modules"]["cli_module"] == "enabled"

            invoke(
                "recopy", str(destination),
                "--data", "project_name=riso-installed-renamed",
                "--data", "cli_module=disabled",
            )
            stored = yaml.safe_load(
                (destination / ".copier-answers.yml").read_text(encoding="utf-8")
            )
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            assert stored["project_name"] == "riso-installed-renamed"
            assert stored["cli_module"] == "disabled"
            assert metadata["modules"]["cli_module"] == "disabled"
            print(json.dumps({
                "installed_module": str(Path(riso.cli.__file__).resolve()),
                "normal_copy_and_recopy": True,
            }))
            """
        ),
        encoding="utf-8",
    )
    env = os.environ.copy()
    for key in (
        "RISO_TEMPLATE_PATH",
        "RISO_SAMPLES_PATH",
        "RISO_SKIP_POST_GEN",
        "RISO_POST_GEN_INSTALL_TOOLS",
        "RISO_STRICT_HOOKS",
        "PYTHONPATH",
    ):
        env.pop(key, None)
    result = run_argv_with_timeout(
        [
            "uv",
            "run",
            "--isolated",
            "--python",
            sys.executable,
            "--with",
            str(_wheel_path(built_dist)),
            "python",
            str(script),
        ],
        cwd=tmp_path,
        env=env,
        timeout=240,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["normal_copy_and_recopy"] is True
    assert not Path(payload["installed_module"]).is_relative_to(_REPO_ROOT)
