# Feature Specification: API Rate Limiting & Throttling

**Status:** Draft  
**Owner:** Platform Team  
**Created:** 2025-10-30  
**Updated:** 2025-10-30

---

## Overview

### Purpose
Implement a comprehensive rate limiting and throttling system to protect API endpoints from abuse, ensure fair resource usage across clients, and maintain service availability under high load conditions. The system will provide configurable per-client, per-endpoint, and per-user rate limits with distributed enforcement.

### Context
As API usage scales, protecting endpoints from abuse and ensuring fair resource allocation becomes critical. Rate limiting prevents:
- Denial-of-service attacks (intentional or accidental)
- Resource exhaustion from runaway clients
- Unfair resource consumption by individual users
- API abuse and credential stuffing attempts

This feature builds on the existing FastAPI scaffold (006) and integrates with the quality suite (003), container deployment (005), and future monitoring capabilities.

### Business Value
- **Reliability:** Prevents service degradation from abusive or misconfigured clients
- **Fairness:** Ensures all users get reasonable access to API resources
- **Security:** Reduces attack surface for brute-force and credential stuffing attacks
- **Compliance:** Supports SLA enforcement and usage-based billing models
- **Observability:** Provides metrics for capacity planning and abuse detection

---

## User Scenarios

### US1: Basic Per-Client Rate Limiting (Priority: P1)
**As a** platform operator  
**I want** to limit the number of requests any single IP address can make  
**So that** no single client can monopolize API resources or launch denial-of-service attacks

**Acceptance Scenarios:**
```gherkin
Given an API endpoint with a 100 requests/minute IP-based limit
When a client from IP 192.0.2.1 makes 100 requests in 50 seconds
Then all 100 requests succeed with HTTP 200
And the X-RateLimit-Remaining header shows decreasing values

When the same client makes the 101st request within the same minute
Then the request is rejected with HTTP 429 (Too Many Requests)
And the X-RateLimit-Remaining header shows 0
And the Retry-After header indicates seconds until limit reset
```

