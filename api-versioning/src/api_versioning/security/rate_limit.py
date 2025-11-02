"""
Rate limiting for API versioning endpoints (FR-026).

This module provides per-consumer, per-version rate limiting with
configurable thresholds and time windows.
"""

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RateLimitConfig:
    """
    Rate limit configuration.
    
    Attributes:
        requests_per_minute: Maximum requests allowed per minute
        burst_capacity: Maximum burst requests allowed
        window_seconds: Time window in seconds (default 60)
    """
    
    requests_per_minute: int
    burst_capacity:      int
    window_seconds:      int = 60


@dataclass
class RateLimitState:
    """
    Rate limit state for a consumer.
    
    Attributes:
        request_count: Number of requests in current window
        window_start: Start time of current window
        last_request: Timestamp of last request
    """
    
    request_count: int   = 0
    window_start:  float = field(default_factory=time.time)
    last_request:  float = field(default_factory=time.time)


@dataclass
class RateLimitResult:
    """
    Result of rate limit check.
    
    Attributes:
        allowed: Whether request is allowed
        remaining: Requests remaining in window
        reset_at: Timestamp when limit resets
        retry_after: Seconds to wait before retrying (if not allowed)
    """
    
    allowed:     bool
    remaining:   int
    reset_at:    float
    retry_after: Optional[int] = None


class RateLimiter:
    """
    Token bucket rate limiter with per-consumer tracking (FR-026).
    
    Implements sliding window rate limiting with burst capacity.
    
    Example:
        >>> limiter = RateLimiter(
        ...     RateLimitConfig(
        ...         requests_per_minute=1000,
        ...         burst_capacity=1200
        ...     )
        ... )
        >>> result = limiter.check_limit("consumer_1")
        >>> print(result.allowed)
        True
    """
    
    def __init__(
        self,
        config: RateLimitConfig,
        authenticated_config: Optional[RateLimitConfig] = None,
        anonymous_config: Optional[RateLimitConfig] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            config: Default rate limit configuration
            authenticated_config: Config for authenticated users
            anonymous_config: Config for anonymous users
        """
        self.config = config
        self.authenticated_config = authenticated_config or RateLimitConfig(
            requests_per_minute=1000,
            burst_capacity=1200
        )
        self.anonymous_config = anonymous_config or RateLimitConfig(
            requests_per_minute=100,
            burst_capacity=120
        )
        
        # State tracking per consumer
        self.states: dict[str, RateLimitState] = {}
    
    def check_limit(
        self,
        consumer_id: str,
        is_authenticated: bool = True
    ) -> RateLimitResult:
        """
        Check if request is within rate limits.
        
        Args:
            consumer_id: Consumer identifier
            is_authenticated: Whether consumer is authenticated
        
        Returns:
            RateLimitResult with limit check result
        """
        # Select configuration
        config = (
            self.authenticated_config if is_authenticated
            else self.anonymous_config
        )
        
        # Get or create state
        if consumer_id not in self.states:
            self.states[consumer_id] = RateLimitState()
        
        state = self.states[consumer_id]
        current_time = time.time()
        
        # Check if window expired
        window_elapsed = current_time - state.window_start
        if window_elapsed >= config.window_seconds:
            # Reset window
            state.window_start = current_time
            state.request_count = 0
        
        # Check if within limits
        if state.request_count < config.requests_per_minute:
            # Allow request
            state.request_count += 1
            state.last_request = current_time
            
            remaining = config.requests_per_minute - state.request_count
            reset_at = state.window_start + config.window_seconds
            
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                reset_at=reset_at
            )
        
        # Rate limit exceeded
        reset_at = state.window_start + config.window_seconds
        retry_after = int(reset_at - current_time)
        
        return RateLimitResult(
            allowed=False,
            remaining=0,
            reset_at=reset_at,
            retry_after=max(1, retry_after)
        )
    
    def reset_consumer(self, consumer_id: str) -> None:
        """
        Reset rate limit state for a consumer.
        
        Args:
            consumer_id: Consumer identifier
        """
        if consumer_id in self.states:
            del self.states[consumer_id]
    
    def get_remaining(self, consumer_id: str, is_authenticated: bool = True) -> int:
        """
        Get remaining requests for consumer.
        
        Args:
            consumer_id: Consumer identifier
            is_authenticated: Whether consumer is authenticated
        
        Returns:
            Number of remaining requests
        """
        config = (
            self.authenticated_config if is_authenticated
            else self.anonymous_config
        )
        
        if consumer_id not in self.states:
            return config.requests_per_minute
        
        state = self.states[consumer_id]
        current_time = time.time()
        
        # Check if window expired
        window_elapsed = current_time - state.window_start
        if window_elapsed >= config.window_seconds:
            return config.requests_per_minute
        
        return max(0, config.requests_per_minute - state.request_count)


def format_rate_limit_headers(result: RateLimitResult) -> dict[str, str]:
    """
    Format rate limit information as HTTP headers.
    
    Args:
        result: Rate limit check result
    
    Returns:
        Dictionary of header name -> value
    """
    headers = {
        "X-RateLimit-Remaining": str(result.remaining),
        "X-RateLimit-Reset": str(int(result.reset_at))
    }
    
    if result.retry_after is not None:
        headers["Retry-After"] = str(result.retry_after)
    
    return headers
