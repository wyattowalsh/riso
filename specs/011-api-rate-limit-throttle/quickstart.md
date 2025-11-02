# Quickstart: API Rate Limiting & Throttling

**Target Audience**: Developers integrating rate limiting into FastAPI applications  
**Time to Complete**: ~15 minutes  
**Prerequisites**: Python 3.11+, Redis 6.0+, FastAPI ≥0.104.0

---

## Installation

### 1. Install Dependencies

```bash
# Using uv (recommended for Riso template projects)
uv add fastapi redis pydantic

# Or using pip
pip install fastapi[all] redis pydantic
```

### 2. Start Redis (Local Development)

**Option A: Docker** (recommended)
```bash
docker run -d --name redis-ratelimit \
  -p 6379:6379 \
  redis:7-alpine
```

**Option B: Docker Compose** (for full stack)
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

```bash
docker-compose up -d
```

---

## Basic Usage

### 1. Create Configuration File

Create `config.toml` in your project root:

```toml
[rate_limiting]
enabled = true
default_limit = 100
default_window = 60  # seconds
algorithm = "token_bucket"
failure_mode = "fail_open"  # Allow requests if Redis down

[rate_limiting.client_identification]
trusted_proxy_depth = 1  # Single load balancer

[rate_limiting.redis]
url = "redis://localhost:6379/0"
topology = "single"  # Use "sentinel" for production
pool_size = 20
socket_timeout = 5.0
```

### 2. Initialize FastAPI Application with Rate Limiting

Create `main.py`:

```python
from fastapi import FastAPI
from rate_limiting import RateLimitMiddleware, RateLimitConfig, RedisBackend

# Load configuration
config = RateLimitConfig.from_toml("config.toml")

# Initialize Redis backend
redis_backend = RedisBackend(config.redis_url, config)

# Create FastAPI app
app = FastAPI(title="Rate Limited API")

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    redis_backend=redis_backend,
    config=config
)

# Example endpoint
@app.get("/api/v1/hello")
async def hello():
    return {"message": "Hello, world!"}

# Run with: uvicorn main:app --reload
```

### 3. Test Rate Limiting

```bash
# Start the application
uvicorn main:app --reload

# In another terminal, test rate limiting
for i in {1..105}; do
  curl -i http://localhost:8000/api/v1/hello
done
```

**Expected Behavior**:
- Requests 1-100: Return HTTP 200 with decreasing `X-RateLimit-Remaining` header
- Requests 101+: Return HTTP 429 with `Retry-After` header

