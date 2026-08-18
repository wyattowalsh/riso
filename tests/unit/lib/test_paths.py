"""Nested sample discovery via scripts.lib.paths (CLI list_sample_variants is one-level).

NOTE for the CLI team: ``riso.template.list_sample_variants`` currently scans
only immediate children of ``samples/``. Nested presets such as
``samples/saas-starter/*/copier-answers.yml`` are discovered here. Recurse the
same way as ``iter_sample_answer_files`` so ``riso variants list`` includes them.
Do not edit ``src/riso`` from the docs/samples lane.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.lib.paths import (
    iter_sample_answer_files,
    repo_root,
    samples_dir,
)

pytestmark = pytest.mark.unit


def test_iter_sample_answer_files_finds_nested_saas_starter_variants() -> None:
    """Pruned walk must include nested saas-starter copier-answers.yml files."""
    files = iter_sample_answer_files(samples_dir())
    rel = {path.relative_to(samples_dir()).as_posix() for path in files}

    assert "saas-starter/enterprise-ready/copier-answers.yml" in rel
    assert "saas-starter/vercel-starter/copier-answers.yml" in rel
    assert "saas-starter/b2b-teams-full/copier-answers.yml" in rel

    nested_saas = [
        path
        for path in rel
        if path.startswith("saas-starter/") and path.endswith("copier-answers.yml")
    ]
    assert len(nested_saas) >= 11


def test_iter_sample_answer_files_skips_render_and_metadata(
    tmp_path: Path,
) -> None:
    """Walk must not enter render/ or metadata/ trees."""
    samples = tmp_path / "samples"
    (samples / "default").mkdir(parents=True)
    (samples / "default" / "copier-answers.yml").write_text(
        "project_name: Default\n", encoding="utf-8"
    )
    (samples / "saas-starter" / "nested").mkdir(parents=True)
    (samples / "saas-starter" / "nested" / "copier-answers.yml").write_text(
        "project_name: Nested\n", encoding="utf-8"
    )
    (samples / "default" / "render").mkdir()
    (samples / "default" / "render" / "copier-answers.yml").write_text(
        "project_name: RenderLeak\n", encoding="utf-8"
    )
    (samples / "metadata").mkdir()
    (samples / "metadata" / "copier-answers.yml").write_text(
        "project_name: MetaLeak\n", encoding="utf-8"
    )

    found = {
        path.relative_to(samples).as_posix()
        for path in iter_sample_answer_files(samples)
    }
    assert found == {
        "default/copier-answers.yml",
        "saas-starter/nested/copier-answers.yml",
    }


def test_samples_dir_is_repo_samples() -> None:
    """samples_dir() must resolve to <repo>/samples."""
    assert samples_dir() == repo_root() / "samples"
    assert samples_dir().is_dir()