**Requirements:**
- Track requests per originating IP address using sliding window
- Return HTTP 429 when limit exceeded
- Include rate limit headers in all responses (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- Handle IPv4 and IPv6 addresses correctly

---

### US2: Per-Endpoint Rate Limiting (Priority: P1)
**As a** platform operator  
**I want** to configure different rate limits for different API endpoints  
**So that** resource-intensive endpoints can have stricter limits than lightweight ones

**Acceptance Scenarios:**
```gherkin
Given two endpoints:
  - GET /api/v1/health with 1000 requests/minute limit
  - POST /api/v1/compute with 10 requests/minute limit

When a client makes 15 requests to /api/v1/health in 10 seconds
Then all 15 requests succeed
And the health endpoint limit counter is at 15/1000

When the same client makes 11 requests to /api/v1/compute in 10 seconds
Then the first 10 requests succeed
And the 11th request returns HTTP 429
And the health endpoint is still accessible
```

**Requirements:**
- Support per-endpoint rate limit configuration in TOML config
- Maintain separate counters for each endpoint
- Allow wildcard patterns (e.g., `/api/v1/admin/*` gets 5 req/min)
- Default rate limit applies to endpoints without explicit configuration

---

### US3: Authenticated User Rate Limiting (Priority: P1)
**As a** platform operator  
**I want** to apply rate limits based on authenticated user identity  
**So that** authenticated users get higher limits than anonymous IP-based clients

**Acceptance Scenarios:**
```gherkin
Given rate limit configuration:
  - Anonymous (IP-based): 100 requests/minute
  - Authenticated users: 1000 requests/minute
  - Premium users: 5000 requests/minute

When an unauthenticated request arrives
Then it is limited to 100 requests/minute based on source IP

When a request includes valid JWT with user_id=alice and tier=standard
Then it is limited to 1000 requests/minute based on user_id
And IP-based limit does not apply

When a request includes valid JWT with user_id=bob and tier=premium
Then it is limited to 5000 requests/minute
And X-RateLimit-Limit header shows 5000
```

**Requirements:**
- Extract user identity from JWT tokens (user_id claim)
- Support tier-based limits (read from JWT `tier` claim or user database)
- Fall back to IP-based limiting for unauthenticated requests
- Prioritize user-based limits over IP-based limits when both apply

---

### US4: Rate Limit Configuration Management (Priority: P2)
**As a** platform operator  
**I want** to configure rate limits through TOML files and environment variables  
**So that** I can adjust limits without code changes or redeployment

**Acceptance Scenarios:**
```gherkin
Given a configuration file config.toml:
  [rate_limiting]
  default_limit = 100
  default_window = 60
  
  [[rate_limiting.endpoints]]
  pattern = "/api/v1/search"
  limit = 20
  window = 60
  
  [[rate_limiting.tiers]]
  name = "premium"
  limit = 5000
  window = 60

When the FastAPI application starts
Then it loads configuration from config.toml
And applies the default 100 req/min limit to unspecified endpoints
And applies 20 req/min limit to /api/v1/search
And applies 5000 req/min limit to users with tier=premium

When the operator updates config.toml and sends SIGHUP
Then the application reloads configuration without downtime
And new limits take effect for subsequent requests
And existing counters are preserved during reload
```

**Requirements:**
- TOML configuration schema for default, endpoint-specific, and tier-based limits
- Environment variable overrides (e.g., `RATE_LIMIT_DEFAULT=200`)
- Configuration validation at startup (reject invalid patterns or negative limits)
- Hot reload capability via SIGHUP signal or admin endpoint
- Backward compatibility: missing config uses safe defaults (100 req/min)

---

### US5: Distributed Rate Limiting (Priority: P2)
**As a** platform operator  
**I want** rate limits to be enforced consistently across multiple API server instances  
**So that** scaling horizontally doesn't create loopholes in rate limiting

**Acceptance Scenarios:**
```gherkin
Given a load-balanced API with 3 instances (api-1, api-2, api-3)
And Redis-backed distributed rate limiting
And a limit of 100 requests/minute for IP 198.51.100.42

When the client makes 40 requests to api-1
And 35 requests to api-2
And 25 requests to api-3
All within 30 seconds

Then the total request count in Redis is 100
And all 100 requests succeed
And the next request to any instance returns HTTP 429

When instance api-2 fails
Then rate limiting continues to work on api-1 and api-3
And counters in Redis remain accurate
```

**Requirements:**
- Use Redis as shared state backend for rate limit counters
- Implement atomic increment operations (INCR, EXPIRE) to prevent race conditions
- Handle Redis connection failures gracefully (fail open or closed based on config)
- Support Redis Cluster and Redis Sentinel for high availability
- Minimize Redis round trips (pipeline multiple commands when possible)

---

### US6: Rate Limit Monitoring & Observability (Priority: P2)
**As a** platform operator  
**I want** metrics and logs for rate limiting activity  
**So that** I can detect abuse patterns and optimize limits

**Acceptance Scenarios:**
```gherkin
When a request is rate-limited
Then the application logs:
  - Timestamp
  - Client identifier (IP or user_id)
  - Endpoint
  - Limit configuration (e.g., "100/60s")
  - Current count
  - Rate limit exceeded message

And Prometheus metrics are updated:
  - rate_limit_requests_total{endpoint, tier, status} (counter)
  - rate_limit_exceeded_total{endpoint, tier, client_type} (counter)
  - rate_limit_current_usage{endpoint, tier, client_id} (gauge)
  - rate_limit_redis_latency_seconds (histogram)

When the operator queries Prometheus
Then they can see:
  - Top rate-limited clients
  - Endpoints with highest rejection rates
  - Redis latency distribution
  - Time-series graphs of rate limit violations
```

**Requirements:**
- Structured JSON logs for rate limit events
- Prometheus metrics for monitoring and alerting
- Include client metadata (IP, user_id, tier) in metrics labels
- Log rate limit violations at INFO level (not ERROR)
- Emit metrics for successful requests showing remaining capacity

---

### US7: Rate Limit Response Headers (Priority: P3)
**As an** API client developer  
**I want** standard rate limit headers in all API responses  
**So that** I can implement intelligent retry logic and backoff strategies

**Acceptance Scenarios:**
```gherkin
Given an endpoint with 100 requests/minute limit
When a client makes their 50th request in the current minute
Then the response includes headers:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 50
  X-RateLimit-Reset: 1698765432 (Unix timestamp)

When the client makes their 101st request (limit exceeded)
Then the response includes:
  Status: 429 Too Many Requests
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1698765492
  Retry-After: 30 (seconds until reset)
  
And the response body contains JSON:
  {
    "error": "rate_limit_exceeded",
    "message": "Rate limit of 100 requests per 60 seconds exceeded",
    "retry_after_seconds": 30
  }
```

**Requirements:**
- Implement standard RateLimit headers (draft RFC 6585 and draft RFC 9110)
- Include X-RateLimit-* headers in all responses (200, 429, 5xx)
- Include Retry-After header in 429 responses with seconds until reset
- Provide JSON error body with actionable information
- Support both Unix timestamp and HTTP-date format for Reset header

---

## Functional Requirements

### FR-001: Rate Limit Enforcement
The system MUST enforce rate limits by rejecting requests that exceed configured thresholds, returning HTTP 429 status code with appropriate headers and error body.

**Validation:** Integration test showing request 101 rejected when limit is 100/minute.

---

### FR-002: Standard Rate Limit Headers
All API responses MUST include standard rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) regardless of whether the request was rate-limited.

