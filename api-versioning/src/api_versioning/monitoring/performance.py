"""
Performance metrics collection (FR-031 through FR-039).

This module provides performance monitoring for version routing operations
with p50/p95/p99 latency tracking and throughput measurement.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class OperationType(str, Enum):
    """Type of operation being measured."""
    
    VERSION_LOOKUP        = "VERSION_LOOKUP"
    PRECEDENCE_RESOLUTION = "PRECEDENCE_RESOLUTION"
    HEADER_INJECTION      = "HEADER_INJECTION"
    ROUTING               = "ROUTING"
    VALIDATION            = "VALIDATION"
    TOTAL_MIDDLEWARE      = "TOTAL_MIDDLEWARE"


@dataclass
class PerformanceMetric:
    """
    Performance measurement for an operation.
    
    Attributes:
        operation: Type of operation measured
        latency_ns: Latency in nanoseconds
        timestamp: When measurement was taken
        version_id: Version being processed
        cache_hit: Whether cache was used
        memory_bytes: Memory used (if applicable)
    """
    
    operation:    OperationType
    latency_ns:   int
    timestamp:    float
    version_id:   Optional[str] = None
    cache_hit:    Optional[bool] = None
    memory_bytes: Optional[int] = None


@dataclass
class PerformanceStats:
    """
    Aggregated performance statistics.
    
    Attributes:
        operation: Operation type
        count: Number of measurements
        p50_latency_ns: 50th percentile latency
        p95_latency_ns: 95th percentile latency
        p99_latency_ns: 99th percentile latency
        min_latency_ns: Minimum latency
        max_latency_ns: Maximum latency
        avg_latency_ns: Average latency
    """
    
    operation:      OperationType
    count:          int
    p50_latency_ns: int
    p95_latency_ns: int
    p99_latency_ns: int
    min_latency_ns: int
    max_latency_ns: int
    avg_latency_ns: int


class PerformanceMonitor:
    """
    Performance monitoring with latency tracking (FR-031).
    
    Tracks operation latencies and computes percentiles for SLA monitoring.
    
    Example:
        >>> monitor = PerformanceMonitor()
        >>> 
        >>> with monitor.measure(OperationType.VERSION_LOOKUP, "v2"):
        ...     # Operation code here
        ...     pass
        >>> 
        >>> stats = monitor.get_stats(OperationType.VERSION_LOOKUP)
        >>> print(f"p99: {stats.p99_latency_ns}ns")
    """
    
    def __init__(self, max_samples: int = 10000):
        """
        Initialize performance monitor.
        
        Args:
            max_samples: Maximum samples to keep per operation
        """
        self.max_samples = max_samples
        self.metrics: dict[OperationType, list[PerformanceMetric]] = {}
    
    def record(self, metric: PerformanceMetric) -> None:
        """
        Record a performance metric.
        
        Args:
            metric: Performance metric to record
        """
        if metric.operation not in self.metrics:
            self.metrics[metric.operation] = []
        
        metrics_list = self.metrics[metric.operation]
        metrics_list.append(metric)
        
        # Keep only recent samples
        if len(metrics_list) > self.max_samples:
            metrics_list.pop(0)
    
    def measure(
        self,
        operation: OperationType,
        version_id: Optional[str] = None
    ) -> "PerformanceMeasurement":
        """
        Context manager for measuring operation latency.
        
        Args:
            operation: Type of operation
            version_id: Version being processed
        
        Returns:
            Performance measurement context manager
        
        Example:
            >>> monitor = PerformanceMonitor()
            >>> with monitor.measure(OperationType.VERSION_LOOKUP, "v2"):
            ...     # Operation code
            ...     pass
        """
        return PerformanceMeasurement(self, operation, version_id)
    
    def get_stats(self, operation: OperationType) -> Optional[PerformanceStats]:
        """
        Get aggregated statistics for an operation.
        
        Args:
            operation: Operation type
        
        Returns:
            PerformanceStats if measurements exist, None otherwise
        """
        if operation not in self.metrics or not self.metrics[operation]:
            return None
        
        metrics_list = self.metrics[operation]
        latencies = sorted([m.latency_ns for m in metrics_list])
        
        count = len(latencies)
        if count == 0:
            return None
        
        return PerformanceStats(
            operation=operation,
            count=count,
            p50_latency_ns=self._percentile(latencies, 0.50),
            p95_latency_ns=self._percentile(latencies, 0.95),
            p99_latency_ns=self._percentile(latencies, 0.99),
            min_latency_ns=latencies[0],
            max_latency_ns=latencies[-1],
            avg_latency_ns=sum(latencies) // count
        )
    
    @staticmethod
    def _percentile(sorted_values: list[int], percentile: float) -> int:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0
        
        index = int(len(sorted_values) * percentile)
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
    
    def clear(self, operation: Optional[OperationType] = None) -> None:
        """
        Clear metrics.
        
        Args:
            operation: Specific operation to clear, or None for all
        """
        if operation:
            if operation in self.metrics:
                self.metrics[operation].clear()
        else:
            self.metrics.clear()


class PerformanceMeasurement:
    """
    Context manager for measuring operation latency.
    
    Example:
        >>> monitor = PerformanceMonitor()
        >>> with PerformanceMeasurement(monitor, OperationType.VERSION_LOOKUP):
        ...     # Operation code
        ...     pass
    """
    
    def __init__(
        self,
        monitor: PerformanceMonitor,
        operation: OperationType,
        version_id: Optional[str] = None
    ):
        """Initialize measurement."""
        self.monitor = monitor
        self.operation = operation
        self.version_id = version_id
        self.start_time: Optional[float] = None
    
    def __enter__(self) -> "PerformanceMeasurement":
        """Start measurement."""
        self.start_time = time.perf_counter_ns()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """End measurement and record."""
        if self.start_time is not None:
            latency_ns = time.perf_counter_ns() - self.start_time
            
            metric = PerformanceMetric(
                operation=self.operation,
                latency_ns=latency_ns,
                timestamp=time.time(),
                version_id=self.version_id
            )
            
            self.monitor.record(metric)


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_global_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def measure_operation(
    operation: OperationType,
    version_id: Optional[str] = None
) -> PerformanceMeasurement:
    """
    Convenience function for measuring operation latency.
    
    Args:
        operation: Type of operation
        version_id: Version being processed
    
    Returns:
        Performance measurement context manager
    
    Example:
        >>> from api_versioning.monitoring import measure_operation, OperationType
        >>> 
        >>> with measure_operation(OperationType.VERSION_LOOKUP, "v2"):
        ...     # Operation code
        ...     pass
    """
    monitor = get_global_monitor()
    return monitor.measure(operation, version_id)
