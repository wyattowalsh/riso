"""Progress tracking and cancellation for long-running operations."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class OperationStage(Enum):
    """Stages of a Copier operation."""

    INITIALIZING = "initializing"
    VALIDATING = "validating"
    RENDERING = "rendering"
    WRITING = "writing"
    FINALIZING = "finalizing"
    COMPLETE = "complete"


@dataclass
class ProgressUpdate:
    """Progress update for streaming to clients."""

    stage: OperationStage
    percent: float  # 0.0 to 100.0
    message: str
    eta_seconds: float | None = None
    files_processed: int = 0
    total_files: int | None = None


class CancellationToken:
    """Token for cancelling long-running operations."""

    def __init__(self) -> None:
        self._cancelled = False
        self._cancel_reason: str | None = None

    @property
    def is_cancelled(self) -> bool:
        """Check if operation has been cancelled."""
        return self._cancelled

    def request_cancel(self, reason: str = "User requested cancellation") -> None:
        """Request cancellation of the operation.

        Parameters
        ----------
        reason
            Human-readable reason for cancellation
        """
        self._cancelled = True
        self._cancel_reason = reason

    def check(self) -> None:
        """Raise if cancelled.

        Raises
        ------
        OperationCancelled
            If operation has been cancelled
        """
        # Import at runtime to avoid circular dependency
        from .errors import OperationCancelled

        if self._cancelled:
            raise OperationCancelled(self._cancel_reason or "Operation cancelled")


class ProgressTracker:
    """Track progress of multi-stage operations.

    Provides milestone-based progress estimation for operations without
    native progress callbacks (like Copier). Supports cancellation checks
    and callbacks for streaming progress updates to MCP clients.

    Examples
    --------
    >>> tracker = ProgressTracker()
    >>> tracker.add_callback(lambda update: print(update.percent))
    >>> tracker.start_stage(OperationStage.VALIDATING)
    >>> tracker.update(0.5, "Validating answers...")
    >>> tracker.complete()
    """

    # Estimated weight of each stage as percentage of total work
    STAGE_WEIGHTS = {
        OperationStage.INITIALIZING: 5,
        OperationStage.VALIDATING: 10,
        OperationStage.RENDERING: 50,
        OperationStage.WRITING: 30,
        OperationStage.FINALIZING: 5,
    }

    def __init__(self, cancellation_token: CancellationToken | None = None):
        """Initialize progress tracker.

        Parameters
        ----------
        cancellation_token
            Optional token for checking cancellation status
        """
        self._current_stage = OperationStage.INITIALIZING
        self._stage_progress = 0.0
        self._start_time = time.time()
        self._callbacks: list[Callable[[ProgressUpdate], None]] = []
        self._token = cancellation_token

    def add_callback(self, callback: Callable[[ProgressUpdate], None]) -> None:
        """Add a callback to receive progress updates.

        Parameters
        ----------
        callback
            Function that receives ProgressUpdate objects
        """
        self._callbacks.append(callback)

    def start_stage(self, stage: OperationStage) -> None:
        """Start a new stage of the operation.

        Parameters
        ----------
        stage
            The stage being started
        """
        if self._token:
            self._token.check()

        self._current_stage = stage
        self._stage_progress = 0.0

        # Notify start of stage
        update = ProgressUpdate(
            stage=stage,
            percent=self._calculate_overall_percent(),
            message=f"Starting {stage.value}...",
            eta_seconds=self._estimate_eta(),
        )
        self._notify(update)

    def update(
        self,
        progress: float,
        message: str = "",
        files_processed: int = 0,
        total_files: int | None = None,
    ) -> None:
        """Update progress within current stage.

        Parameters
        ----------
        progress
            Progress within current stage (0.0 to 1.0)
        message
            Status message describing current activity
        files_processed
            Number of files processed so far
        total_files
            Total number of files to process
        """
        if self._token:
            self._token.check()

        self._stage_progress = max(0.0, min(1.0, progress))

        update = ProgressUpdate(
            stage=self._current_stage,
            percent=self._calculate_overall_percent(),
            message=message or f"Processing {self._current_stage.value}...",
            eta_seconds=self._estimate_eta(),
            files_processed=files_processed,
            total_files=total_files,
        )
        self._notify(update)

    def complete(self) -> None:
        """Mark operation as complete."""
        self._current_stage = OperationStage.COMPLETE
        self._stage_progress = 1.0

        update = ProgressUpdate(
            stage=OperationStage.COMPLETE,
            percent=100.0,
            message="Operation completed successfully",
            eta_seconds=0.0,
        )
        self._notify(update)

    def _calculate_overall_percent(self) -> float:
        """Calculate overall progress percentage.

        Returns
        -------
        float
            Overall progress from 0.0 to 100.0
        """
        # Find completed stages before current
        completed_weight = 0.0
        for stage in OperationStage:
            if stage == OperationStage.COMPLETE:
                continue
            if stage == self._current_stage:
                break
            completed_weight += self.STAGE_WEIGHTS.get(stage, 0)

        # Add progress within current stage
        current_weight = self.STAGE_WEIGHTS.get(self._current_stage, 0)
        current_progress = current_weight * self._stage_progress

        # Calculate as percentage of total weight
        total_weight = sum(
            w for s, w in self.STAGE_WEIGHTS.items() if s != OperationStage.COMPLETE
        )
        return ((completed_weight + current_progress) / total_weight) * 100.0

    def _estimate_eta(self) -> float | None:
        """Estimate remaining time based on elapsed time and progress.

        Returns
        -------
        float | None
            Estimated seconds remaining, or None if cannot estimate
        """
        elapsed = time.time() - self._start_time
        current_percent = self._calculate_overall_percent()

        if current_percent < 1.0 or elapsed < 1.0:
            return None  # Not enough progress to estimate

        # Linear extrapolation based on progress
        total_estimated = elapsed / (current_percent / 100.0)
        remaining = total_estimated - elapsed
        return max(0.0, remaining)

    def _notify(self, update: ProgressUpdate) -> None:
        """Notify all callbacks of progress update.

        Parameters
        ----------
        update
            Progress update to send to callbacks
        """
        for callback in self._callbacks:
            try:
                callback(update)
            except Exception:
                # Ignore callback errors to not break progress tracking
                pass
