# Testing Strategy & Tooling Compatibility

**Feature**: 010-api-versioning-strategy  
**Purpose**: Comprehensive testing approach and tooling validation specifications

---

## 1. Testing Pyramid

### 1.1 Unit Tests (70% coverage target)
**Scope**: Individual middleware functions, version lookup logic, validation rules

**Key Areas**:
- Version parsing and validation
- Status determination logic
- Header injection/extraction
- Cache lookup operations
- Error response formatting
- Rate limiting calculation

**Tools**:
- Python: pytest with pytest-cov
- Node.js: Jest with coverage reporters
- Target: >90% code coverage for core logic

**Example Test Cases**:
```python
def test_version_parsing_valid():
    assert parse_version("v2") == Version(major=2, suffix=None)
    assert parse_version("v3-beta") == Version(major=3, suffix="beta")

def test_version_parsing_invalid():
    with pytest.raises(ValidationError):
        parse_version("invalid")
    with pytest.raises(ValidationError):
        parse_version("V1")  # case sensitive
```

### 1.2 Integration Tests (20% coverage target)
**Scope**: End-to-end request flows, middleware chain, database interactions

**Key Areas**:
- Full request → response cycle
- Version resolution from multiple sources (header, path, query)
- Deprecation header injection
- Authentication + version routing
- Registry reload without downtime

**Tools**:
- Python: pytest with requests library
- Node.js: Supertest or Playwright
- Test containers for dependencies

**Example Test Cases**:
```python
def test_version_header_precedence(client):
    response = client.get(
        "/api/v1/users",
        headers={"X-API-Version": "v2"}  # Override path version
    )
    assert response.headers["X-API-Version"] == "v2"
    assert "routed to v2 handler" in logs

def test_deprecated_version_headers(client):
    response = client.get("/api/v1/users")
    assert "Deprecation" in response.headers
    assert "Sunset" in response.headers
    assert "Link" in response.headers
```

### 1.3 Contract Tests (5% coverage target)
**Scope**: API contract validation against OpenAPI specification

**Tools**:
- Schemathesis: Property-based API testing
- Dredd: OpenAPI contract testing
- Prism: Mock server validation

**Example**:
```bash
schemathesis run --checks all \
  contracts/api-versioning.openapi.yaml \
  http://localhost:8000
```

**Validation**:
- All responses match schema
- Required headers present
- Error codes documented
- Examples are valid

### 1.4 Performance Tests (5% coverage target)
**Scope**: Latency, throughput, resource utilization under load

**Tools**:
- k6: Load testing with JavaScript DSL
- Locust: Python-based load testing
- Artillery: Quick load tests

**Scenarios**:
1. **Baseline**: 100 req/s, steady state
2. **Spike**: 0 → 10,000 req/s in 10 seconds
3. **Sustained**: 5,000 req/s for 10 minutes
4. **Burst**: Alternating 100 ↔ 5,000 req/s

**Metrics**:
- p50, p95, p99 latency <5ms, <10ms, <20ms
- Error rate <0.1%
- CPU <5%, Memory <150KB per request

---

## 2. Load Testing Specifications

### 2.1 Throughput Test
**Objective**: Verify 1000+ req/s handling

**Setup**:
- Target: 1000 authenticated requests/minute = ~17 req/s
- Ramp-up: 0 → 1000 req/min over 60 seconds
- Sustained: 1000 req/min for 5 minutes
- Cooldown: 60 seconds

**Acceptance**:
- All requests complete successfully
- p99 latency <20ms
- No memory leaks (steady state after 2 minutes)

**k6 Script**:
```javascript
export const options = {
  stages: [
    { duration: '1m', target: 1000 },
    { duration: '5m', target: 1000 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(99)<20'],
    http_req_failed: ['rate<0.001'],
  },
};

export default function () {
  const response = http.get('http://localhost:8000/versions', {
    headers: { 'X-API-Key': __ENV.API_KEY },
  });
  check(response, {
    'status is 200': (r) => r.status === 200,
    'has rate limit headers': (r) => r.headers['X-RateLimit-Limit'],
  });
}
```

### 2.2 Spike Test
**Objective**: Validate auto-scaling and burst capacity

**Setup**:
- Baseline: 100 req/s
- Spike: 10,000 req/s for 30 seconds
- Return: 100 req/s

**Acceptance**:
- No 500 errors during spike
- p99 latency <50ms during spike
- Recovery to baseline latency within 60s

### 2.3 Stress Test
**Objective**: Identify breaking point

**Setup**:
- Ramp to 50,000 req/s
- Increase by 5,000 req/s every 2 minutes
- Monitor until first failure

**Success Metrics**:
- Document maximum sustained throughput
- Graceful degradation (503 responses, not crashes)
- Recovery when load decreases

---

## 3. Security Testing

### 3.1 Input Validation Tests
**Tool**: Burp Suite, OWASP ZAP

