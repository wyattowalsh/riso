"""
Circuit breaker for graceful degradation (FR-039, FR-044).

This module provides circuit breaker pattern implementation for
handling failures and degraded performance scenarios.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, TypeVar


T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker state."""
    
    CLOSED     = "CLOSED"      # Normal operation
    OPEN       = "OPEN"        # Failing, rejecting requests
    HALF_OPEN  = "HALF_OPEN"   # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """
    Circuit breaker configuration.
    
    Attributes:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes to close circuit from half-open
        timeout_seconds: Time to wait before trying half-open
    """
    
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds:   float = 60.0


class CircuitBreaker:
    """
    Circuit breaker for graceful degradation.
    
    Implements the circuit breaker pattern to prevent cascading failures
    and enable graceful degradation when dependencies fail.
    
    States:
        - CLOSED: Normal operation, all requests pass through
        - OPEN: Too many failures, rejecting requests
        - HALF_OPEN: Testing recovery, limited requests pass through
    
    Example:
        >>> breaker = CircuitBreaker("version_registry")
        >>> 
        >>> try:
        ...     with breaker.protect():
        ...         result = risky_operation()
        ... except CircuitBreakerOpen:
        ...     result = fallback_value
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Circuit breaker name for logging
            config: Configuration (uses defaults if None)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
    
    def call(self, func: Callable[[], T]) -> T:
        """
        Call function with circuit breaker protection.
        
        Args:
            func: Function to call
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: Any exception from func
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpen(self.name)
        
        try:
            result = func()
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure()
            raise
    
    def protect(self) -> "CircuitBreakerContext":
        """
        Context manager for circuit breaker protection.
        
        Returns:
            Circuit breaker context manager
        
        Example:
            >>> breaker = CircuitBreaker("api_call")
            >>> with breaker.protect():
            ...     result = api_call()
        """
        return CircuitBreakerContext(self)
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.timeout_seconds
    
    def _on_success(self) -> None:
        """Handle successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.config.success_threshold:
                # Close circuit - recovery successful
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed operation."""
        self.last_failure_time = time.time()
        self.failure_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery - reopen circuit
            self.state = CircuitState.OPEN
            self.success_count = 0
        
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                # Too many failures - open circuit
                self.state = CircuitState.OPEN
    
    def reset(self) -> None:
        """Manually reset circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None


class CircuitBreakerContext:
    """Context manager for circuit breaker protection."""
    
    def __init__(self, breaker: CircuitBreaker):
        """Initialize context."""
        self.breaker = breaker
    
    def __enter__(self) -> CircuitBreaker:
        """Enter context."""
        if self.breaker.state == CircuitState.OPEN:
            if not self.breaker._should_attempt_reset():
                raise CircuitBreakerOpen(self.breaker.name)
            self.breaker.state = CircuitState.HALF_OPEN
            self.breaker.success_count = 0
        
        return self.breaker
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        if exc_type is None:
            self.breaker._on_success()
        else:
            self.breaker._on_failure()


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    
    def __init__(self, circuit_name: str):
        """Initialize exception."""
        super().__init__(f"Circuit breaker '{circuit_name}' is open")
        self.circuit_name = circuit_name
