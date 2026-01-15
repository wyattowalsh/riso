"""Wizard session management for multi-step project generation.

Maintains state across tool calls for the interactive wizard workflow.
"""

from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .errors import SessionExpiredError, SessionNotFoundError


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
        prompts=["cli_module", "api_tracks", "mcp_module", "websocket_module"],
        required=False,
    ),
    WizardStep(
        name="documentation",
        title="Documentation",
        prompts=["docs_site", "shared_logic"],
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
    ) -> None:
        self._sessions: dict[str, WizardSession] = {}
        self._lock = threading.RLock()
        self._ttl_minutes = ttl_minutes
        self._max_sessions = max_sessions

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
        """
        with self._lock:
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
                raise SessionExpiredError(session_id)

            session.touch()
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

            return len(expired)

    def _evict_oldest(self) -> None:
        """Evict the oldest session to make room."""
        if not self._sessions:
            return

        oldest_id = min(
            self._sessions.keys(), key=lambda k: self._sessions[k].last_activity
        )
        del self._sessions[oldest_id]

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
