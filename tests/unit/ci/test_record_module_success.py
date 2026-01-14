"""Unit tests for record_module_success.py"""

import json
import pytest


pytestmark = pytest.mark.usefixtures("ci_scripts_path")


@pytest.mark.unit
class TestModuleStats:
    """Tests for ModuleStats dataclass."""

    def test_initial_state_zeros(self):
        """New ModuleStats should have zero counts."""
        from record_module_success import ModuleStats

        stats = ModuleStats()
        assert stats.passed == 0
        assert stats.failed == 0
        assert stats.errored == 0
        assert stats.skipped == 0

    def test_total_sums_passed_failed_errored(self):
        """Total should sum passed, failed, and errored (excludes skipped)."""
        from record_module_success import ModuleStats

        stats = ModuleStats(passed=5, failed=2, errored=1, skipped=3)
        assert stats.total() == 8  # 5 + 2 + 1, skipped not included

    def test_success_rate_normal_case(self):
        """Success rate should be passed/total."""
        from record_module_success import ModuleStats

        stats = ModuleStats(passed=8, failed=2)
        assert stats.success_rate() == pytest.approx(0.8)

    def test_success_rate_zero_total(self):
        """Success rate should be 0.0 when total is 0."""
        from record_module_success import ModuleStats

        stats = ModuleStats()
        assert stats.success_rate() == 0.0

    def test_success_rate_all_passed(self):
        """Success rate should be 1.0 when all passed."""
        from record_module_success import ModuleStats

        stats = ModuleStats(passed=10)
        assert stats.success_rate() == 1.0

    def test_success_rate_all_failed(self):
        """Success rate should be 0.0 when all failed."""
        from record_module_success import ModuleStats

        stats = ModuleStats(failed=10)
        assert stats.success_rate() == 0.0

    def test_to_dict_includes_computed_values(self):
        """to_dict should include all fields plus computed values."""
        from record_module_success import ModuleStats

        stats = ModuleStats(passed=5, failed=2, errored=1, skipped=2)
        d = stats.to_dict()
        assert d["passed"] == 5
        assert d["failed"] == 2
        assert d["errored"] == 1
        assert d["skipped"] == 2
        assert d["total_recorded"] == 8  # passed + failed + errored
        assert d["success_rate"] == pytest.approx(0.625, abs=0.0001)  # 5/8


@pytest.mark.unit
class TestModuleSuccessRecorder:
    """Tests for ModuleSuccessRecorder class."""

    def test_empty_recorder(self):
        """Empty recorder should have no modules."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        assert len(recorder.modules) == 0

    def test_record_passed_result(self):
        """Should record passed results correctly."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.record("cli", "passed", "default")
        assert "cli" in recorder.modules
        assert recorder.modules["cli"].passed == 1

    def test_record_failed_result(self):
        """Should record failed results correctly."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.record("api", "failed", "default")
        assert recorder.modules["api"].failed == 1

    def test_record_multiple_variants(self):
        """Should accumulate across variants."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.record("api", "passed", "variant1")
        recorder.record("api", "passed", "variant2")
        recorder.record("api", "failed", "variant3")
        assert recorder.modules["api"].passed == 2
        assert recorder.modules["api"].failed == 1

    def test_record_multiple_modules(self):
        """Should track multiple modules independently."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.record("cli", "passed", "v1")
        recorder.record("api", "failed", "v1")
        recorder.record("docs", "skipped", "v1")
        assert recorder.modules["cli"].passed == 1
        assert recorder.modules["api"].failed == 1
        assert recorder.modules["docs"].skipped == 1

    def test_write_creates_valid_json(self, tmp_path):
        """Should write valid JSON file."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.record("test_module", "passed", "v1")
        recorder.record("test_module", "failed", "v2")

        output_path = tmp_path / "success.json"
        recorder.write(output_path)

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert "modules" in data
        assert "test_module" in data["modules"]
        assert data["modules"]["test_module"]["passed"] == 1
        assert data["modules"]["test_module"]["failed"] == 1

    def test_write_includes_success_rate(self, tmp_path):
        """Written JSON should include success rate."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.record("mod", "passed", "v1")
        recorder.record("mod", "passed", "v2")

        output_path = tmp_path / "success.json"
        recorder.write(output_path)

        data = json.loads(output_path.read_text())
        assert data["modules"]["mod"]["success_rate"] == 1.0


@pytest.mark.unit
class TestWorkflowValidation:
    """Tests for workflow validation tracking."""

    def test_update_workflow_validation_pass(self):
        """Should increment passed on 'pass' status."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_workflow_validation("pass")
        assert recorder.workflow_stats.passed == 1
        assert recorder.workflow_stats.failed == 0
        assert recorder.workflow_stats.skipped == 0

    def test_update_workflow_validation_fail(self):
        """Should increment failed on 'fail' status."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_workflow_validation("fail")
        assert recorder.workflow_stats.passed == 0
        assert recorder.workflow_stats.failed == 1

    def test_update_workflow_validation_unknown(self):
        """Should increment skipped on unknown status."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_workflow_validation("unknown")
        recorder.update_workflow_validation("skipped")
        assert recorder.workflow_stats.skipped == 2


@pytest.mark.unit
class TestContainerStatus:
    """Tests for container status tracking."""

    def test_update_container_status_files_present(self):
        """Should track files_present status."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_container_status("files_present")
        assert recorder.container_metrics.files_present == 1
        assert recorder.container_metrics.total_checked == 1

    def test_update_container_status_validated(self):
        """Should track validated status and calculate success rate."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_container_status("validated")
        assert recorder.container_metrics.validated == 1
        assert recorder.container_metrics.success_rate == 1.0

    def test_update_container_status_lint_errors(self):
        """Should track lint_errors status."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_container_status("lint_errors")
        assert recorder.container_metrics.lint_errors == 1

    def test_update_container_status_files_missing(self):
        """Should track files_missing status."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_container_status("files_missing")
        assert recorder.container_metrics.files_missing == 1

    def test_update_container_status_not_applicable(self):
        """Should track not_applicable status."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_container_status("not_applicable")
        assert recorder.container_metrics.not_applicable == 1
        # Not applicable shouldn't count toward success rate
        assert recorder.container_metrics.success_rate == 0.0

    def test_container_success_rate_calculation(self):
        """Should calculate success rate excluding not_applicable."""
        from record_module_success import ModuleSuccessRecorder

        recorder = ModuleSuccessRecorder()
        recorder.update_container_status("validated")
        recorder.update_container_status("validated")
        recorder.update_container_status("lint_errors")
        recorder.update_container_status("not_applicable")
        # 2 validated out of 3 applicable (4 total - 1 not_applicable)
        assert recorder.container_metrics.success_rate == pytest.approx(2 / 3, rel=0.01)
