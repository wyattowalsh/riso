"""Final release assets must be built after the selected version is applied."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("build_fails", [False, True])
def test_prepare_builds_selected_version_and_stops_on_failure(tmp_path, build_fails):
    """Verify prepare builds selected version and stops on failure."""
    config = yaml.safe_load((REPO_ROOT / ".releaserc.yml").read_text(encoding="utf-8"))
    command = next(
        plugin[1]["prepareCmd"]
        for plugin in config["plugins"]
        if isinstance(plugin, list) and plugin[0] == "@semantic-release/exec"
    ).replace("${nextRelease.version}", "2.0.0")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "riso"\nversion = "1.2.11"\n', encoding="utf-8"
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text(
        "#!/bin/sh\n"
        'printf "%s\\n" "$*" >> "$RISO_PREPARE_LOG"\n'
        'if [ "$1" = "build" ]; then\n'
        '  cat pyproject.toml >> "$RISO_PREPARE_LOG"\n'
        '  exit "$RISO_BUILD_EXIT"\n'
        "fi\n",
        encoding="utf-8",
    )
    uv.chmod(0o755)
    log = tmp_path / "prepare.log"
    result = subprocess.run(
        ["sh", "-c", command],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.defpath}",
            "RISO_PREPARE_LOG": str(log),
            "RISO_BUILD_EXIT": "1" if build_fails else "0",
        },
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    evidence = log.read_text(encoding="utf-8")
    assert "build --no-sources --clear" in evidence
    assert 'version = "2.0.0"' in evidence
    assert ("twine check" in evidence) is not build_fails
    assert (result.returncode != 0) is build_fails