**Test Cases**:
- SQL injection via version parameter
- YAML injection in configuration
- Path traversal: `../../etc/passwd` as version
- Header injection: `v1\r\nX-Injected: evil`
- XSS in error messages

**Acceptance**: All attacks blocked, 400/401 response

### 3.2 Authentication Tests
**Test Cases**:
- Missing API key → anonymous access (100 req/min limit)
- Invalid API key → 401 Unauthorized
- Expired OAuth token → 401 with WWW-Authenticate
- Rate limit enforcement per key
- Prerelease access without opt-in → 404

### 3.3 Rate Limiting Tests
**Tool**: Custom scripts with concurrent requests

**Scenarios**:
- Authenticated: 1001st request in 1 minute → 429
- Anonymous: 101st request in 1 minute → 429
- Retry-After header present
- Rate limit reset after window

### 3.4 Penetration Testing
**Scope**: External security audit

**Focus Areas**:
- Authentication bypass attempts
- Privilege escalation
- Data exposure via timing attacks
- DDoS resilience

---

## 4. Tooling Compatibility

### 4.1 OpenAPI Validators

#### Spectral (Linter)
**Version**: >=6.0.0  
**Purpose**: Enforce OpenAPI best practices

```bash
spectral lint contracts/api-versioning.openapi.yaml \
  --ruleset .spectral.yaml
```

**Custom Rules**:
- All operations have operationId
- All responses have examples
- Security schemes defined
- Error responses documented

**Acceptance**: Zero errors, <5 warnings

#### Swagger Editor
**Version**: Latest  
**Purpose**: Visual contract editing and validation

**Validation**:
- Import contract without errors
- Generate client code (TypeScript, Python, Go)
- Mock server startup succeeds

#### Redoc
**Version**: >=2.0.0  
**Purpose**: API documentation generation

```bash
redoc-cli bundle contracts/api-versioning.openapi.yaml \
  -o docs/api-reference.html
```

**Acceptance**: Clean HTML output, all examples render

### 4.2 HTTP Client Libraries

#### cURL
**Test Command**:
```bash
curl -H "X-API-Key: test-key" \
  -H "X-API-Version: v2" \
  http://localhost:8000/versions
```

**Validation**:
- Response status 200
- Headers parsed correctly
- JSON body valid

#### Python `requests`
```python
import requests

response = requests.get(
    "http://localhost:8000/versions/v2",
    headers={"X-API-Key": "test-key"}
)
assert response.status_code == 200
assert "X-RateLimit-Limit" in response.headers
```

#### Node.js `axios`
```javascript
const axios = require('axios');

const response = await axios.get('http://localhost:8000/versions', {
  headers: { 'X-API-Key': 'test-key' }
});
console.assert(response.status === 200);
console.assert(response.headers['x-ratelimit-limit']);
```

#### Postman
**Collection**: `api-versioning.postman_collection.json`

**Tests**:
- Environment variables for API_KEY
- Pre-request scripts for authentication
- Test assertions on all responses
- Collection runner passes 100%

### 4.3 Code Generation Tools

#### OpenAPI Generator
**Supported Languages**: Python, TypeScript, Go, Java, Ruby

```bash
openapi-generator-cli generate \
  -i contracts/api-versioning.openapi.yaml \
  -g python \
  -o clients/python
```

**Validation**:
- Generated code compiles without errors
- Type hints correct (Python)
- All endpoints accessible
- Authentication helpers work

#### Swagger Codegen
**Legacy support**: Version 2.x for Java 8 clients

**Validation**: Same as OpenAPI Generator

### 4.4 Mock Servers

#### Prism
**Purpose**: Contract-first development with mock API

```bash
prism mock contracts/api-versioning.openapi.yaml \
  --port 4010
```

**Validation**:
- Allendpoints respond with example data
- Error responses match schema
- Dynamic response based on request

#### Mockoon
**Purpose**: GUI-based mock server for testing

**Validation**:
- Import OpenAPI contract
- Customize responses for test scenarios
- Export environment for CI

### 4.5 API Gateways

#### Kong
**Plugin**: `request-transformer` for version header injection

**Configuration**:
```yaml
plugins:
  - name: request-transformer
    config:
      add:
        headers:
          - X-API-Version:v2
```

**Validation**:
- Version routing works
- Rate limiting enforced
- Authentication integrated

#### AWS API Gateway
**Integration**: Lambda proxy integration

**Validation**:
- OpenAPI import succeeds
- Stages map to versions
- Usage plans enforce rate limits

#### nginx
**Module**: `ngx_http_headers_module`

**Configuration**:
```nginx
location /api/v2/ {
    proxy_set_header X-API-Version v2;
    proxy_pass http://backend;
}
```

**Validation**: Version header injection works

### 4.6 Monitoring & Observability

#### Prometheus
**Metrics Exposed**:
- `api_requests_total{version, status}`
- `api_request_duration_seconds{version}`
- `api_version_usage{version}`

