"""Unit tests for scripts/ci/run_quality_suite.py pure helpers and profile wiring."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from run_quality_suite import (
    PYTHON_TARGETS,
    STRICT_ONLY,
    main,
    write_results,
)

pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestWriteResults:
    def test_writes_profile_and_durations_json(self, tmp_path: Path) -> None:
        log_dir = tmp_path / "logs"
        write_results(log_dir, "standard", {"ruff": 1.25, "ty": 2.5})

        payload = json.loads(
            (log_dir / "quality-results.json").read_text(encoding="utf-8")
        )
        assert payload["profile"] == "standard"
        assert payload["durations"]["ruff"] == 1.25
        assert payload["durations"]["ty"] == 2.5


@pytest.mark.unit
class TestProfileMatrix:
    def test_standard_targets_include_scripts_and_src(self) -> None:
        assert "scripts" in PYTHON_TARGETS
        assert "src" in PYTHON_TARGETS
        assert "pylint" in STRICT_ONLY

    @patch("run_quality_suite.write_results")
    @patch("run_quality_suite.run_command", return_value=0.1)
    @patch("run_quality_suite.configure_logging")
    def test_standard_profile_skips_pylint(
        self, _log, mock_run, mock_write, tmp_path: Path
    ) -> None:
        with patch(
            "sys.argv",
            [
                "run_quality_suite.py",
                "--profile",
                "standard",
                "--log-dir",
                str(tmp_path),
            ],
        ):
            main()

        joined = [" ".join(call.args[0]) for call in mock_run.call_args_list]
        assert any("ruff" in cmd for cmd in joined)
        assert any("ty" in cmd for cmd in joined)
        assert not any("pylint" in cmd for cmd in joined)
        mock_write.assert_called_once()
        assert mock_write.call_args.args[1] == "standard"

    @patch("run_quality_suite.write_results")
    @patch("run_quality_suite.run_command", return_value=0.1)
    @patch("run_quality_suite.configure_logging")
    def test_strict_profile_runs_pylint(
        self, _log, mock_run, mock_write, tmp_path: Path
    ) -> None:
        with patch(
            "sys.argv",
            ["run_quality_suite.py", "--profile", "strict", "--log-dir", str(tmp_path)],
        ):
            main()

        joined = [" ".join(call.args[0]) for call in mock_run.call_args_list]
        assert any("pylint" in cmd for cmd in joined)
        mock_write.assert_called_once()
        assert mock_write.call_args.args[1] == "strict"
