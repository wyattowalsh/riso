"""Validate rendered sample projects for pre-commit layout (DG-1 Option A).

Checks that `.pre-commit-config.yaml` lives at the project root, hook install
metadata is consistent, and legacy root `pyproject.toml` stubs are absent when
`python/pyproject.toml` is the canonical manifest.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = REPO_ROOT / "samples"

PYTHON_VARIANTS = (
    "changelog-python",
    "full-stack",
    "api-python",
    "gitlab-ci-python",
    "default",
)


def python_enabled(answers: dict[str, object]) -> bool:
    cli = str(answers.get("cli_module", "disabled")).lower() == "enabled"
    cli_langs = answers.get("cli_languages", [])
    api = str(answers.get("api_module", "disabled")).lower() == "enabled"
    api_langs = answers.get("api_languages", [])
    mcp = str(answers.get("mcp_module", "disabled")).lower() == "enabled"
    mcp_langs = answers.get("mcp_languages", [])

    def has_python(langs: object) -> bool:
        if isinstance(langs, list):
            return "python" in [str(item).lower() for item in langs]
        return "python" in str(langs).lower()

    return (
        (cli and has_python(cli_langs))
        or (api and has_python(api_langs))
        or (mcp and has_python(mcp_langs))
    )


def load_answers(variant_dir: Path) -> dict[str, object]:
    answers_path = variant_dir / "copier-answers.yml"
    if not answers_path.exists():
        return {}
    data = yaml.safe_load(answers_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def validate_render(render_dir: Path, answers: dict[str, object]) -> list[str]:
    errors: list[str] = []
    precommit = render_dir / ".pre-commit-config.yaml"
    if not precommit.exists():
        errors.append("missing root .pre-commit-config.yaml")
    else:
        try:
            config = yaml.safe_load(precommit.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"invalid .pre-commit-config.yaml: {exc}")
        else:
            if not isinstance(config, dict) or "repos" not in config:
                errors.append(".pre-commit-config.yaml missing repos key")

    root_makefile = render_dir / "Makefile"
    quality_makefile = render_dir / "quality" / "makefile.quality"
    if not root_makefile.exists():
        errors.append("missing root Makefile")
    elif "quality/makefile.quality" not in root_makefile.read_text(encoding="utf-8"):
        errors.append("root Makefile does not delegate to quality/makefile.quality")
    if not quality_makefile.exists():
        errors.append("missing quality/makefile.quality")
    elif "hooks:" not in quality_makefile.read_text(encoding="utf-8"):
        errors.append("quality/makefile.quality missing hooks target")

    metadata_path = render_dir / ".riso" / "post_gen_metadata.json"
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        pre_commit = metadata.get("pre_commit", {})
        install_cmd = pre_commit.get("install_command", "")
        if install_cmd != "make hooks":
            errors.append(
                f"pre_commit.install_command expected 'make hooks', got {install_cmd!r}"
            )

    if python_enabled(answers):
        python_pyproject = render_dir / "python" / "pyproject.toml"
        root_pyproject = render_dir / "pyproject.toml"
        if not python_pyproject.exists():
            errors.append("missing python/pyproject.toml")
        if root_pyproject.exists():
            content = root_pyproject.read_text(encoding="utf-8")
            if "[tool.uv.tasks]" in content and "[project]" not in content:
                errors.append("legacy root pyproject.toml stub still present")

    return errors


def discover_variants() -> list[str]:
    variants: list[str] = []
    if not SAMPLES_DIR.is_dir():
        return variants
    for answers_file in sorted(SAMPLES_DIR.rglob("copier-answers.yml")):
        if answers_file.parent.name == "metadata":
            continue
        variant = answers_file.parent.relative_to(SAMPLES_DIR).as_posix()
        render_dir = answers_file.parent / "render"
        if render_dir.is_dir():
            variants.append(variant)
    return variants


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate every sample variant that has a render/ directory",
    )
    parser.add_argument(
        "--variants",
        nargs="*",
        default=None,
        help="Sample variant names under samples/ (default: common Python variants)",
    )
    args = parser.parse_args()

    if args.all:
        variant_list = discover_variants()
    elif args.variants:
        variant_list = list(args.variants)
    else:
        variant_list = list(PYTHON_VARIANTS)

    failures: list[str] = []
    checked = 0
    for variant in variant_list:
        variant_dir = SAMPLES_DIR / variant
        render_dir = variant_dir / "render"
        if not render_dir.is_dir():
            failures.append(
                f"{variant}: render directory missing (run render-samples.sh)"
            )
            continue
        answers = load_answers(variant_dir)
        errors = validate_render(render_dir, answers)
        checked += 1
        if errors:
            failures.append(f"{variant}: " + "; ".join(errors))

    if failures:
        for failure in failures:
            sys.stderr.write(f"[precommit-render] {failure}\n")
        return 1

    sys.stdout.write(f"Pre-commit render checks passed ({checked} variants).\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