**Validation:** Automated test verifying headers present in 200, 429, and 500 responses.

---

### FR-003: Token Bucket Algorithm
The system MUST implement the token bucket algorithm for rate limiting, allowing short bursts while enforcing average rate limits over time windows.

**Validation:** Test demonstrating burst of 100 requests succeeds if followed by idle period, but sustained 101 req/min fails.

---

### FR-004: Redis Backend for Distributed Limiting
The system MUST use Redis as the backend for rate limit counters to ensure consistent enforcement across multiple API instances.

**Validation:** Load test with 3+ instances showing total requests across all instances honored.

---

### FR-005: Graceful Redis Failure Handling
The system MUST handle Redis connection failures gracefully, with configurable behavior: fail-open (allow requests), fail-closed (reject requests), or circuit-breaker pattern.

**Validation:** Test with Redis unavailable showing configured failure mode (pass when Redis down if fail-open configured).

---

### FR-006: IP-Based Rate Limiting
The system MUST support rate limiting based on client IP address (both IPv4 and IPv6) for unauthenticated requests.

**Validation:** Test with IPv4 and IPv6 clients showing independent rate limit counters.

---

### FR-007: User-Based Rate Limiting
The system MUST support rate limiting based on authenticated user identity extracted from JWT tokens (user_id claim), with priority over IP-based limits.

**Validation:** Test showing authenticated user with 1000 req/min limit exceeds IP-based 100 req/min limit successfully.

---

### FR-008: Tier-Based Rate Limits
The system MUST support multiple rate limit tiers (e.g., anonymous, standard, premium) with different thresholds, configurable via TOML and user JWT claims.

**Validation:** Test with users in different tiers receiving different limits (100, 1000, 5000 req/min).

---

### FR-009: Per-Endpoint Rate Limits
The system MUST support configuring different rate limits for different API endpoints, including wildcard patterns (e.g., `/api/v1/admin/*`).

**Validation:** Test showing /health endpoint allows 1000 req/min while /compute endpoint allows 10 req/min for the same client.

---

