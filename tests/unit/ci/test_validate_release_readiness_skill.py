"""Tests for validate_release_readiness_skill.py."""

from __future__ import annotations

import pytest

from validate_release_readiness_skill import (
    REQUIRED_FILES,
    validate_frontmatter,
    validate_skill_mirror,
)


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


def copy_skill_fixture(tmp_path):
    source = tmp_path / ".agents" / "skills" / "riso-release-readiness"
    mirror = tmp_path / ".claude" / "skills" / "riso-release-readiness"
    for directory in (source, mirror):
        (directory / "references").mkdir(parents=True)
        (directory / "scripts").mkdir(parents=True)
        for name in REQUIRED_FILES:
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if name == "SKILL.md":
                path.write_text(
                    "---\n"
                    "name: riso-release-readiness\n"
                    "description: Validate Riso release readiness.\n"
                    "---\n"
                    "\n"
                    "# Instructions\n"
                )
            else:
                path.write_text(f"# {name}\n")
    return source, mirror


def test_validate_skill_mirror_accepts_matching_fixture(tmp_path):
    source, mirror = copy_skill_fixture(tmp_path)

    assert validate_skill_mirror(source, mirror) == []


def test_validate_skill_mirror_reports_mismatch(tmp_path):
    source, mirror = copy_skill_fixture(tmp_path)
    (mirror / "references" / "release-gates.md").write_text("changed\n")

    assert (
        "Skill mirror mismatch: references/release-gates.md"
        in validate_skill_mirror(source, mirror)
    )


def test_validate_frontmatter_requires_name(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\ndescription: Missing name.\n---\n\n# Body\n")

    errors = validate_frontmatter(skill)

    assert "SKILL.md frontmatter must set name: riso-release-readiness" in errors


def test_repository_skill_mirror_is_valid():
    assert validate_skill_mirror() == []
