# Riso Rate Limiting Sample

This sample demonstrates comprehensive API rate limiting with Redis backend.

## Features

- ? **Token Bucket Algorithm**: Allows burst traffic while enforcing average rates
- ? **Redis Backend**: Distributed rate limiting across multiple instances
- ? **IP & JWT Identification**: Support for both anonymous and authenticated rate limiting
- ? **Per-Endpoint Limits**: Different limits for different API endpoints
- ? **Tier-Based Limits**: Anonymous, standard, and premium user tiers
- ? **Prometheus Metrics**: Monitor rate limit violations and Redis performance
- ? **Structured Logging**: JSON logs for rate limit events
- ? **Standard Headers**: X-RateLimit-* headers in all responses

## Quick Start

### 1. Render the Project

```bash
# From riso-template root
./scripts/render-samples.sh --variant api-rate-limit
cd samples/api-rate-limit/render
```

### 2. Start Redis

```bash
docker-compose up -d redis
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Configure Rate Limiting

```bash
cp config.toml.example config.toml
# Edit config.toml to customize rate limits
```

### 5. Start the API

```bash
uv run uvicorn riso_rate_limit_demo.api.main:app --reload
```

### 6. Test Rate Limiting

```bash
# Make requests to see rate limiting in action
for i in {1..105}; do
  curl -i http://localhost:8000/test
  echo "Request $i"
done

# You should see HTTP 429 after 100 requests
```

## Configuration

### Basic Rate Limiting

```toml
# config.toml
[rate_limiting]
enabled = true
default_limit = 100  # requests per window
default_window = 60  # seconds
algorithm = "token_bucket"
```

### Per-Endpoint Limits

```toml
[[rate_limiting.endpoints]]
pattern = "/api/v1/search"
limit = 20
window = 60

[[rate_limiting.endpoints]]
pattern = "/api/v1/admin/*"
limit = 5
window = 60
```

### Tier-Based Limits

```toml
[[rate_limiting.tiers]]
name = "anonymous"
limit = 100
window = 60

[[rate_limiting.tiers]]
name = "premium"
limit = 5000
window = 60
```

## Testing

### Run Unit Tests

```bash
uv run pytest tests/api/rate_limit/ -v
```

### Run Integration Tests (requires Redis)

```bash
docker-compose up -d redis
uv run pytest tests/api/rate_limit/test_redis_backend.py -v
```

### Check Code Coverage

```bash
uv run pytest tests/api/rate_limit/ --cov=riso_rate_limit_demo.api.rate_limit --cov-report=term-missing
```

## Monitoring

### View Prometheus Metrics

```bash
# Metrics are available at /metrics
curl http://localhost:8000/metrics | grep rate_limit
```

Key metrics:
- `rate_limit_requests_total`: Total requests processed
- `rate_limit_exceeded_total`: Total rate limit violations
- `rate_limit_current_usage`: Current usage percentage
- `rate_limit_redis_latency_seconds`: Redis operation latency

### View Structured Logs

Rate limit events are logged in JSON format:

```bash
# Watch logs
tail -f logs/api.log | grep rate_limit
```

## Client Integration

### Python Client with Retry

```python
import time
import requests

def make_request_with_retry(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        response = requests.get(url)
        
        # Check rate limit headers
        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")

# Usage
response = make_request_with_retry("http://localhost:8000/test")
print(response.json())
```

## Production Deployment

### Redis Sentinel Setup

For production, use Redis Sentinel for high availability:

```yaml
# docker-compose.prod.yml
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --port 6379
  
  redis-replica-1:
    image: redis:7-alpine
    command: redis-server --port 6379 --replicaof redis-master 6379
  
  redis-sentinel-1:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
```

Update configuration:

```toml
[rate_limiting.redis]
topology = "sentinel"

[rate_limiting.redis.sentinel]
service_name = "mymaster"

[[rate_limiting.redis.sentinel.sentinels]]
host = "sentinel-1"
port = 26379
```

### Best Practices

1. **Monitor metrics**: Set up Grafana dashboards for rate limit metrics
2. **Alert on high rejection rates**: Configure alerts when rejection rate > 10%
3. **Use fail-open mode**: Graceful degradation when Redis is unavailable
4. **Configure proxy trust depth**: Prevent IP spoofing in production
5. **Review limits periodically**: Adjust based on actual traffic patterns

## Troubleshooting

### Redis Connection Failed

```bash
# Check Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Test Redis connection
redis-cli -h localhost -p 6379 ping
```

### Rate Limiting Not Working

1. Check configuration is loaded: `curl http://localhost:8000/health`
2. Verify Redis connection: `redis-cli ping`
3. Check exemptions: Health endpoints are auto-exempted
4. Review logs: `grep rate_limit logs/api.log`

### High Redis Latency

1. Increase connection pool: Set `pool_size = 50` in config
2. Use Redis in same region/datacenter
3. Switch to token bucket algorithm (lower overhead than sliding window)

## Documentation

- [Rate Limiting Module Documentation](../../docs/modules/rate-limiting.md)
- [Configuration Reference](config.toml.example)
- [API Documentation](http://localhost:8000/docs)

## License

MIT