### FR-010: TOML Configuration Schema
The system MUST load rate limit configuration from TOML files with schema supporting default limits, per-endpoint limits, tier definitions, and Redis connection settings.

**Validation:** Test loading valid config.toml and rejecting invalid configurations (negative limits, malformed patterns).

---

### FR-011: Environment Variable Overrides
The system MUST support environment variable overrides for critical configuration (e.g., `RATE_LIMIT_DEFAULT`, `REDIS_URL`) with precedence over TOML config.

**Validation:** Test showing env var `RATE_LIMIT_DEFAULT=200` overrides config.toml value of 100.

---

### FR-012: Configuration Hot Reload
The system SHOULD support hot reload of rate limit configuration via SIGHUP signal or admin endpoint, preserving existing counters.

**Validation:** Test showing config change applied without restarting application and without resetting counters.

---

### FR-013: Atomic Counter Operations
The system MUST use atomic Redis operations (INCR, EXPIRE) to prevent race conditions when multiple instances update counters concurrently.

**Validation:** Concurrency test with 10 clients and 3 instances showing accurate total count ±1% margin of error.

---

### FR-014: Retry-After Header
HTTP 429 responses MUST include Retry-After header indicating seconds until rate limit resets, enabling intelligent client retry logic.

**Validation:** Test verifying Retry-After value matches X-RateLimit-Reset timestamp.

---

### FR-015: JSON Error Response
HTTP 429 responses MUST include JSON body with error code, human-readable message, and retry_after_seconds field.

**Validation:** Test verifying JSON schema of 429 response body.

---

### FR-016: Prometheus Metrics
The system MUST export Prometheus metrics for rate limiting activity, including total requests, rejections, current usage, and Redis latency.

**Validation:** Test scraping /metrics endpoint and verifying presence of rate_limit_* metrics.

---

### FR-017: Structured Logging
The system MUST emit structured JSON logs for rate limit events with fields: timestamp, client_id, endpoint, limit_config, current_count, status.

**Validation:** Test verifying JSON log format and required fields present.

---

### FR-018: Rate Limit Bypass for Exemptions
The system SHOULD support exemption list (IP addresses or user IDs) that bypass rate limiting for testing or admin access.

**Validation:** Test showing exempted IP makes 1000 requests successfully despite 100 req/min limit.

---

### FR-019: Sliding Window Algorithm Option
The system SHOULD support sliding window algorithm as an alternative to token bucket, configurable per endpoint.

**Validation:** Test showing sliding window prevents limit bypass through window boundary exploitation.

---

### FR-020: Multiple Time Windows
The system SHOULD support multiple concurrent time windows (e.g., 100/minute AND 1000/hour) with rejection when any limit exceeded.

**Validation:** Test showing 100 req/min passes but 1001st request in hour rejected.

---

## Success Criteria

### SC-001: Configuration Simplicity
**Metric:** Developers can configure basic rate limiting (IP-based, single endpoint) in <5 minutes following documentation.  
**Target:** 90% of users configure successfully without support tickets.

---

### SC-002: Rate Limit Accuracy
**Metric:** Actual requests processed vs. configured limit.  
**Target:** 99% accuracy (±1 request per 100 limit) under normal load.

---

### SC-003: Low Performance Overhead
**Metric:** P95 latency increase for rate-limited endpoints.  
**Target:** <5ms added latency at P95, <10ms at P99.

---

### SC-004: Redis Connection Pooling
**Metric:** Redis connection count per API instance.  
**Target:** ≤10 connections per instance regardless of request volume.

---

### SC-005: Concurrent Request Handling
**Metric:** Accuracy under 1000 concurrent requests from 100 clients.  
**Target:** Total requests processed within 2% of aggregate limits.

---

### SC-006: Distributed Consistency
**Metric:** Counter accuracy across 3+ API instances with load balancer.  
**Target:** 98% accuracy (within ±2 requests per 100 limit) in distributed setup.

