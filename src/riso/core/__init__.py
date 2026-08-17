"""Shared core utilities for Riso CLI and template operations."""

from riso.core.answers import (
    REMOVED_ANSWER_KEYS,
    apply_then_reject_removed_keys,
    reject_removed_answer_keys,
)
from riso.core.errors import (
    CopierOperationError,
    OperationCancelled,
    OperationTimeoutError,
    PathNotFoundError,
    PermissionDeniedError,
    RisoError,
    TemplateNotFoundError,
    ValidationFailedError,
)
from riso.core.removed_answer_keys import (
    ANSWER_KEY_REMAPS,
    RemapOp,
    RemapResult,
    apply_removed_key_remaps,
)

__all__ = [
    "ANSWER_KEY_REMAPS",
    "REMOVED_ANSWER_KEYS",
    "CopierOperationError",
    "OperationCancelled",
    "OperationTimeoutError",
    "PathNotFoundError",
    "PermissionDeniedError",
    "RemapOp",
    "RemapResult",
    "RisoError",
    "TemplateNotFoundError",
    "ValidationFailedError",
    "apply_removed_key_remaps",
    "apply_then_reject_removed_keys",
    "reject_removed_answer_keys",
]
