"""Wizard session management for multi-step project generation.

Maintains state across tool calls for the interactive wizard workflow.
"""

from __future__ import annotations

import logging
import secrets
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from .config import RateLimitConfig
from .errors import SessionExpiredError, SessionNotFoundError, TooManyRequestsError
from .logging import log_event

if TYPE_CHECKING:
    from .persistence import SessionStore


@dataclass
class WizardStep:
    """A single step in the wizard workflow."""

    name: str
    title: str
    prompts: list[str]
    required: bool = True
    completed: bool = False
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WizardSession:
    """Session state for multi-step wizard workflow.

    Tracks collected answers, current step, and validation state.
    """

    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    # Wizard state
    current_step: int = 0
    steps: list[WizardStep] = field(default_factory=list)
    answers: dict[str, Any] = field(default_factory=dict)

    # Metadata
    project_name: str = ""
    destination: str = ""
    template_variant: str = "default"

    # Validation
    validation_errors: list[str] = field(default_factory=list)
    is_complete: bool = False

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()

    def is_expired(self, ttl_minutes: int) -> bool:
        """Check if session has expired."""
        return datetime.now() > self.last_activity + timedelta(minutes=ttl_minutes)

    def advance_step(self) -> int:
        """Move to next wizard step."""
        self.current_step += 1
        self.touch()
        return self.current_step

    def go_back(self) -> int:
        """Move to previous wizard step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.is_complete = False
        self.touch()
        return self.current_step

    def set_answer(self, key: str, value: Any) -> None:
        """Set an answer value."""
        self.answers[key] = value
        self.touch()

    def set_answers(self, answers: dict[str, Any]) -> None:
        """Set multiple answer values."""
        self.answers.update(answers)
        self.touch()


# Default wizard steps configuration
DEFAULT_WIZARD_STEPS = [
    WizardStep(
        name="project_basics",
        title="Project Basics",
        prompts=["project_name", "project_layout", "project_language"],
        required=True,
    ),
    WizardStep(
        name="quality",
        title="Quality & Testing",
        prompts=["quality_profile", "python_versions"],
        required=True,
    ),
    WizardStep(
        name="modules",
        title="Modules & Features",
        prompts=[
            "cli_module",
            "api_module",
            "api_languages",
            "mcp_module",
            "mcp_languages",
            "websocket_module",
        ],
        required=False,
    ),
    WizardStep(
        name="documentation",
        title="Documentation",
        prompts=["docs_module", "docs_framework", "shared_logic"],
        required=False,
    ),
    WizardStep(
        name="ci_cd",
        title="CI/CD Configuration",
        prompts=["ci_platform", "changelog_module"],
        required=False,
    ),
    WizardStep(
        name="destination",
        title="Output Location",
        prompts=["destination"],
        required=True,
    ),
]


class SessionManager:
    """Thread-safe session manager for wizard workflows.

    Handles session creation, retrieval, cleanup, and expiration.
    """

    def __init__(
        self,
        ttl_minutes: int = 60,
        max_sessions: int = 100,
        rate_config: RateLimitConfig | None = None,
        auto_cleanup_interval: int | None = None,
        store: SessionStore | None = None,
    ) -> None:
        self._sessions: dict[str, WizardSession] = {}
        self._lock = threading.RLock()
        self._ttl_minutes = ttl_minutes
        self._max_sessions = max_sessions
        self._creation_times: deque[float] = deque(maxlen=100)
        self._rate_config = rate_config or RateLimitConfig()
        self._logger = logging.getLogger("riso.mcp.session")
        self._cleanup_interval = auto_cleanup_interval
        self._cleanup_timer: threading.Timer | None = None
        self._cleanup_enabled = (
            auto_cleanup_interval is not None and auto_cleanup_interval > 0
        )
        self._store = store

        if self._cleanup_enabled:
            self._start_cleanup_timer()

    def _check_rate_limit(self) -> None:
        """Check if rate limit has been exceeded.

        Raises
        ------
        TooManyRequestsError
            If rate limit is exceeded
        """
        now = time.time()

        # Count recent sessions
        recent_minute = sum(1 for t in self._creation_times if now - t < 60)
        recent_hour = sum(1 for t in self._creation_times if now - t < 3600)

        # Check minute limit
        if recent_minute >= self._rate_config.max_sessions_per_minute:
            raise TooManyRequestsError(
                "Rate limit exceeded: too many sessions per minute",
                retry_after=60,
            )

        # Check hour limit
        if recent_hour >= self._rate_config.max_sessions_per_hour:
            raise TooManyRequestsError(
                "Rate limit exceeded: too many sessions per hour",
                retry_after=3600,
            )

    def create_session(
        self,
        project_name: str = "",
        destination: str = "",
        template_variant: str = "default",
    ) -> WizardSession:
        """Create a new wizard session.

        Returns
        -------
        WizardSession
            New session with unique ID

        Raises
        ------
        TooManyRequestsError
            If rate limit is exceeded
        """
        with self._lock:
            # Check rate limit first
            self._check_rate_limit()

            # Cleanup if at capacity
            if len(self._sessions) >= self._max_sessions:
                self.cleanup_expired()
                if len(self._sessions) >= self._max_sessions:
                    self._evict_oldest()

            session_id = secrets.token_urlsafe(16)
            session = WizardSession(
                session_id=session_id,
                project_name=project_name,
                destination=destination,
                template_variant=template_variant,
                steps=[
                    WizardStep(
                        name=s.name,
                        title=s.title,
                        prompts=s.prompts.copy(),
                        required=s.required,
                    )
                    for s in DEFAULT_WIZARD_STEPS
                ],
            )
            self._sessions[session_id] = session

            # Persist to storage backend if available
            if self._store is not None:
                try:
                    self._store.save(session_id, session)
                except Exception as e:
                    log_event(
                        self._logger,
                        "session_persist_failed",
                        level="error",
                        session_id=session_id,
                        error=str(e),
                    )

            # Record creation time after successful creation
            self._creation_times.append(time.time())

            # Log session creation
            log_event(
                self._logger,
                "session_created",
                level="info",
                session_id=session_id,
                project_name=project_name,
                template_variant=template_variant,
                total_sessions=len(self._sessions),
            )

            return session

    def get_session(self, session_id: str) -> WizardSession:
        """Retrieve an existing session.

        Returns
        -------
        WizardSession
            Session if found and not expired

        Raises
        ------
        SessionNotFoundError
            If session doesn't exist
        SessionExpiredError
            If session has expired
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise SessionNotFoundError(session_id)

            if session.is_expired(self._ttl_minutes):
                del self._sessions[session_id]
                # Remove from persistence
                if self._store is not None:
                    try:
                        self._store.delete(session_id)
                    except Exception as e:
                        log_event(
                            self._logger,
                            "session_delete_failed",
                            level="error",
                            session_id=session_id,
                            error=str(e),
                        )
                log_event(
                    self._logger,
                    "session_expired",
                    level="warning",
                    session_id=session_id,
                    age_minutes=(datetime.now() - session.last_activity).total_seconds()
                    / 60,
                )
                raise SessionExpiredError(session_id)

            session.touch()

            # Persist updated timestamp
            if self._store is not None:
                try:
                    self._store.save(session_id, session)
                except Exception as e:
                    log_event(
                        self._logger,
                        "session_persist_failed",
                        level="error",
                        session_id=session_id,
                        error=str(e),
                    )

            return session

    def get_session_or_none(self, session_id: str) -> WizardSession | None:
        """Retrieve session or return None if not found/expired."""
        try:
            return self.get_session(session_id)
        except (SessionNotFoundError, SessionExpiredError):
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

                # Remove from persistence
                if self._store is not None:
                    try:
                        self._store.delete(session_id)
                    except Exception as e:
                        log_event(
                            self._logger,
                            "session_delete_failed",
                            level="error",
                            session_id=session_id,
                            error=str(e),
                        )

                return True
            return False

    def cleanup_expired(self) -> int:
        """Remove all expired sessions.

        Returns
        -------
        int
            Number of sessions cleaned up
        """
        with self._lock:
            expired = [
                sid
                for sid, session in self._sessions.items()
                if session.is_expired(self._ttl_minutes)
            ]
            for sid in expired:
                del self._sessions[sid]

                # Remove from persistence
                if self._store is not None:
                    try:
                        self._store.delete(sid)
                    except Exception as e:
                        log_event(
                            self._logger,
                            "session_delete_failed",
                            level="error",
                            session_id=sid,
                            error=str(e),
                        )

            if expired:
                log_event(
                    self._logger,
                    "sessions_cleaned",
                    level="info",
                    expired_count=len(expired),
                    remaining_sessions=len(self._sessions),
                )

            return len(expired)

    def _evict_oldest(self) -> None:
        """Evict the oldest session to make room."""
        if not self._sessions:
            return

        oldest_id = min(
            self._sessions.keys(), key=lambda k: self._sessions[k].last_activity
        )
        del self._sessions[oldest_id]

    def _start_cleanup_timer(self) -> None:
        """Start the periodic cleanup timer."""
        if not self._cleanup_enabled or self._cleanup_interval is None:
            return
        self._cleanup_timer = threading.Timer(
            self._cleanup_interval, self._run_cleanup_task
        )
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
        log_event(
            self._logger,
            "cleanup_timer_started",
            level="debug",
            interval_seconds=self._cleanup_interval,
        )

    def _run_cleanup_task(self) -> None:
        """Execute cleanup and reschedule timer."""
        try:
            expired_count = self.cleanup_expired()
            log_event(
                self._logger,
                "auto_cleanup_executed",
                level="debug",
                expired_count=expired_count,
                active_sessions=self.active_session_count,
            )
        except Exception as e:
            log_event(
                self._logger,
                "cleanup_task_error",
                level="error",
                error=str(e),
                error_type=type(e).__name__,
            )
        finally:
            if self._cleanup_enabled:
                self._start_cleanup_timer()

    def _stop_cleanup_timer(self) -> None:
        """Stop the periodic cleanup timer."""
        if self._cleanup_timer is not None:
            self._cleanup_timer.cancel()
            self._cleanup_timer = None
            log_event(self._logger, "cleanup_timer_stopped", level="debug")

    @property
    def active_session_count(self) -> int:
        """Get count of active sessions."""
        with self._lock:
            return len(self._sessions)

    def list_sessions(self) -> list[dict[str, Any]]:
        """List all active sessions with basic info."""
        with self._lock:
            return [
                {
                    "session_id": s.session_id,
                    "project_name": s.project_name,
                    "current_step": s.current_step,
                    "is_complete": s.is_complete,
                    "created_at": s.created_at.isoformat(),
                    "last_activity": s.last_activity.isoformat(),
                }
                for s in self._sessions.values()
                if not s.is_expired(self._ttl_minutes)
            ]

    def enable_auto_cleanup(self, interval: int | None = None) -> None:
        """Enable automatic session cleanup.

        Parameters
        ----------
        interval
            Cleanup interval in seconds (60-3600). If None, uses existing interval.

        Raises
        ------
        ValueError
            If interval is out of range or no interval is configured
        """
        with self._lock:
            if interval is not None:
                if interval < 60 or interval > 3600:
                    raise ValueError(
                        "Cleanup interval must be between 60 and 3600 seconds"
                    )
                self._cleanup_interval = interval
            if self._cleanup_interval is None:
                raise ValueError("No cleanup interval configured")
            if not self._cleanup_enabled:
                self._cleanup_enabled = True
                self._start_cleanup_timer()
                log_event(
                    self._logger,
                    "auto_cleanup_enabled",
                    level="info",
                    interval_seconds=self._cleanup_interval,
                )

    def disable_auto_cleanup(self) -> None:
        """Disable automatic session cleanup."""
        with self._lock:
            if self._cleanup_enabled:
                self._cleanup_enabled = False
                self._stop_cleanup_timer()
                log_event(self._logger, "auto_cleanup_disabled", level="info")

    @property
    def is_auto_cleanup_enabled(self) -> bool:
        """Check if auto-cleanup is currently enabled."""
        return self._cleanup_enabled

    @property
    def cleanup_interval_seconds(self) -> int | None:
        """Get the configured cleanup interval in seconds."""
        return self._cleanup_interval

    def shutdown(self) -> None:
        """Shutdown the session manager and cleanup resources."""
        with self._lock:
            self._stop_cleanup_timer()
            log_event(
                self._logger,
                "session_manager_shutdown",
                level="info",
                final_session_count=len(self._sessions),
            )

    def load_persisted_sessions(self) -> int:
        """Load sessions from persistent storage on startup.

        Returns
        -------
        int
            Number of sessions loaded

        Notes
        -----
        This should be called during server initialization to restore
        sessions from a previous run. Expired sessions are not loaded.
        """
        if self._store is None:
            return 0

        with self._lock:
            try:
                persisted_sessions = self._store.load_all_sessions()

                # Filter out expired sessions
                loaded = 0
                for session_id, session in persisted_sessions.items():
                    if not session.is_expired(self._ttl_minutes):
                        self._sessions[session_id] = session
                        loaded += 1
                    else:
                        # Clean up expired persisted sessions
                        try:
                            self._store.delete(session_id)
                        except Exception as e:
                            log_event(
                                self._logger,
                                "session_delete_failed",
                                level="error",
                                session_id=session_id,
                                error=str(e),
                            )

                if loaded > 0:
                    log_event(
                        self._logger,
                        "sessions_loaded",
                        level="info",
                        loaded_count=loaded,
                        expired_count=len(persisted_sessions) - loaded,
                    )

                return loaded

            except Exception as e:
                log_event(
                    self._logger,
                    "session_load_failed",
                    level="error",
                    error=str(e),
                )
                return 0

    def export_session(self, session_id: str) -> dict:
        """Export a session as a dictionary.

        Parameters
        ----------
        session_id
            Session identifier to export

        Returns
        -------
        dict
            Session data as a dictionary

        Raises
        ------
        SessionNotFoundError
            If session doesn't exist
        """
        session = self.get_session(session_id)
        return asdict(session)

    def import_session(self, data: dict) -> str:
        """Import a session from a dictionary.

        Parameters
        ----------
        data
            Session data dictionary (from export_session)

        Returns
        -------
        str
            New session ID

        Raises
        ------
        ValueError
            If session data is invalid
        """
        with self._lock:
            try:
                # Reconstruct WizardStep objects
                steps = []
                for step_data in data.get("steps", []):
                    steps.append(WizardStep(**step_data))

                # Create session object
                session_data = data.copy()
                session_data["steps"] = steps

                session = WizardSession(**session_data)

                # Store in memory
                self._sessions[session.session_id] = session

                # Persist to storage backend if available
                if self._store is not None:
                    try:
                        self._store.save(session.session_id, session)
                    except Exception as e:
                        log_event(
                            self._logger,
                            "session_persist_failed",
                            level="error",
                            session_id=session.session_id,
                            error=str(e),
                        )

                log_event(
                    self._logger,
                    "session_imported",
                    level="info",
                    session_id=session.session_id,
                )

                return session.session_id

            except (KeyError, TypeError, ValueError) as e:
                raise ValueError(f"Invalid session data: {e}") from e