---

### SC-007: Header Compliance
**Metric:** Presence of X-RateLimit-* headers in responses.  
**Target:** 100% of responses include all three headers (Limit, Remaining, Reset).

---

### SC-008: Retry-After Accuracy
**Metric:** Retry-After header value vs. actual reset time.  
**Target:** Within ±2 seconds of actual reset time.

---

### SC-009: Documentation Completeness
**Metric:** Documentation coverage of configuration, headers, error handling, troubleshooting.  
**Target:** All user stories have corresponding documentation with examples.

---

### SC-010: Test Coverage
**Metric:** Code coverage for rate limiting module.  
**Target:** ≥90% line coverage, ≥80% branch coverage.

---

### SC-011: Prometheus Metrics Availability
**Metric:** Metrics exported within 1 second of rate limit event.  
**Target:** 99% of events reflected in metrics within 1 second.

---

### SC-012: Redis Failure Recovery
**Metric:** API availability during Redis outage with fail-open mode.  
**Target:** 0% request rejection due to Redis failure in fail-open mode.

---

### SC-013: Configuration Validation
**Metric:** Invalid configurations rejected at startup.  
**Target:** 100% of invalid configs (negative limits, malformed patterns) rejected with clear error message.

---

### SC-014: Client Library Compatibility
**Metric:** Standard HTTP clients can parse rate limit headers without custom code.  
**Target:** Headers conform to draft RFCs, parseable by Python requests, JavaScript fetch, curl.

---

## Edge Cases & Error Handling

### Zero-Request Limits
**Scenario:** Endpoint configured with limit=0.  
**Behavior:** Reject all requests with HTTP 429, document as "maintenance mode" pattern.  
**Validation:** Test showing limit=0 rejects first request.

### Clock Skew
**Scenario:** API instances have system clocks out of sync by >5 seconds.  
**Behavior:** Use Redis server time (TIME command) for timestamps to ensure consistency.  
**Validation:** Test with instances at different wall clock times showing accurate limiting.

### Burst Traffic
**Scenario:** Client sends 100 requests in first second of rate limit window.  
**Behavior:** Token bucket allows burst, subsequent requests throttled until tokens replenish.  
**Validation:** Test showing 100 req/min limit allows 100 immediate requests, then enforces average rate.

### Rate Limit Configuration Changes
**Scenario:** Operator reduces limit from 1000 to 100 req/min while clients are active.  
**Behavior:** Existing counters preserved but compared against new limit; some clients immediately hit limit.  
**Validation:** Test showing limit reduction takes effect within 1 second without resetting counters.

### Redis Key Expiration Race Condition
**Scenario:** Counter key expires between GET and INCR operations.  
**Behavior:** Use INCR+EXPIRE in pipeline to atomically create and set expiration if key missing.  
**Validation:** Test with artificially short expiration (1 second) showing no counter loss.

### IPv6 Address Normalization
**Scenario:** Same IPv6 address represented in different formats (compressed vs. expanded).  
**Behavior:** Normalize IPv6 addresses to canonical form before using as cache key.  
**Validation:** Test showing `2001:db8::1` and `2001:0db8:0000:0000:0000:0000:0000:0001` counted together.

### Missing JWT Claims
**Scenario:** JWT token present but missing `user_id` or `tier` claim.  
**Behavior:** Fall back to IP-based limiting, log warning about missing claim.  
**Validation:** Test showing JWT without user_id uses IP-based limit.

### Redis Connection Pool Exhaustion
**Scenario:** All Redis connections in use, new request arrives.  
**Behavior:** Wait for available connection with timeout (5s), then fail-open or fail-closed based on config.  
**Validation:** Test with connection pool size=2 and 10 concurrent requests showing graceful handling.

### Multiple Rate Limit Windows
**Scenario:** Endpoint has 100/minute AND 1000/hour limits; client exhausts minute limit.  
**Behavior:** Reject with 429 including both limits in response body, show shortest Retry-After.  
**Validation:** Test showing 101st request in minute rejected even though hour limit not exceeded.

