#!/usr/bin/env python3
"""Validate the maintainer-only Riso release-readiness skill mirror."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / ".agents" / "skills" / "riso-release-readiness"
MIRROR_DIR = REPO_ROOT / ".claude" / "skills" / "riso-release-readiness"
REQUIRED_FILES = {
    "SKILL.md",
    "references/release-gates.md",
    "references/task-graph.md",
    "references/no-legacy-answer-policy.md",
    "scripts/collect_release_evidence.py",
}


def relative_files(directory: Path) -> set[str]:
    return {
        str(path.relative_to(directory))
        for path in directory.rglob("*")
        if path.is_file()
    }


def validate_frontmatter(skill_path: Path) -> list[str]:
    errors: list[str] = []
    text = skill_path.read_text()
    if not text.startswith("---\n"):
        return ["SKILL.md must start with YAML frontmatter"]
    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        return ["SKILL.md frontmatter must have opening and closing delimiters"]
    if "name: riso-release-readiness" not in frontmatter:
        errors.append("SKILL.md frontmatter must set name: riso-release-readiness")
    if "description:" not in frontmatter:
        errors.append("SKILL.md frontmatter must include description")
    if len(frontmatter) > 1200:
        errors.append("SKILL.md frontmatter is too large")
    if not body.strip():
        errors.append("SKILL.md must include body instructions")
    return errors


def validate_skill_mirror(
    source_dir: Path = SOURCE_DIR,
    mirror_dir: Path = MIRROR_DIR,
) -> list[str]:
    errors: list[str] = []
    if not source_dir.exists():
        return [f"Source skill directory missing: {source_dir}"]
    if not mirror_dir.exists():
        return [f"Mirror skill directory missing: {mirror_dir}"]

    source_files = relative_files(source_dir)
    mirror_files = relative_files(mirror_dir)
    missing = sorted(REQUIRED_FILES - source_files)
    if missing:
        errors.extend(f"Missing source skill file: {name}" for name in missing)
    if source_files != mirror_files:
        errors.append(
            "Skill source/mirror file sets differ: "
            f"source_only={sorted(source_files - mirror_files)} "
            f"mirror_only={sorted(mirror_files - source_files)}"
        )

    for name in sorted(source_files & mirror_files):
        source_file = source_dir / name
        mirror_file = mirror_dir / name
        if source_file.read_bytes() != mirror_file.read_bytes():
            errors.append(f"Skill mirror mismatch: {name}")

    skill_path = source_dir / "SKILL.md"
    if skill_path.exists():
        errors.extend(validate_frontmatter(skill_path))
    return errors


def main() -> None:
    errors = validate_skill_mirror()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print("Release readiness skill mirror is valid.")


if __name__ == "__main__":
    main()
