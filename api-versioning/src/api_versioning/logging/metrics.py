"""
Version usage metrics logging and analytics.

This module provides structured logging for version adoption tracking,
deprecation impact analysis, and consumer migration monitoring.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


logger = logging.getLogger("api_versioning.metrics")


class ConsumerSource(str, Enum):
    """
    Source of consumer identity extraction.
    
    Values:
        API_KEY: From X-API-Key header
        OAUTH_CLIENT: From OAuth client ID
        CUSTOM_HEADER: From X-Consumer-ID header
        IP_ADDRESS: Fallback to IP address
    """
    
    API_KEY       = "API_KEY"
    OAUTH_CLIENT  = "OAUTH_CLIENT"
    CUSTOM_HEADER = "CUSTOM_HEADER"
    IP_ADDRESS    = "IP_ADDRESS"


@dataclass
class VersionUsageMetric:
    """
    Log entry for version usage tracking and analytics (FR-017).
    
    This dataclass captures all relevant information about version usage
    for adoption tracking, deprecation impact analysis, and consumer
    migration monitoring.
    
    Attributes:
        timestamp: When the request was processed (ISO 8601)
        version_id: Version used for this request
        endpoint_path: API endpoint accessed
        http_status: Response status code
        latency_ms: Request processing time in milliseconds
        consumer_id: Identifier for the API consumer
        consumer_source: How consumer identity was determined
        version_source: How version was specified (HEADER/URL_PATH/QUERY_PARAM/DEFAULT)
        is_deprecated_access: Whether accessed version is deprecated
    
    Example:
        >>> from datetime import datetime
        >>> metric = VersionUsageMetric(
        ...     timestamp=datetime.now(),
        ...     version_id="v2",
        ...     endpoint_path="/users",
        ...     http_status=200,
        ...     latency_ms=45.3,
        ...     consumer_id="client_abc123",
        ...     consumer_source=ConsumerSource.API_KEY,
        ...     version_source="HEADER",
        ...     is_deprecated_access=False
        ... )
        >>> log_version_usage(metric)
    """
    
    timestamp:            datetime
    version_id:           str
    endpoint_path:        str
    http_status:          int
    latency_ms:           float
    consumer_id:          str
    consumer_source:      ConsumerSource
    version_source:       str
    is_deprecated_access: bool
    
    def to_dict(self) -> dict[str, any]:
        """
        Convert metric to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of metric
        """
        return {
            "timestamp":            self.timestamp.isoformat(),
            "version_id":           self.version_id,
            "endpoint_path":        self.endpoint_path,
            "http_status":          self.http_status,
            "latency_ms":           self.latency_ms,
            "consumer_id":          self.consumer_id,
            "consumer_source":      self.consumer_source.value,
            "version_source":       self.version_source,
            "is_deprecated_access": self.is_deprecated_access,
        }
    
    def to_json(self) -> str:
        """
        Convert metric to JSON string for logging.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict())


def log_version_usage(metric: VersionUsageMetric) -> None:
    """
    Log version usage metric as structured JSON.
    
    This function emits structured JSON logs suitable for aggregation
    by log management systems (ELK, Splunk, CloudWatch Logs, etc.).
    
    Args:
        metric: Version usage metric to log
    
    Example:
        >>> from datetime import datetime
        >>> metric = VersionUsageMetric(
        ...     timestamp=datetime.now(),
        ...     version_id="v2",
        ...     endpoint_path="/users",
        ...     http_status=200,
        ...     latency_ms=45.3,
        ...     consumer_id="client_abc123",
        ...     consumer_source=ConsumerSource.API_KEY,
        ...     version_source="HEADER",
        ...     is_deprecated_access=False
        ... )
        >>> log_version_usage(metric)
    """
    logger.info(
        "version_usage",
        extra={"metric": metric.to_dict()}
    )


def extract_consumer_identity(
    headers: dict[bytes, bytes],
    client_ip: Optional[str] = None
) -> tuple[str, ConsumerSource]:
    """
    Extract consumer identity following FR-017 priority.
    
    Extraction Priority (highest to lowest):
        1. X-API-Key header ? source=API_KEY
        2. OAuth client ID from Authorization header ? source=OAUTH_CLIENT
        3. X-Consumer-ID custom header ? source=CUSTOM_HEADER
        4. IP address fallback ? source=IP_ADDRESS
    
    Args:
        headers: Request headers as bytes dictionary
        client_ip: Client IP address for fallback
    
    Returns:
        Tuple of (consumer_id, consumer_source)
    
    Example:
        >>> headers = {b"x-api-key": b"key_abc123"}
        >>> consumer_id, source = extract_consumer_identity(headers)
        >>> print(f"{consumer_id} from {source.value}")
        key_abc123 from API_KEY
    """
    # Priority 1: X-API-Key header
    for header_name, header_value in headers.items():
        if header_name.lower() == b"x-api-key":
            consumer_id = header_value.decode("utf-8", errors="ignore")
            return consumer_id, ConsumerSource.API_KEY
    
    # Priority 2: OAuth client ID from Authorization header
    for header_name, header_value in headers.items():
        if header_name.lower() == b"authorization":
            auth_value = header_value.decode("utf-8", errors="ignore")
            if auth_value.startswith("Bearer "):
                # Extract OAuth client ID (simplified - would use JWT parsing in production)
                consumer_id = f"oauth_{auth_value[:20]}"
                return consumer_id, ConsumerSource.OAUTH_CLIENT
    
    # Priority 3: X-Consumer-ID custom header
    for header_name, header_value in headers.items():
        if header_name.lower() == b"x-consumer-id":
            consumer_id = header_value.decode("utf-8", errors="ignore")
            return consumer_id, ConsumerSource.CUSTOM_HEADER
    
    # Priority 4: IP address fallback (FR-049)
    if client_ip:
        return client_ip, ConsumerSource.IP_ADDRESS
    
    return "anonymous", ConsumerSource.IP_ADDRESS


def mask_consumer_id(consumer_id: str, source: ConsumerSource) -> str:
    """
    Mask sensitive consumer identity data for logging (FR-025).
    
    This function implements hashing/masking for GDPR compliance
    while allowing analytics.
    
    Args:
        consumer_id: Consumer identifier
        source: Source of consumer identity
    
    Returns:
        Masked/hashed consumer identifier
    
    Example:
        >>> masked = mask_consumer_id("key_abc123", ConsumerSource.API_KEY)
        >>> print(masked)
        key_***  # Last digits masked
    """
    if source == ConsumerSource.IP_ADDRESS:
        # Mask IP address (keep first 2 octets for IPv4)
        parts = consumer_id.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.***"
        return consumer_id
    
    elif source == ConsumerSource.API_KEY:
        # Mask API key (keep prefix for debugging)
        if len(consumer_id) > 8:
            return consumer_id[:8] + "***"
        return "***"
    
    elif source == ConsumerSource.OAUTH_CLIENT:
        # Hash OAuth client ID
        import hashlib
        return hashlib.sha256(consumer_id.encode()).hexdigest()[:16]
    
    else:
        # Generic masking
        if len(consumer_id) > 4:
            return consumer_id[:4] + "***"
        return "***"
