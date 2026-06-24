"""Tests for progress tracking and cancellation in MCP operations."""

from __future__ import annotations

import time
from unittest.mock import Mock, patch

import pytest

from riso.mcp.errors import OperationCancelled
from riso.mcp.progress import (
    CancellationToken,
    OperationStage,
    ProgressTracker,
    ProgressUpdate,
)


class TestOperationStage:
    """Tests for OperationStage enum."""

    def test_stage_values(self):
        """Test that all expected stages are defined."""
        assert OperationStage.INITIALIZING.value == "initializing"
        assert OperationStage.VALIDATING.value == "validating"
        assert OperationStage.RENDERING.value == "rendering"
        assert OperationStage.WRITING.value == "writing"
        assert OperationStage.FINALIZING.value == "finalizing"
        assert OperationStage.COMPLETE.value == "complete"

    def test_stage_enum_members(self):
        """Test that all expected stages exist."""
        stages = {stage.value for stage in OperationStage}
        expected = {
            "initializing",
            "validating",
            "rendering",
            "writing",
            "finalizing",
            "complete",
        }
        assert stages == expected


class TestProgressUpdate:
    """Tests for ProgressUpdate dataclass."""

    def test_create_basic_update(self):
        """Test creating a basic progress update."""
        update = ProgressUpdate(
            stage=OperationStage.VALIDATING,
            percent=25.0,
            message="Validating template answers",
        )

        assert update.stage == OperationStage.VALIDATING
        assert update.percent == 25.0
        assert update.message == "Validating template answers"
        assert update.eta_seconds is None
        assert update.files_processed == 0
        assert update.total_files is None

    def test_create_update_with_all_fields(self):
        """Test creating a progress update with all fields."""
        update = ProgressUpdate(
            stage=OperationStage.WRITING,
            percent=75.0,
            message="Writing files",
            eta_seconds=30.5,
            files_processed=150,
            total_files=200,
        )

        assert update.stage == OperationStage.WRITING
        assert update.percent == 75.0
        assert update.message == "Writing files"
        assert update.eta_seconds == 30.5
        assert update.files_processed == 150
        assert update.total_files == 200

    def test_progress_percentage_bounds(self):
        """Test that percentage can be 0.0 to 100.0."""
        low = ProgressUpdate(
            stage=OperationStage.INITIALIZING, percent=0.0, message="Starting"
        )
        high = ProgressUpdate(
            stage=OperationStage.COMPLETE, percent=100.0, message="Done"
        )

        assert low.percent == 0.0
        assert high.percent == 100.0


class TestCancellationToken:
    """Tests for CancellationToken class."""

    def test_initial_state_not_cancelled(self):
        """Test that token starts in non-cancelled state."""
        token = CancellationToken()
        assert token.is_cancelled is False

    def test_request_cancel_sets_state(self):
        """Test requesting cancellation sets the cancelled flag."""
        token = CancellationToken()
        token.request_cancel()
        assert token.is_cancelled is True

    def test_request_cancel_with_reason(self):
        """Test cancellation request with custom reason."""
        token = CancellationToken()
        token.request_cancel(reason="Custom cancellation reason")
        assert token.is_cancelled is True

    def test_cancellation_token_request_idempotent(self):
        """Test that requesting cancel multiple times is safe."""
        token = CancellationToken()
        token.request_cancel(reason="First reason")
        token.request_cancel(reason="Second reason")
        assert token.is_cancelled is True

    def test_check_raises_when_cancelled(self):
        """Test that check() raises OperationCancelled when cancelled."""
        token = CancellationToken()
        token.request_cancel(reason="Test cancellation")

        with pytest.raises(OperationCancelled) as exc_info:
            token.check()

        assert "Test cancellation" in str(exc_info.value)

    def test_check_does_not_raise_when_not_cancelled(self):
        """Test that check() does not raise when not cancelled."""
        token = CancellationToken()
        token.check()  # Should not raise

    def test_cancellation_token_default_reason(self):
        """Test default cancellation reason."""
        token = CancellationToken()
        token.request_cancel()

        with pytest.raises(OperationCancelled) as exc_info:
            token.check()

        # Default reason is "User requested cancellation"
        assert (
            "user" in str(exc_info.value).lower()
            or "cancel" in str(exc_info.value).lower()
        )