**Example Response (Request #50)**:
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 50
X-RateLimit-Reset: 1698765492

{"message": "Hello, world!"}
```

**Example Response (Request #101)**:
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1698765492
Retry-After: 30

{
  "error": "rate_limit_exceeded",
  "message": "Rate limit of 100 requests per 60 seconds exceeded for endpoint /api/v1/hello",
  "retry_after_seconds": 30,
  "limit": 100,
  "window_seconds": 60
}
```

---

## Advanced Configuration

### Per-Endpoint Rate Limits

Add endpoint-specific limits to `config.toml`:

```toml
[[rate_limiting.endpoints]]
pattern = "/api/v1/search"
limit = 20
window = 60

[[rate_limiting.endpoints]]
pattern = "/api/v1/compute"
limit = 5
window = 60

[[rate_limiting.endpoints]]
pattern = "/api/v1/admin/*"
limit = 10
window = 60
```

**Behavior**:
- `/api/v1/search`: 20 requests/minute
- `/api/v1/compute`: 5 requests/minute
- `/api/v1/admin/users`, `/api/v1/admin/settings`: 10 requests/minute (wildcard match)
- All other endpoints: 100 requests/minute (default)

### User-Based Rate Limiting (JWT Authentication)

Update `config.toml` to define user tiers:

```toml
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
```

Update `main.py` to extract user from JWT:

```python
from fastapi import FastAPI, Depends, Header
from fastapi.security import HTTPBearer
from rate_limiting import RateLimitMiddleware, RateLimitConfig, RedisBackend
import jwt

config = RateLimitConfig.from_toml("config.toml")
redis_backend = RedisBackend(config.redis_url, config)

app = FastAPI()
app.add_middleware(RateLimitMiddleware, redis_backend=redis_backend, config=config)

security = HTTPBearer()

@app.get("/api/v1/protected")
async def protected_endpoint(authorization: str = Header(None)):
    # Rate limiting middleware automatically extracts user_id and tier from JWT
    # No additional code needed - middleware handles it
    return {"message": "Protected resource"}
```

**JWT Payload Example**:
```json
{
  "user_id": "alice",
  "tier": "premium",
  "exp": 1698765492
}
```

**Behavior**:
- Anonymous requests (no JWT): 100 requests/minute (IP-based)
- Authenticated users (tier=standard): 1000 requests/minute (user-based)
- Premium users (tier=premium): 5000 requests/minute (user-based)

### Exemptions (Testing/Admin Access)

Add exemptions to `config.toml`:

```toml
[[rate_limiting.exemptions]]
type = "ip"
value = "192.168.1.0/24"  # Local network

[[rate_limiting.exemptions]]
type = "user_id"
value = "admin"  # Admin user
```

**Behavior**: Exempted IPs and user IDs bypass rate limiting entirely.

### Progressive Penalties (Repeat Violators)

Enable progressive penalties in `config.toml`:

```toml
[rate_limiting.progressive_penalties]
enabled = true
detection_window = 3600  # 1 hour
violation_threshold = 3  # 3 violations before penalties
penalty_multipliers = [1, 2, 4, 8]  # Cooldown multipliers
```

**Behavior**:
- First 3 violations in 1 hour: Normal cooldown (1x)
- 4th violation: 2x cooldown (wait 2 minutes instead of 1 minute)
- 5th violation: 4x cooldown (wait 4 minutes)
- 6th+ violations: 8x cooldown (wait 8 minutes)

---

## Production Deployment

### Redis Sentinel (High Availability)

Update `config.toml` for production:

```toml
[rate_limiting.redis]
url = "redis://sentinel1.example.com:26379/0"
topology = "sentinel"
pool_size = 20
socket_timeout = 5.0
circuit_breaker_threshold = 3
circuit_breaker_timeout = 30

[rate_limiting.redis.sentinel]
service_name = "mymaster"
sentinels = [
  { host = "sentinel1.example.com", port = 26379 },
  { host = "sentinel2.example.com", port = 26379 },
  { host = "sentinel3.example.com", port = 26379 }
]
```

**Docker Compose Example** (3-node Sentinel):

```yaml
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data

  redis-replica1:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379 --appendonly yes

  redis-replica2:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379 --appendonly yes

  sentinel1:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf

  sentinel2:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf

  sentinel3:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./sentinel.conf:/etc/redis/sentinel.conf

volumes:
  redis-data:
```

**sentinel.conf**:
```
sentinel monitor mymaster redis-master 6379 2
sentinel down-after-milliseconds mymaster 30000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1
```

### Environment Variable Overrides

Override config values via environment variables:

```bash
export RATE_LIMIT_DEFAULT=200
export REDIS_URL="redis://redis-sentinel:26379/0"
export RATE_LIMIT_FAILURE_MODE="fail_closed"

uvicorn main:app --host 0.0.0.0 --port 8000
```

**Priority**: Environment variables > TOML config > Defaults

---

## Monitoring & Observability

### Prometheus Metrics

Add Prometheus exporter to `main.py`:

```python
from prometheus_client import make_asgi_app

app = FastAPI()

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, redis_backend=redis_backend, config=config)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Available Metrics**:
- `rate_limit_requests_total` - Total requests by endpoint/tier/status
- `rate_limit_exceeded_total` - Total rejections by endpoint/tier
- `rate_limit_redis_latency_seconds` - Redis operation latency histogram
- `rate_limit_redis_errors_total` - Redis errors by operation/type

**Example Prometheus Queries**:
```promql
# Rejection rate (last 5 minutes)
rate(rate_limit_exceeded_total[5m]) / rate(rate_limit_requests_total[5m])

# P95 Redis latency
histogram_quantile(0.95, rate(rate_limit_redis_latency_seconds_bucket[5m]))

# Top rate-limited endpoints
topk(10, sum by (endpoint) (rate_limit_exceeded_total))
```

### Structured Logging

Enable structured logging in `main.py`:

```python
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Rate limiting middleware automatically logs to configured logger
# No additional configuration needed
```

**Example Log Output** (429 response):
```json
{
  "timestamp": "2025-11-01T12:34:56.789Z",
  "level": "INFO",
  "event": "rate_limit_exceeded",
  "client_id": "ip:192.0.2.1",
  "endpoint": "/api/v1/search",
  "limit": 20,
  "window": 60,
  "current_count": 21,
  "tier": "anonymous"
}
```

---

## Troubleshooting

### Issue: Rate limiting not working (all requests allowed)

**Check**:
1. Verify Redis connection: `redis-cli ping` → `PONG`
2. Check `config.toml`: `enabled = true`
3. Verify middleware order (rate limit should be after authentication)
4. Check Redis keys: `redis-cli KEYS "ratelimit:*"`

### Issue: High latency (>10ms per request)

**Check**:
1. Redis latency: `redis-cli --latency`
2. Network latency: Ensure Redis in same datacenter/region
3. Redis connection pool size: Increase `pool_size` if exhausted
4. Use Redis read replicas for distributed deployments

### Issue: Inaccurate rate limits (off by >2%)

**Check**:
1. Clock skew between API instances: Use NTP synchronization
2. Redis replication lag: Check `info replication` on Redis master
3. Connection pool exhaustion: Monitor `rate_limit_redis_errors_total` metric
4. Algorithm choice: Switch to `sliding_window` for stricter enforcement

### Issue: Redis failover causes brief disruption

**Expected behavior**: Sentinel failover takes ~30-60 seconds
- **Mitigation**: Set `failure_mode = "fail_open"` to allow requests during failover
- **Alternative**: Use Redis Cluster for faster failover (<5 seconds)

---

## Next Steps

- **Testing**: See `/specs/011-api-rate-limit-throttle/research.md` for testing strategy (unit, integration, load, chaos)
- **API Contract**: See `/specs/011-api-rate-limit-throttle/contracts/openapi.yml` for full OpenAPI specification
- **Data Model**: See `/specs/011-api-rate-limit-throttle/data-model.md` for Redis key structure and lifecycle
- **Production Checklist**:
  - [ ] Configure Redis Sentinel (3-node minimum)
  - [ ] Set up Prometheus monitoring and alerts
  - [ ] Configure structured logging with log aggregation
  - [ ] Test failover scenarios (chaos engineering)
  - [ ] Document rate limits in API documentation
  - [ ] Implement client retry guidance (exponential backoff + jitter)

---

## Further Reading

- [FastAPI Middleware Documentation](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Redis Sentinel Guide](https://redis.io/docs/management/sentinel/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Rate Limiting Design Patterns (Stripe)](https://stripe.com/blog/rate-limiters)
