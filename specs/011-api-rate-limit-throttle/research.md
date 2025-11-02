# Research: API Rate Limiting & Throttling

**Phase**: 0 (Outline & Research)  
**Date**: 2025-11-01  
**Status**: Complete

---

## Research Questions

### 1. Token Bucket Algorithm Implementation

**Question**: What is the optimal token bucket algorithm implementation for distributed rate limiting with Redis?

**Decision**: Use Redis-based token bucket with Lua scripting for atomic operations

**Rationale**:
- **Atomicity**: Lua scripts execute atomically in Redis, preventing race conditions in distributed setup
- **Performance**: Single Redis round-trip for refill + consume operation (vs. multiple GET/SET calls)
- **Accuracy**: Server-side execution eliminates clock skew between API instances
- **Industry Standard**: Used by major platforms (Stripe, GitHub, Cloudflare)

**Alternatives Considered**:
1. **Client-side token bucket with Redis counter**: Rejected due to race conditions (non-atomic read-modify-write)
2. **Redis transactions (MULTI/EXEC)**: Rejected due to complexity and watch/retry logic overhead
3. **Sorted sets (sliding window)**: Rejected as default due to higher memory overhead and complexity; kept as optional algorithm

**Implementation Approach**:
```lua
-- Lua script (pseudocode)
local key = KEYS[1]
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local requested = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

local last_refill = redis.call('HGET', key, 'last_refill')
local tokens = redis.call('HGET', key, 'tokens')

if not last_refill then
  -- Initialize bucket
  redis.call('HSET', key, 'last_refill', now, 'tokens', max_tokens - requested)
  redis.call('EXPIRE', key, 3600)  -- TTL for cleanup
  return {1, max_tokens - requested}  -- allowed, remaining
end

-- Refill tokens based on elapsed time
local elapsed = now - tonumber(last_refill)
local refilled_tokens = math.min(max_tokens, tonumber(tokens) + elapsed * refill_rate)

if refilled_tokens >= requested then
  redis.call('HSET', key, 'last_refill', now, 'tokens', refilled_tokens - requested)
  return {1, refilled_tokens - requested}  -- allowed, remaining
else
  redis.call('HSET', key, 'last_refill', now, 'tokens', refilled_tokens)
  return {0, refilled_tokens}  -- denied, remaining
end
```