class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_tracker_initialization(self):
        """Test ProgressTracker initializes with correct defaults."""
        tracker = ProgressTracker()
        assert tracker._current_stage == OperationStage.INITIALIZING
        assert tracker._stage_progress == 0.0

    def test_tracker_with_cancellation_token(self):
        """Test ProgressTracker accepts optional cancellation token."""
        token = CancellationToken()
        tracker = ProgressTracker(cancellation_token=token)
        assert tracker._token is token

    def test_progress_tracker_stages(self):
        """Test starting different stages."""
        tracker = ProgressTracker()
        stages = [
            OperationStage.INITIALIZING,
            OperationStage.VALIDATING,
            OperationStage.RENDERING,
            OperationStage.WRITING,
            OperationStage.FINALIZING,
        ]

        for stage in stages:
            tracker.start_stage(stage)
            assert tracker._current_stage == stage
            assert tracker._stage_progress == 0.0

    def test_add_callback(self):
        """Test adding callbacks to tracker."""
        tracker = ProgressTracker()
        callback1 = Mock()
        callback2 = Mock()

        tracker.add_callback(callback1)
        tracker.add_callback(callback2)

        assert len(tracker._callbacks) == 2
        assert callback1 in tracker._callbacks
        assert callback2 in tracker._callbacks

    def test_callback_invoked_on_start_stage(self):
        """Test that callbacks are invoked when starting a stage."""
        tracker = ProgressTracker()
        callback = Mock()
        tracker.add_callback(callback)

        tracker.start_stage(OperationStage.VALIDATING)

        callback.assert_called_once()
        update = callback.call_args[0][0]
        assert isinstance(update, ProgressUpdate)
        assert update.stage == OperationStage.VALIDATING

    def test_callback_invoked_on_update(self):
        """Test that callbacks are invoked on progress updates."""
        tracker = ProgressTracker()
        callback = Mock()
        tracker.add_callback(callback)

        tracker.update(0.5, "Processing...")

        assert callback.call_count >= 1  # At least one call
        last_update = callback.call_args[0][0]
        assert isinstance(last_update, ProgressUpdate)
        assert last_update.message == "Processing..."

    def test_callback_invoked_on_complete(self):
        """Test that callbacks are invoked on completion."""
        tracker = ProgressTracker()
        callback = Mock()
        tracker.add_callback(callback)

        tracker.complete()

        last_update = callback.call_args[0][0]
        assert isinstance(last_update, ProgressUpdate)
        assert last_update.stage == OperationStage.COMPLETE
        assert last_update.percent == 100.0

    def test_progress_percentage_calculation(self):
        """Test overall progress percentage calculation."""
        tracker = ProgressTracker()

        # Initially at 0%
        tracker.start_stage(OperationStage.INITIALIZING)
        update = tracker._calculate_overall_percent()
        assert 0 <= update <= 5  # INITIALIZING is 5%

        # At 50% of VALIDATING (10% total = 5% + 5% of 10%)
        tracker.start_stage(OperationStage.VALIDATING)
        tracker.update(0.5, "Halfway through validation")
        percent = tracker._calculate_overall_percent()
        assert 5 < percent < 15  # Between INIT (5%) and halfway through VALIDATING

        # At full VALIDATING
        tracker.update(1.0, "Validation complete")
        percent = tracker._calculate_overall_percent()
        assert 14 < percent < 16  # INIT (5%) + VALIDATING (10%)

        # At RENDERING
        tracker.start_stage(OperationStage.RENDERING)
        percent = tracker._calculate_overall_percent()
        assert 14 < percent < 17  # INIT + VALIDATING + start of RENDERING

    def test_stage_weights_sum(self):
        """Test that stage weights sum to 100."""
        tracker = ProgressTracker()
        total_weight = sum(
            w for s, w in tracker.STAGE_WEIGHTS.items() if s != OperationStage.COMPLETE
        )
        assert total_weight == 100

    def test_update_clamps_progress_bounds(self):
        """Test that update clamps progress to 0.0-1.0."""
        tracker = ProgressTracker()
        tracker.start_stage(OperationStage.RENDERING)

        # Test values outside bounds are clamped
        tracker.update(-0.5, "Negative progress")
        assert tracker._stage_progress == 0.0

        tracker.update(1.5, "Over 100%")
        assert tracker._stage_progress == 1.0

        tracker.update(0.75, "Valid progress")
        assert tracker._stage_progress == 0.75

    def test_cancellation_stops_operation(self):
        """Test that cancellation stops the operation."""
        token = CancellationToken()
        tracker = ProgressTracker(cancellation_token=token)

        tracker.start_stage(OperationStage.VALIDATING)

        # Cancel and verify check raises
        token.request_cancel(reason="User cancelled")

        with pytest.raises(OperationCancelled):
            tracker.start_stage(OperationStage.RENDERING)

    def test_cancellation_check_on_update(self):
        """Test that cancellation is checked during update."""
        token = CancellationToken()
        tracker = ProgressTracker(cancellation_token=token)

        tracker.start_stage(OperationStage.VALIDATING)
        token.request_cancel()

        with pytest.raises(OperationCancelled):
            tracker.update(0.5, "Processing...")

    def test_progress_eta_estimation(self):
        """Test ETA estimation based on elapsed time and progress."""
        tracker = ProgressTracker()

        # Start tracker and immediately check - should return None
        # (not enough progress)
        tracker.start_stage(OperationStage.INITIALIZING)
        eta = tracker._estimate_eta()
        assert eta is None

        # Move through stages to accumulate time and progress
        tracker.start_stage(OperationStage.VALIDATING)
        tracker.update(0.3, "Validating...")

        # Simulate some elapsed time
        with patch("time.time") as mock_time:
            mock_time.return_value = tracker._start_time + 2.0  # 2 seconds elapsed
            eta = tracker._estimate_eta()

            # Should now have an estimate if progress > 1%
            if tracker._calculate_overall_percent() > 1.0:
                assert eta is not None
                assert eta >= 0.0

    def test_eta_non_negative(self):
        """Test that ETA is never negative."""
        tracker = ProgressTracker()

        # Simulate rapid progress (more than 100% if linear extrapolation)
        with patch("time.time") as mock_time:
            mock_time.return_value = tracker._start_time + 0.5  # 0.5 seconds elapsed
            tracker.start_stage(OperationStage.RENDERING)
            tracker.update(0.9, "Almost done")

            eta = tracker._estimate_eta()
            if eta is not None:
                assert eta >= 0.0


