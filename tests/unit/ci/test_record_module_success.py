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