### Exemption List Bypass
**Scenario:** Admin IP in exemption list makes 10,000 requests.  
**Behavior:** All requests succeed, no counters incremented, metrics track exempted requests separately.  
**Validation:** Test showing exempted IP bypasses limit while non-exempted IP blocked at 100.

### Progressive Rate Limit Penalties
**Scenario:** Client repeatedly hits rate limit (100+ violations in hour).  
**Behavior:** Optionally increase cooldown period exponentially (1x, 2x, 4x timeout), configurable feature.  
**Validation:** Test showing 3rd violation requires waiting 4x normal reset period.

### Redis Sentinel Failover
**Scenario:** Redis master fails, Sentinel promotes replica.  
**Behavior:** Redis client automatically reconnects to new master, rate limit counters preserved in replica.  
**Validation:** Test with Redis Sentinel showing <1s of rate limiting disruption during failover.

---

## Dependencies

### Required Dependencies
- **FastAPI** ≥0.104.0 (feature 006-fastapi-api-scaffold)
  - Provides web framework for middleware integration
  - Dependency injection for rate limiter instances
  - Request/response lifecycle hooks

- **Redis** ≥6.0
  - Persistent storage for distributed rate limit counters
  - Atomic operations (INCR, EXPIRE) for counter management
  - Pub/sub for configuration updates (optional)

- **redis-py** ≥5.0 OR **aioredis** ≥2.0
  - Python client for Redis operations
  - Connection pooling and circuit breaker support
  - Async/await support for FastAPI

- **Pydantic** ≥2.0
  - Configuration schema validation
  - TOML config parsing and validation
  - Settings management with env var overrides

### Optional Dependencies
- **prometheus-client** ≥0.16.0
  - Metrics export for monitoring integration
  - Counter, Gauge, Histogram for rate limit metrics

- **structlog** ≥23.0
  - Structured logging for rate limit events
  - JSON log formatting for log aggregation

### Dependent Features
This feature is a **foundation** for:
- **API Usage Billing** (future): Accurate usage tracking for metered billing
- **API Abuse Detection** (future): Patterns in rate limit violations inform abuse rules
- **SLA Enforcement** (future): Different limits per customer tier

This feature **depends on**:
- **FastAPI API Scaffold** (006): Requires middleware integration points
- **Container Deployment** (005): Redis containers in docker-compose
- **Quality Suite** (003): Testing and validation infrastructure

### Integration Points
- **Monitoring/Observability** (future 010): Prometheus metrics, distributed tracing spans for rate limit checks
- **Authentication** (future): JWT claims extraction for user-based limiting
- **Configuration Management**: TOML config loading, env var overrides

---

## Out of Scope

The following are explicitly **out of scope** for this feature:

### Dynamic Rate Limit Adjustment
Automatically adjusting rate limits based on system load or user behavior is not included. Operators must manually update configuration. Future feature could implement autoscaling-aware limits.

### Geographic/Regional Rate Limiting
Applying different limits based on client country or region requires geolocation database (e.g., MaxMind GeoIP2) and is deferred to future work.

### Payment-Based Rate Limits
Integration with payment/billing systems to automatically provision higher limits for paying customers is out of scope. User tier must be manually set in JWT claims or config.

### Admin UI for Rate Limit Configuration
Web-based admin interface for managing rate limits is out of scope. Configuration must be done via TOML files and deployments.

### Rate Limit Analytics Dashboard
Pre-built dashboards for visualizing rate limit metrics are out of scope. Operators must build Grafana dashboards using exported Prometheus metrics.

### Machine Learning-Based Abuse Detection
Using ML models to detect anomalous traffic patterns and dynamically block abusive clients is out of scope. Static exemption lists and manual analysis only.