**Validation**: Scrape endpoint returns valid metrics

#### Grafana
**Dashboards**:
- Version adoption over time
- Deprecation countdown
- Error rates by version

**Validation**: Import dashboard JSON succeeds

#### Jaeger/Zipkin
**Tracing**: Distributed tracing for version resolution

**Validation**:
- Spans created for version lookup
- Trace ID propagation works
- Service map shows dependencies

### 4.7 CI/CD Integration

#### GitHub Actions
**Workflow**: `.github/workflows/api-validation.yml`

```yaml
name: API Contract Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate OpenAPI
        run: |
          npx @stoplight/spectral-cli lint \
            contracts/api-versioning.openapi.yaml
```

**Validation**: Workflow passes on main branch

#### Jenkins
**Pipeline**: Declarative pipeline with API testing stage

**Validation**: Integration tests run on PRs

#### GitLab CI
**Stage**: `api-test` with contract validation

**Validation**: Pipeline succeeds

---

## 5. Benchmark Requirements

### 5.1 Version Lookup Benchmarks
**Target**: O(1) hash map lookup

```python
@pytest.mark.benchmark
def test_version_lookup_performance(benchmark):
    registry = VersionRegistry(load_from_config())
    result = benchmark(registry.get_version, "v2")
    assert result is not None
    # Target: <1ms per lookup
```

**Acceptance**: <1ms p99 for in-memory lookup

### 5.2 Middleware Overhead
**Measurement**: Latency with vs. without versioning middleware

**Target**: <2ms overhead for version resolution

**Benchmark**:
```bash
# Without middleware
ab -n 10000 -c 100 http://localhost:8000/api/users

# With middleware
ab -n 10000 -c 100 -H "X-API-Version: v2" http://localhost:8000/api/users
```

**Acceptance**: Overhead <10% of total request time

### 5.3 Configuration Reload Performance
**Measurement**: Time to hot-reload version registry

**Target**: <100ms for 20 versions

**Test**:
```python
def test_config_reload_performance():
    registry = VersionRegistry()
    start = time.time()
    registry.reload_from_file("versions.yaml")
    duration = time.time() - start
    assert duration < 0.1  # 100ms
```

---

## 6. Testing Environment Setup

### 6.1 Local Development
**Tools**: Docker Compose with all dependencies

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
      - RATE_LIMIT_ENABLED=true
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### 6.2 CI Environment
**Runners**: GitHub Actions hosted runners

**Requirements**:
- Python 3.11+
- Node.js 20 LTS
- Docker for integration tests
- 4 GB RAM minimum

### 6.3 Staging Environment
**Purpose**: Pre-production validation

**Configuration**:
- Real authentication (test keys)
- Production-like load (10% of prod traffic)
- Monitoring enabled
- Weekly load tests

---

## 7. Acceptance Criteria

### API Contract
- [ ] OpenAPI 3.1 spec validates with Spectral
- [ ] Client code generation succeeds (Python, TypeScript, Go)
- [ ] Prism mock server starts without errors
- [ ] All examples are syntactically valid

### Performance
- [ ] Throughput test: 1000 req/min sustained
- [ ] Latency test: p99 <20ms under load
- [ ] Stress test: Graceful degradation at limits
- [ ] Memory: No leaks detected after 10-minute test

### Security
- [ ] OWASP ZAP scan: Zero high/critical findings
- [ ] Penetration test: No exploitable vulnerabilities
- [ ] Rate limiting: Enforced within 1% accuracy
- [ ] Input validation: All injection attacks blocked

### Tooling
- [ ] Postman collection: 100% tests pass
- [ ] OpenAPI Generator: Clients compile error-free
- [ ] Kong gateway: Version routing works
- [ ] Prometheus: Metrics scraped successfully

### Testing Coverage
- [ ] Unit tests: >90% code coverage
- [ ] Integration tests: All critical paths covered
- [ ] Contract tests: 100% endpoint coverage
- [ ] Load tests: All scenarios pass

---

## 8. Test Data

### Version Registry Fixture
```yaml
versions:
  - version_id: v1
    status: deprecated
    released_at: '2023-01-01T00:00:00Z'
    deprecated_at: '2024-01-01T00:00:00Z'
    sunset_at: '2025-01-01T00:00:00Z'
  
  - version_id: v2
    status: current
    released_at: '2024-01-01T00:00:00Z'
  
  - version_id: v3-beta
    status: prerelease
    released_at: '2024-11-01T00:00:00Z'
    opt_in_required: true

default_version: v2
```

### Test API Keys
```
test-auth-key: Authenticated consumer (1000 req/min)
test-anon-key: Anonymous consumer (100 req/min)
test-invalid-key: Invalid key for 401 testing
```

---

## References

- [OpenAPI Contract](contracts/api-versioning.openapi.yaml)
- [Edge Cases](edge-cases.md)
- [Specification](spec.md)
- [Performance Requirements](spec.md#performance-requirements)