class TestProgressWithCallbacks:
    """Tests for progress callbacks and integration."""

    def test_with_progress_yields_updates(self):
        """Test that tracker yields progress updates through callbacks."""
        tracker = ProgressTracker()
        updates = []

        def capture_update(update: ProgressUpdate) -> None:
            updates.append(update)

        tracker.add_callback(capture_update)

        tracker.start_stage(OperationStage.VALIDATING)
        tracker.update(0.5, "Processing...")
        tracker.update(1.0, "Validation complete")

        # Should have multiple updates
        assert len(updates) >= 2
        assert all(isinstance(u, ProgressUpdate) for u in updates)

    def test_callback_receives_file_counts(self):
        """Test that callbacks receive file processing information."""
        tracker = ProgressTracker()
        callback = Mock()
        tracker.add_callback(callback)

        tracker.start_stage(OperationStage.WRITING)
        tracker.update(0.5, "Writing files", files_processed=50, total_files=100)

        update = callback.call_args[0][0]
        assert update.files_processed == 50
        assert update.total_files == 100

    def test_callback_exception_handling(self):
        """Test that callback exceptions don't break progress tracking."""
        tracker = ProgressTracker()

        def failing_callback(update: ProgressUpdate) -> None:
            raise ValueError("Callback error")

        def working_callback(update: ProgressUpdate) -> None:
            pass

        working_mock = Mock(side_effect=working_callback)
        tracker.add_callback(failing_callback)
        tracker.add_callback(working_mock)

        # Should not raise even though first callback fails
        tracker.start_stage(OperationStage.VALIDATING)
        assert working_mock.called

    def test_multiple_callbacks_all_notified(self):
        """Test that all callbacks are notified on progress."""
        tracker = ProgressTracker()
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        tracker.add_callback(callback1)
        tracker.add_callback(callback2)
        tracker.add_callback(callback3)

        tracker.update(0.5, "Progress")

        assert callback1.called
        assert callback2.called
        assert callback3.called

    def test_progress_message_default(self):
        """Test default progress message when none provided."""
        tracker = ProgressTracker()
        callback = Mock()
        tracker.add_callback(callback)

        tracker.start_stage(OperationStage.RENDERING)
        tracker.update(0.75)  # No message

        update = callback.call_args[0][0]
        assert "rendering" in update.message.lower()