### WebSocket/Server-Sent Events Rate Limiting
Rate limiting for long-lived connections (WebSocket, SSE) requires different counter semantics (messages/second vs. connections/minute) and is deferred to feature 008-websockets-scaffold.

### Request Size-Based Limiting
Rate limiting based on request body size or response payload size (e.g., "100 MB/minute") is out of scope. Only request count is tracked.

### Client SDK with Automatic Retry
Providing official client libraries with built-in rate limit handling and exponential backoff is out of scope. Clients must implement retry logic using standard headers.

### Distributed Tracing Integration
Adding trace spans for rate limit checks to correlate with upstream/downstream services is deferred to future observability work.

---

## Technical Considerations

### Algorithm Choice: Token Bucket vs. Sliding Window
- **Token Bucket** (recommended): Allows natural bursts, simpler implementation, easier to reason about.
- **Sliding Window**: More accurate for strict "requests per time window" enforcement, higher Redis overhead (requires sorted sets).
- **Recommendation:** Implement token bucket as default, add sliding window as optional algorithm via config flag.

### Redis Data Structures
- **Simple Counter**: Use STRING type with INCR + EXPIRE for basic per-client counters.
- **Token Bucket**: Use HASH with fields `{tokens, last_refill}`, or Lua script for atomic refill+decrement.
- **Sliding Window**: Use ZSET with timestamps, ZREMRANGEBYSCORE to prune old entries.

### Key Naming Convention
```
ratelimit:{scope}:{identifier}:{endpoint}
Examples:
  ratelimit:ip:192.0.2.1:/api/v1/search
  ratelimit:user:alice:/api/v1/compute
  ratelimit:tier:premium:global
```

### Redis Connection Pooling
- Use connection pool size = 2x number of worker threads (e.g., 10 workers → 20 connections).
- Set socket timeout = 5s to prevent blocking on slow Redis.
- Implement circuit breaker pattern: open circuit after 3 consecutive failures, half-open after 30s.

### Middleware Implementation (FastAPI)
```python
# Pseudocode - NOT implementation
from fastapi import Request, HTTPException, status

async def rate_limit_middleware(request: Request, call_next):
    # 1. Extract client identifier (IP or user_id from JWT)
    client_id = get_client_id(request)
    endpoint = request.url.path
    
    # 2. Get applicable rate limit config
    limit_config = get_limit_config(endpoint, client_id)
    
    # 3. Check rate limit in Redis
    allowed, remaining, reset_at = await check_rate_limit(client_id, endpoint, limit_config)
    
    # 4. Add headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(limit_config.limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_at)
    
    # 5. Reject if limit exceeded
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limit_exceeded", "retry_after_seconds": reset_at - now()},
            headers={"Retry-After": str(reset_at - now())}
        )
    
    return response
```

### Configuration Schema (TOML)
```toml
[rate_limiting]
enabled = true
default_limit = 100
default_window = 60  # seconds
algorithm = "token_bucket"  # or "sliding_window"
failure_mode = "fail_open"  # or "fail_closed"

[rate_limiting.redis]
url = "redis://localhost:6379/0"
pool_size = 20
socket_timeout = 5.0
circuit_breaker_threshold = 3
circuit_breaker_timeout = 30

[[rate_limiting.endpoints]]
pattern = "/api/v1/search"
limit = 20
window = 60

[[rate_limiting.endpoints]]
pattern = "/api/v1/admin/*"
limit = 5
window = 60

[[rate_limiting.tiers]]
name = "anonymous"
limit = 100
window = 60

[[rate_limiting.tiers]]
name = "standard"
limit = 1000
window = 60

[[rate_limiting.tiers]]
name = "premium"
limit = 5000
window = 60

[[rate_limiting.exemptions]]
type = "ip"
value = "192.0.2.0/24"

[[rate_limiting.exemptions]]
type = "user_id"
value = "admin"
```

