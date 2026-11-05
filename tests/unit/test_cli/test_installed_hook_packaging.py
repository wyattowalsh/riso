"""Exercise packaged hook imports and execution from outside the checkout."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml


def test_packaged_post_gen_includes_its_runtime_helpers(tmp_path: Path) -> None:
    """The wheel layout runs post-gen with its required helpers outside a checkout."""
    root = Path(__file__).resolve().parents[3]
    site = tmp_path / "site-packages"
    shutil.copytree(
        root / "src/riso", site / "riso", ignore=shutil.ignore_patterns("__pycache__")
    )
    config = tomllib.loads((root / "pyproject.toml").read_text())
    includes = config["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]
    for source, target in includes.items():
        source_path, target_path = root / source, site / target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.is_dir():
            shutil.copytree(
                source_path, target_path, ignore=shutil.ignore_patterns("__pycache__")
            )
        else:
            shutil.copyfile(source_path, target_path)

    dest = tmp_path / "project"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        yaml.safe_dump(
            {
                "project_name": "packaged-demo",
                "package_name": "packaged_demo",
                "docs_module": "disabled",
                "ci_platform": "none",
                "api_module": "disabled",
                "quality_profile": "standard",
            }
        )
    )
    child_env = os.environ.copy()
    child_env.update(
        {
            "PYTHONPATH": str(site),
            "RISO_POST_GEN_INSTALL_TOOLS": "0",
            "RISO_STRICT_HOOKS": "0",
        }
    )
    completed = subprocess.run(
        [sys.executable, str(site / "riso/copier_template/hooks/post_gen_project.py")],
        cwd=dest,
        env=child_env,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    metadata = json.loads((dest / ".riso/post_gen_metadata.json").read_text())
    assert metadata["quality"]["profile"] == "standard"