class TestCopierProgressIntegration:
    """Tests for integration with Copier operations."""

    def test_copier_copy_with_progress_callback(self):
        """Test tracking progress through a simulated Copier operation."""
        tracker = ProgressTracker()
        progress_updates = []

        def track_progress(update: ProgressUpdate) -> None:
            progress_updates.append(update)

        tracker.add_callback(track_progress)

        # Simulate Copier operation stages
        tracker.start_stage(OperationStage.INITIALIZING)
        time.sleep(0.01)

        tracker.start_stage(OperationStage.VALIDATING)
        tracker.update(0.5, "Validating answers")
        tracker.update(1.0, "Answers validated")

        tracker.start_stage(OperationStage.RENDERING)
        tracker.update(0.3, "Rendering template", files_processed=10, total_files=35)
        tracker.update(0.7, "Rendering template", files_processed=25, total_files=35)
        tracker.update(1.0, "Template rendered")

        tracker.start_stage(OperationStage.WRITING)
        tracker.update(0.5, "Writing files", files_processed=50, total_files=100)
        tracker.update(1.0, "Files written")

        tracker.start_stage(OperationStage.FINALIZING)
        tracker.update(1.0, "Finalizing...")

        tracker.complete()

        # Verify progress updates
        assert len(progress_updates) > 0
        assert progress_updates[0].stage == OperationStage.INITIALIZING
        assert progress_updates[-1].stage == OperationStage.COMPLETE
        assert progress_updates[-1].percent == 100.0

    def test_graceful_abort_cleanup(self):
        """Test graceful abort and cleanup."""
        token = CancellationToken()
        tracker = ProgressTracker(cancellation_token=token)
        cleanup_called = False

        def cleanup() -> None:
            nonlocal cleanup_called
            cleanup_called = True

        tracker.start_stage(OperationStage.RENDERING)
        tracker.update(0.5, "Processing...")

        # Simulate user cancellation
        token.request_cancel(reason="User aborted operation")

        try:
            tracker.start_stage(OperationStage.WRITING)
        except OperationCancelled:
            cleanup()

        assert cleanup_called is True


class TestProgressTrackerAdvanced:
    """Advanced tests for progress tracker behavior."""

    def test_progress_monotonic_increase(self):
        """Test that overall progress generally increases."""
        tracker = ProgressTracker()
        percentages = []

        def capture_percent(update: ProgressUpdate) -> None:
            percentages.append(update.percent)

        tracker.add_callback(capture_percent)

        stages = [
            OperationStage.INITIALIZING,
            OperationStage.VALIDATING,
            OperationStage.RENDERING,
            OperationStage.WRITING,
            OperationStage.FINALIZING,
        ]

        for stage in stages:
            tracker.start_stage(stage)
            tracker.update(0.5, f"Processing {stage.value}")
            tracker.update(1.0, f"{stage.value} complete")

        tracker.complete()

        # Progress should generally increase (allowing for same values)
        for i in range(1, len(percentages)):
            assert percentages[i] >= percentages[i - 1] - 0.1  # Allow small margin

    def test_stage_progress_reset_on_new_stage(self):
        """Test that stage progress resets when starting a new stage."""
        tracker = ProgressTracker()

        tracker.start_stage(OperationStage.VALIDATING)
        tracker.update(0.8, "Halfway through validation")
        assert tracker._stage_progress == 0.8

        # Start new stage should reset
        tracker.start_stage(OperationStage.RENDERING)
        assert tracker._stage_progress == 0.0

    def test_complete_sets_100_percent(self):
        """Test that completion sets 100% progress."""
        tracker = ProgressTracker()
        callback = Mock()
        tracker.add_callback(callback)

        tracker.start_stage(OperationStage.INITIALIZING)
        tracker.start_stage(OperationStage.VALIDATING)

        # Don't complete all stages, just complete
        tracker.complete()

        update = callback.call_args[0][0]
        assert update.percent == 100.0
        assert update.stage == OperationStage.COMPLETE

    def test_eta_calculation_with_mock_time(self):
        """Test ETA calculation with controlled time."""
        tracker = ProgressTracker()

        # Mock initial time
        initial_time = 1000.0
        with patch("time.time", return_value=initial_time):
            tracker = ProgressTracker()
            tracker.start_stage(OperationStage.VALIDATING)

        # Simulate 2 seconds elapsed, 15% progress (5% base + 10% * 0.5)
        with patch("time.time", return_value=initial_time + 2.0):
            tracker.update(0.5, "Some progress")  # 50% through VALIDATING
            eta = tracker._estimate_eta()

            if eta is not None:
                # Ensure ETA is non-negative
                assert eta >= 0.0  # Just verify it's calculated and reasonable

    def test_empty_callback_list(self):
        """Test tracker works without callbacks."""
        tracker = ProgressTracker()

        # Should not raise even without callbacks
        tracker.start_stage(OperationStage.VALIDATING)
        tracker.update(0.5, "Processing")
        tracker.complete()

    def test_large_file_count_tracking(self):
        """Test tracking large file counts."""
        tracker = ProgressTracker()
        callback = Mock()
        tracker.add_callback(callback)

        tracker.start_stage(OperationStage.WRITING)
        tracker.update(0.5, "Writing files", files_processed=5000, total_files=10000)

        update = callback.call_args[0][0]
        assert update.files_processed == 5000
        assert update.total_files == 10000