### Performance Optimization
- **Pipeline Redis Commands**: Batch INCR + EXPIRE into single round trip.
- **Cache Config Locally**: Load rate limit config once at startup, cache in memory.
- **Skip Rate Limit for Health Checks**: Exempt `/health`, `/metrics` endpoints.
- **Pre-Check Before Redis**: If local in-memory counter shows limit far from exceeded, skip Redis call (risk of slight over-limiting).

### Security Considerations
- **IP Spoofing**: Validate X-Forwarded-For header, trust only from configured load balancer IPs.
- **JWT Validation**: Verify signature and expiration before extracting user_id/tier claims.
- **Redis ACLs**: Configure Redis user with minimal permissions (GET, SET, INCR, EXPIRE only).
- **DoS via Configuration**: Validate rate limits are non-negative and windows are ≥1 second to prevent accidental DoS.

### Observability
- **Prometheus Metrics:**
  ```
  rate_limit_requests_total{endpoint, tier, status}
  rate_limit_exceeded_total{endpoint, tier, client_type}
  rate_limit_current_usage{endpoint, tier, client_id}  # Gauge
  rate_limit_redis_latency_seconds{operation}  # Histogram
  rate_limit_redis_errors_total{operation, error_type}
  ```

- **Structured Logs (JSON):**
  ```json
  {
    "timestamp": "2025-10-30T12:34:56Z",
    "level": "INFO",
    "event": "rate_limit_exceeded",
    "client_id": "192.0.2.1",
    "user_id": "alice",
    "endpoint": "/api/v1/search",
    "limit": 20,
    "window": 60,
    "current_count": 21,
    "tier": "standard"
  }
  ```

### Testing Strategy
- **Unit Tests**: Token bucket logic, config parsing, header generation.
- **Integration Tests**: FastAPI + Redis, verify 429 responses and headers.
- **Load Tests**: 1000 req/s with 100 concurrent clients, verify accuracy within 2%.
- **Chaos Tests**: Kill Redis mid-request, verify fail-open/fail-closed behavior.
- **Distributed Tests**: 3 FastAPI instances + Redis, verify total count across instances.

---

## References

### Standards & RFCs
- [RFC 6585](https://www.rfc-editor.org/rfc/rfc6585.html) - Additional HTTP Status Codes (429 Too Many Requests)
- [draft-ietf-httpapi-ratelimit-headers](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers) - RateLimit Header Fields for HTTP

### Related Features
- **006-fastapi-api-scaffold**: FastAPI middleware integration points
- **003-code-quality-integrations**: Testing infrastructure
- **005-container-deployment**: Redis container orchestration

### External Resources
- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
- [Redis INCR Documentation](https://redis.io/commands/incr/)
- [FastAPI Middleware Guide](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Stripe Rate Limiting Design](https://stripe.com/blog/rate-limiters) (industry best practices)

---

## Appendix: Example Rate Limit Responses

### Successful Request (Within Limit)
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1698765492

{
  "status": "success",
  "data": { ... }
}
```

### Rate Limited Request
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1698765492
Retry-After: 30

{
  "error": "rate_limit_exceeded",
  "message": "Rate limit of 100 requests per 60 seconds exceeded for endpoint /api/v1/search",
  "retry_after_seconds": 30,
  "limit": 100,
  "window_seconds": 60,
  "documentation_url": "https://docs.example.com/rate-limiting"
}
```

### Multiple Time Windows Exceeded
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1698765492
Retry-After: 30

{
  "error": "rate_limit_exceeded",
  "message": "Multiple rate limits exceeded",
  "limits_exceeded": [
    {
      "window": "60 seconds",
      "limit": 100,
      "current": 101,
      "retry_after_seconds": 30
    },
    {
      "window": "3600 seconds",
      "limit": 1000,
      "current": 1001,
      "retry_after_seconds": 1800
    }
  ],
  "retry_after_seconds": 1800
}
```

---

**End of Specification**