**References**:
- [Redis Lua Scripting](https://redis.io/docs/manual/programmability/eval-intro/)
- [Stripe Rate Limiter Design](https://stripe.com/blog/rate-limiters)
- [Token Bucket Algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Token_bucket)

---

### 2. Redis Sentinel High Availability Configuration

**Question**: What is the recommended Redis Sentinel configuration for production rate limiting?

**Decision**: 3-node Sentinel setup (1 master + 2 replicas) with quorum=2

**Rationale**:
- **Automatic Failover**: Sentinel detects master failure and promotes replica without manual intervention
- **Minimal Overhead**: 3-node setup provides HA without excessive operational complexity
- **Quorum Safety**: quorum=2 prevents split-brain (requires majority agreement for failover)
- **Cost-Effective**: Balances reliability with infrastructure cost (vs. 5+ node cluster)

**Alternatives Considered**:
1. **Single Redis instance**: Rejected for production (no HA, single point of failure)
2. **Redis Cluster (6+ nodes)**: Overkill for rate limiting workload; added complexity of sharding not needed unless >100k req/s
3. **5-node Sentinel**: Higher reliability but increased cost; 3-node sufficient for rate limiting use case

**Configuration Details**:
```toml
[rate_limiting.redis]
topology = "sentinel"
url = "redis://localhost:6379/0"  # Initial connection (any Sentinel node)

[rate_limiting.redis.sentinel]
service_name = "mymaster"
sentinels = [
  { host = "sentinel1.example.com", port = 26379 },
  { host = "sentinel2.example.com", port = 26379 },
  { host = "sentinel3.example.com", port = 26379 }
]
quorum = 2
socket_timeout = 5.0
retry_on_timeout = true
```

**Failover Behavior**:
- **Detection Time**: ~30 seconds (configurable via `down-after-milliseconds`)
- **Promotion Time**: ~5 seconds (Sentinel election + SLAVEOF command)
- **Client Reconnection**: Python redis-py automatically reconnects to new master
- **Counter Preservation**: Asynchronous replication ensures counters preserved (potential <1s data loss acceptable for rate limiting)

**References**:
- [Redis Sentinel Documentation](https://redis.io/docs/management/sentinel/)
- [redis-py Sentinel Support](https://redis-py.readthedocs.io/en/stable/sentinel.html)
- [High Availability with Redis Sentinel](https://redis.io/topics/sentinel)

---

### 3. X-Forwarded-For Header Parsing Strategy

**Question**: How should the system extract client IP from X-Forwarded-For headers to prevent spoofing?

**Decision**: Rightmost untrusted IP strategy with configurable trust depth

**Rationale**:
- **Security**: Prevents client-injected fake IPs (client can add arbitrary values to left side)
- **Flexibility**: Configurable trust depth handles multi-tier proxy setups (CDN + load balancer)
- **Standard Practice**: Recommended by OWASP, used by nginx, AWS ALB
- **Validation**: Rejects malformed headers (non-IP values, excessive length)

**Alternatives Considered**:
1. **Trust all IPs in header**: Rejected due to trivial spoofing vulnerability
2. **Trust first IP only**: Rejected; incorrect for multi-proxy setups (gets proxy IP, not client)
3. **Ignore header entirely**: Rejected; breaks rate limiting behind load balancers (all requests appear from LB IP)

**Implementation Algorithm**:
```python
def extract_client_ip(request: Request, trusted_proxy_depth: int = 1) -> str:
    """
    Extract client IP using rightmost untrusted IP strategy.
    
    Examples:
      X-Forwarded-For: "client, proxy1, proxy2, load_balancer"
      trusted_proxy_depth=1 → returns "proxy2" (rightmost untrusted)
      trusted_proxy_depth=2 → returns "proxy1"
    """
    xff_header = request.headers.get("X-Forwarded-For")
    
    if not xff_header:
        # No XFF header, use direct connection IP
        return request.client.host
    
    # Split by comma, strip whitespace
    ips = [ip.strip() for ip in xff_header.split(",")]
    
    # Validate all IPs (reject if any malformed)
    for ip in ips:
        try:
            ipaddress.ip_address(ip)  # Raises ValueError if invalid
        except ValueError:
            # Malformed header, fall back to connection IP
            return request.client.host
    
    # Return rightmost untrusted IP (skip trusted_proxy_depth hops from right)
    if len(ips) > trusted_proxy_depth:
        return ips[-(trusted_proxy_depth + 1)]
    else:
        # Not enough IPs to skip trusted hops, use leftmost (least trusted)
        return ips[0]
```

**Edge Cases**:
- **Empty header**: Fall back to `request.client.host`
- **Single IP**: Use that IP (common for direct connections)
- **Malformed IPs**: Reject entire header, use connection IP
- **IPv6**: Canonical normalization via `ipaddress.ip_address()`

**References**:
- [OWASP: HTTP Headers](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
- [MDN: X-Forwarded-For](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For)
- [AWS ALB Headers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html)

---

### 4. Progressive Penalty Algorithm

**Question**: How should progressive rate limit penalties be implemented for repeat violators?

**Decision**: Sliding window violation tracker with exponential cooldown multipliers

**Rationale**:
- **Fairness**: Single violation doesn't trigger penalty (transient spikes forgiven)
- **Effectiveness**: Exponential backoff discourages persistent abuse (1x → 2x → 4x → 8x)
- **Configurable**: Operators control detection window, threshold, and multipliers
- **Resource Efficient**: Redis ZSET with timestamps, O(log N) operations

**Alternatives Considered**:
1. **Immediate penalty on first violation**: Rejected as too aggressive; punishes legitimate burst traffic
2. **Linear penalty increase**: Rejected as less effective deterrent than exponential
3. **Permanent bans**: Rejected; out of scope (requires manual intervention and appeals process)

**Implementation Approach**:
```python
def check_progressive_penalty(client_id: str, config: ProgressivePenaltyConfig) -> int:
    """
    Check if client is subject to progressive penalty.
    Returns: cooldown multiplier (1 = no penalty, 2 = 2x, 4 = 4x, etc.)
    """
    if not config.enabled:
        return 1  # No penalty
    
    # Redis key: "ratelimit:penalties:{client_id}"
    key = f"ratelimit:penalties:{client_id}"
    now = time.time()
    window_start = now - config.detection_window
    
    # Count violations in detection window
    # ZSET: {violation_timestamp: violation_count}
    redis.zremrangebyscore(key, 0, window_start)  # Remove old violations
    violation_count = redis.zcount(key, window_start, now)
    
    if violation_count < config.violation_threshold:
        return 1  # Below threshold, no penalty
    
    # Apply penalty based on violation count
    # multipliers = [1, 2, 4, 8]
    # violations = 3 → multipliers[0] = 1x (no penalty, at threshold)
    # violations = 4 → multipliers[1] = 2x
    # violations = 5 → multipliers[2] = 4x
    penalty_index = min(violation_count - config.violation_threshold, len(config.penalty_multipliers) - 1)
    return config.penalty_multipliers[penalty_index]

def record_violation(client_id: str, config: ProgressivePenaltyConfig):
    """Record a rate limit violation for progressive penalty tracking."""
    if not config.enabled:
        return
    
    key = f"ratelimit:penalties:{client_id}"
    now = time.time()
    
    # Add violation timestamp to ZSET
    redis.zadd(key, {now: now})
    redis.expire(key, config.detection_window)  # TTL for cleanup
```

**Configuration Example**:
```toml
[rate_limiting.progressive_penalties]
enabled = false  # Default disabled
detection_window = 3600  # 1 hour
violation_threshold = 3  # 3 violations before penalties
penalty_multipliers = [1, 2, 4, 8]  # Cooldown multipliers
```

**Example Scenario**:
- Client violates limit 3 times in 1 hour → no penalty (at threshold)
- 4th violation → 2x cooldown (wait 2 minutes instead of 1 minute)
- 5th violation → 4x cooldown (wait 4 minutes)
- 6th+ violations → 8x cooldown (wait 8 minutes)

**References**:
- [Exponential Backoff Strategy](https://en.wikipedia.org/wiki/Exponential_backoff)
- [Redis Sorted Sets](https://redis.io/docs/data-types/sorted-sets/)

---

### 5. FastAPI Middleware Integration Pattern

**Question**: What is the best pattern for integrating rate limiting as FastAPI middleware?

**Decision**: Starlette-based middleware with dependency injection for configuration

**Rationale**:
- **Non-Invasive**: Middleware applies to all routes without modifying individual endpoints
- **Order Control**: Middleware stack order determines execution (place after authentication, before business logic)
- **Testability**: Can test middleware independently with `TestClient`
- **Dependency Injection**: FastAPI's DI system provides Redis connection and config to middleware

**Alternatives Considered**:
1. **Decorator-based (@ratelimit)**: Rejected; requires decorating every endpoint (high maintenance)
2. **Route dependencies**: Rejected; must be added to each route definition (not global)
3. **ASGI middleware**: Considered but Starlette middleware simpler and sufficient

**Implementation Pattern**:
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_backend, config):
        super().__init__(app)
        self.redis = redis_backend
        self.config = config
    
    async def dispatch(self, request: Request, call_next):
        # 1. Extract client identifier
        client_id = extract_client_id(request, self.config.trusted_proxy_depth)
        endpoint = request.url.path
        
        # 2. Get applicable rate limit
        limit_config = self.config.get_limit(endpoint, client_id)
        
        # 3. Check rate limit
        allowed, remaining, reset_at = await self.redis.check_limit(
            client_id, endpoint, limit_config
        )
        
        # 4. Handle rejection
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit of {limit_config.limit} requests per {limit_config.window} seconds exceeded",
                    "retry_after_seconds": int(reset_at - time.time())
                },
                headers={
                    "X-RateLimit-Limit": str(limit_config.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_at)),
                    "Retry-After": str(int(reset_at - time.time()))
                }
            )
        
        # 5. Process request
        response = await call_next(request)
        
        # 6. Add headers
        response.headers["X-RateLimit-Limit"] = str(limit_config.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_at))
        
        return response

# Application setup
app = FastAPI()

redis_backend = RedisBackend(config.redis_url)
rate_limit_config = RateLimitConfig.from_toml("config.toml")

app.add_middleware(
    RateLimitMiddleware,
    redis_backend=redis_backend,
    config=rate_limit_config
)
```

**Middleware Order**:
```python
# Correct order (inside → outside):
app.add_middleware(CORSMiddleware)           # 4. CORS (outermost)
app.add_middleware(LoggingMiddleware)        # 3. Logging
app.add_middleware(RateLimitMiddleware)      # 2. Rate limiting (after auth)
app.add_middleware(AuthenticationMiddleware) # 1. Authentication (innermost, runs first)
```

**References**:
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Starlette Middleware](https://www.starlette.io/middleware/)

---

### 6. Prometheus Metrics Best Practices

**Question**: What Prometheus metrics should be exported for rate limiting observability?

**Decision**: 5 core metrics (counters, gauges, histograms) with cardinality-conscious labels

**Rationale**:
- **Completeness**: Covers request volume, rejections, current usage, and backend latency
- **Cardinality Control**: Avoids label explosion (no client_id in labels except gauge)
- **Alerting-Friendly**: Counter metrics enable rate-based alerts (e.g., >10% rejection rate)
- **Troubleshooting**: Histogram enables latency percentile analysis (P50, P95, P99)

**Metrics Specification**:
```python
from prometheus_client import Counter, Gauge, Histogram

# 1. Total requests processed (segmented by endpoint, tier, status)
rate_limit_requests_total = Counter(
    "rate_limit_requests_total",
    "Total requests processed by rate limiter",
    labelnames=["endpoint", "tier", "status"]  # status: allowed | denied
)

# 2. Rate limit rejections (segmented by endpoint, tier, client type)
rate_limit_exceeded_total = Counter(
    "rate_limit_exceeded_total",
    "Total requests rejected due to rate limit exceeded",
    labelnames=["endpoint", "tier", "client_type"]  # client_type: ip | user | tier
)

# 3. Current usage per client (gauge, high cardinality - use sparingly)
rate_limit_current_usage = Gauge(
    "rate_limit_current_usage",
    "Current rate limit usage for a client",
    labelnames=["endpoint", "tier", "client_id"]  # WARNING: High cardinality
)

# 4. Redis operation latency (histogram for percentiles)
rate_limit_redis_latency_seconds = Histogram(
    "rate_limit_redis_latency_seconds",
    "Redis operation latency in seconds",
    labelnames=["operation"],  # operation: check_limit | record_violation
    buckets=[0.001, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250, 0.500, 1.0]
)

# 5. Redis errors (counter for alerting)
rate_limit_redis_errors_total = Counter(
    "rate_limit_redis_errors_total",
    "Total Redis errors encountered",
    labelnames=["operation", "error_type"]  # error_type: timeout | connection_error | ...
)
```

**Cardinality Analysis**:
- `endpoint`: ~10-20 values (acceptable)
- `tier`: ~3-5 values (anonymous, standard, premium)
- `status`: 2 values (allowed, denied)
- `client_type`: 3 values (ip, user, tier)
- `operation`: ~5 values (check_limit, record_violation, etc.)
- `error_type`: ~10 values (timeout, connection_error, etc.)
- **Total cardinality (excluding gauge)**: ~10k time series (acceptable)

**Gauge Cardinality Warning**:
- `client_id`: Potentially 1000+ values (high cardinality)
- **Mitigation**: Only track top N clients (e.g., top 100 by usage) or sample (1% of clients)
- **Alternative**: Use logging for per-client troubleshooting instead of metrics

**Example PromQL Queries**:
```promql
# Rate limit rejection rate (last 5 minutes)
rate(rate_limit_exceeded_total[5m]) / rate(rate_limit_requests_total[5m])

# P95 Redis latency
histogram_quantile(0.95, rate(rate_limit_redis_latency_seconds_bucket[5m]))

# Top endpoints by rejection count
topk(10, sum by (endpoint) (rate_limit_exceeded_total))
```

**References**:
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Cardinality is Key](https://www.robustperception.io/cardinality-is-key)

---

### 7. Testing Strategy for Distributed Systems

**Question**: How should distributed rate limiting be tested to ensure correctness?

**Decision**: 4-tier testing strategy (unit → integration → load → chaos)

**Rationale**:
- **Unit Tests**: Fast feedback on algorithm correctness (no external dependencies)
- **Integration Tests**: Verify Redis interaction (real Redis via pytest-redis)
- **Load Tests**: Validate performance under concurrent load (Locust framework)
- **Chaos Tests**: Ensure graceful degradation during failures (manual Redis shutdown)

**Test Tier Breakdown**:

**1. Unit Tests (pytest, no external dependencies)**
```python
# tests/rate_limiting/unit/test_token_bucket.py
def test_token_bucket_refill():
    bucket = TokenBucket(max_tokens=100, refill_rate=10)  # 10 tokens/sec
    
    # Initial state
    assert bucket.consume(50) == (True, 50)  # 50 remaining
    
    # Fast forward 2 seconds (refill 20 tokens)
    bucket.advance_time(2.0)
    assert bucket.consume(60) == (True, 10)  # 70 tokens available, consume 60, 10 remaining
    
    # Exceed limit
    assert bucket.consume(20) == (False, 10)  # Only 10 remaining, deny

def test_client_id_extraction_xff():
    # Mock request with X-Forwarded-For
    request = MockRequest(
        headers={"X-Forwarded-For": "client, proxy1, proxy2"},
        client_host="load_balancer"
    )
    
    # Trust depth = 1 (trust load_balancer only)
    assert extract_client_ip(request, trusted_proxy_depth=1) == "proxy2"
    
    # Trust depth = 2 (trust load_balancer + proxy2)
    assert extract_client_ip(request, trusted_proxy_depth=2) == "proxy1"
```

**2. Integration Tests (pytest + pytest-redis)**
```python
# tests/rate_limiting/integration/test_redis_backend.py
@pytest.mark.asyncio
async def test_redis_backend_atomic_incr(redis_client):
    backend = RedisBackend(redis_client)
    config = LimitConfig(limit=10, window=60)
    
    # 10 concurrent requests (should all succeed atomically)
    tasks = [
        backend.check_limit("client1", "/api/test", config)
        for _ in range(10)
    ]
    results = await asyncio.gather(*tasks)
    
    # All 10 should be allowed
    assert all(allowed for allowed, _, _ in results)
    
    # 11th request should be denied
    allowed, remaining, _ = await backend.check_limit("client1", "/api/test", config)
    assert not allowed
    assert remaining == 0

@pytest.mark.asyncio
async def test_distributed_consistency(redis_client):
    """Test consistency across 3 simulated API instances."""
    backend = RedisBackend(redis_client)
    config = LimitConfig(limit=100, window=60)
    
    # Simulate 3 instances each processing 40 requests (120 total)
    async def instance_requests(instance_id: int, count: int):
        results = []
        for _ in range(count):
            result = await backend.check_limit(f"instance{instance_id}", "client1", "/api/test", config)
            results.append(result[0])  # allowed bool
        return results
    
    instance1 = await instance_requests(1, 40)
    instance2 = await instance_requests(2, 40)
    instance3 = await instance_requests(3, 40)
    
    total_allowed = sum(instance1) + sum(instance2) + sum(instance3)
    
    # Should allow exactly 100 (within ±2 due to timing)
    assert 98 <= total_allowed <= 102
```

**3. Load Tests (Locust framework)**
```python
# tests/rate_limiting/load/test_performance.py
from locust import HttpUser, task, between

class RateLimitUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Random delay between requests
    
    @task
    def get_endpoint(self):
        response = self.client.get("/api/v1/test")
        
        # Verify rate limit headers present
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        
        # Record latency
        if response.elapsed.total_seconds() > 0.010:  # >10ms
            print(f"WARNING: High latency {response.elapsed.total_seconds():.3f}s")

# Run: locust -f test_performance.py --users 100 --spawn-rate 10 --run-time 60s
```

**4. Chaos Tests (pytest + manual Redis shutdown)**
```python
# tests/rate_limiting/chaos/test_redis_failures.py
@pytest.mark.asyncio
async def test_redis_failure_fail_open(redis_client, redis_server):
    backend = RedisBackend(redis_client, failure_mode="fail_open")
    config = LimitConfig(limit=10, window=60)
    
    # Normal operation
    allowed, _, _ = await backend.check_limit("client1", "/api/test", config)
    assert allowed
    
    # Shutdown Redis
    redis_server.stop()
    
    # Should fail open (allow requests)
    allowed, _, _ = await backend.check_limit("client1", "/api/test", config)
    assert allowed  # Fail open = allow when Redis down
    
    # Restart Redis
    redis_server.start()
    
    # Should resume normal operation
    allowed, _, _ = await backend.check_limit("client1", "/api/test", config)
    assert allowed

@pytest.mark.asyncio
async def test_redis_failure_fail_closed(redis_client, redis_server):
    backend = RedisBackend(redis_client, failure_mode="fail_closed")
    config = LimitConfig(limit=10, window=60)
    
    # Shutdown Redis
    redis_server.stop()
    
    # Should fail closed (reject requests)
    allowed, _, _ = await backend.check_limit("client1", "/api/test", config)
    assert not allowed  # Fail closed = reject when Redis down
```

**Test Coverage Targets**:
- Unit tests: ≥95% line coverage (algorithms, config, headers)
- Integration tests: ≥90% line coverage (Redis operations, middleware)
- Load tests: 1000 req/s sustained for 60s, P95 latency <10ms
- Chaos tests: Cover Redis failure modes (connection loss, timeout, Sentinel failover)

**References**:
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [pytest-redis](https://pypi.org/project/pytest-redis/)
- [Locust Documentation](https://docs.locust.io/)

---

## Summary

All research questions resolved. Key decisions:

1. **Algorithm**: Token bucket with Lua scripting for atomicity
2. **Redis Topology**: Sentinel 3-node (1 master + 2 replicas)
3. **IP Extraction**: Rightmost untrusted IP with configurable trust depth
4. **Progressive Penalties**: ZSET-based sliding window with exponential multipliers
5. **Middleware**: Starlette BaseHTTPMiddleware with dependency injection
6. **Metrics**: 5 core metrics with cardinality control
7. **Testing**: 4-tier strategy (unit → integration → load → chaos)

**Next Phase**: Phase 1 - Design & Contracts (data-model.md, contracts/, quickstart.md)
