"""Integration-style tests for generation control plane (no network/copier)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from riso.core.errors import ValidationFailedError
from riso.template import run_generator, run_update


@pytest.mark.unit
def test_run_generator_rejects_removed_keys_before_worker(tmp_path: Path) -> None:
    """Generation rejects unsupported removed answers before any Copier work."""
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(ValidationFailedError):
            run_generator(
                destination=tmp_path / "out",
                data={"saas_auth": "firebase", "project_name": "demo"},
                template_path=tmp_path,
                skip_post_gen=True,
            )
        worker.assert_not_called()


@pytest.mark.unit
def test_run_update_rejects_saas_incompat_before_worker(tmp_path: Path) -> None:
    """Update rejects incompatible stored SaaS answers before any Copier work."""
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / ".copier-answers.yml").write_text(
        "saas_infra_module: enabled\n"
        "saas_database: neon\n"
        "saas_storage: supabase-storage\n",
        encoding="utf-8",
    )
    with patch("riso.template._run_copier_worker") as worker:
        with pytest.raises(ValidationFailedError):
            run_update(
                destination=dest,
                template_path=tmp_path / "template",
                skip_post_gen=True,
            )
        worker.assert_not_called()


@pytest.mark.unit
def test_smoke_schema_failure_count_integration() -> None:
    """The checkout smoke loader counts recorded failures across import layouts."""
    repo = Path(__file__).resolve().parents[2]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    # Both imports must follow this test's checkout-specific sys.path setup.
    # pylint: disable=import-outside-toplevel
    try:
        from scripts.lib.smoke_schema import failure_count, load_smoke
    except ModuleNotFoundError:
        scripts = repo / "scripts"
        sys.path.insert(0, str(scripts))
        from lib.smoke_schema import failure_count, load_smoke  # type: ignore[no-redef]

    fixtures = Path(__file__).resolve().parents[1] / "fixtures" / "json_samples"
    payload = load_smoke(fixtures / "smoke_results_failures.json")
    assert failure_count(payload) >= 1
