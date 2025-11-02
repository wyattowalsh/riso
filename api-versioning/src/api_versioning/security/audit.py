"""
Security audit logging (FR-027).

This module provides structured logging for security events including
authentication failures, authorization denials, and suspicious patterns.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional


logger = logging.getLogger("api_versioning.security.audit")


class AuditEventType(str, Enum):
    """Type of security audit event."""
    
    AUTH_SUCCESS           = "AUTH_SUCCESS"
    AUTH_FAILURE           = "AUTH_FAILURE"
    AUTHZ_DENIED           = "AUTHZ_DENIED"
    RATE_LIMIT_EXCEEDED    = "RATE_LIMIT_EXCEEDED"
    INVALID_INPUT          = "INVALID_INPUT"
    SUSPICIOUS_PATTERN     = "SUSPICIOUS_PATTERN"
    CONFIG_CHANGED         = "CONFIG_CHANGED"
    VERSION_ACCESS_DENIED  = "VERSION_ACCESS_DENIED"


@dataclass
class AuditEvent:
    """
    Security audit event.
    
    Attributes:
        event_type: Type of security event
        timestamp: When event occurred
        consumer_id: Consumer identifier (masked if sensitive)
        ip_address: Client IP address (masked for privacy)
        user_agent: Client user agent
        version_id: API version accessed (if applicable)
        endpoint_path: Endpoint path (if applicable)
        details: Additional event-specific details
        severity: Event severity (INFO, WARNING, ERROR)
    """
    
    event_type:   AuditEventType
    timestamp:    datetime
    consumer_id:  str
    ip_address:   str
    user_agent:   Optional[str] = None
    version_id:   Optional[str] = None
    endpoint_path: Optional[str] = None
    details:      dict[str, Any] = None
    severity:     str = "INFO"
    
    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.details is None:
            self.details = {}
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type":   self.event_type.value,
            "timestamp":    self.timestamp.isoformat(),
            "consumer_id":  self.consumer_id,
            "ip_address":   self.ip_address,
            "user_agent":   self.user_agent,
            "version_id":   self.version_id,
            "endpoint_path": self.endpoint_path,
            "details":      self.details,
            "severity":     self.severity,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


def log_audit_event(event: AuditEvent) -> None:
    """
    Log security audit event.
    
    Args:
        event: Audit event to log
    """
    # Select log level based on severity
    if event.severity == "ERROR":
        logger.error(
            f"security_audit.{event.event_type.value}",
            extra={"audit_event": event.to_dict()}
        )
    elif event.severity == "WARNING":
        logger.warning(
            f"security_audit.{event.event_type.value}",
            extra={"audit_event": event.to_dict()}
        )
    else:
        logger.info(
            f"security_audit.{event.event_type.value}",
            extra={"audit_event": event.to_dict()}
        )


def log_auth_failure(
    consumer_id: str,
    ip_address: str,
    reason: str,
    user_agent: Optional[str] = None
) -> None:
    """
    Log authentication failure.
    
    Args:
        consumer_id: Consumer identifier
        ip_address: Client IP address
        reason: Failure reason
        user_agent: Client user agent
    """
    event = AuditEvent(
        event_type=AuditEventType.AUTH_FAILURE,
        timestamp=datetime.now(),
        consumer_id=consumer_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"reason": reason},
        severity="WARNING"
    )
    log_audit_event(event)


def log_rate_limit_exceeded(
    consumer_id: str,
    ip_address: str,
    version_id: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """
    Log rate limit exceeded event.
    
    Args:
        consumer_id: Consumer identifier
        ip_address: Client IP address
        version_id: Version being accessed
        user_agent: Client user agent
    """
    event = AuditEvent(
        event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
        timestamp=datetime.now(),
        consumer_id=consumer_id,
        ip_address=ip_address,
        user_agent=user_agent,
        version_id=version_id,
        severity="WARNING"
    )
    log_audit_event(event)


def log_suspicious_pattern(
    consumer_id: str,
    ip_address: str,
    pattern: str,
    details: dict[str, Any],
    user_agent: Optional[str] = None
) -> None:
    """
    Log suspicious pattern detection.
    
    Args:
        consumer_id: Consumer identifier
        ip_address: Client IP address
        pattern: Pattern detected
        details: Additional details
        user_agent: Client user agent
    """
    event = AuditEvent(
        event_type=AuditEventType.SUSPICIOUS_PATTERN,
        timestamp=datetime.now(),
        consumer_id=consumer_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details={"pattern": pattern, **details},
        severity="ERROR"
    )
    log_audit_event(event)


def mask_ip_address(ip_address: str) -> str:
    """
    Mask IP address for privacy (GDPR compliance).
    
    Args:
        ip_address: IP address to mask
    
    Returns:
        Masked IP address
    """
    parts = ip_address.split(".")
    if len(parts) == 4:
        # Mask last 2 octets for IPv4
        return f"{parts[0]}.{parts[1]}.***"
    
    # For IPv6 or other formats, mask more aggressively
    if ":" in ip_address:
        parts = ip_address.split(":")
        if len(parts) >= 4:
            return f"{parts[0]}:{parts[1]}:***"
    
    return "***"
