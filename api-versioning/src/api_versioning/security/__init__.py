"""Security modules for authentication, validation, and rate limiting."""

from api_versioning.security.audit import (
    AuditEvent,
    AuditEventType,
    log_audit_event,
    log_auth_failure,
    log_rate_limit_exceeded,
    log_suspicious_pattern,
    mask_ip_address,
)
from api_versioning.security.auth import (
    APIKeyAuthenticator,
    AuthMethod,
    AuthResult,
    OAuthAuthenticator,
    authenticate_request,
    extract_credentials_from_headers,
)
from api_versioning.security.rate_limit import (
    RateLimitConfig,
    RateLimitResult,
    RateLimiter,
    format_rate_limit_headers,
)

__all__ = [
    # Authentication
    "APIKeyAuthenticator",
    "OAuthAuthenticator",
    "AuthMethod",
    "AuthResult",
    "authenticate_request",
    "extract_credentials_from_headers",
    # Rate Limiting
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitResult",
    "format_rate_limit_headers",
    # Audit Logging
    "AuditEvent",
    "AuditEventType",
    "log_audit_event",
    "log_auth_failure",
    "log_rate_limit_exceeded",
    "log_suspicious_pattern",
    "mask_ip_address",
]
