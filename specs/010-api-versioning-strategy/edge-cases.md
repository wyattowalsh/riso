# Edge Cases & Error Scenarios

**Feature**: 010-api-versioning-strategy  
**Purpose**: Comprehensive edge case handling and recovery flow specifications

---

## 1. Malformed Version Identifiers

### 1.1 Invalid Format
**Scenario**: Version identifier doesn't match `^v[0-9]+(-[a-z]+)?$` pattern

**Examples**:
- `V1` (uppercase)
- `1.0` (missing 'v' prefix)
- `v1.2` (contains dot)
- `v1_beta` (underscore instead of hyphen)
- `version1` (full word)

**Behavior**:
- HTTP 400 Bad Request
- Error code: `INVALID_VERSION_FORMAT`
- Response includes pattern requirement and examples
- Log at INFO level (not an error)

### 1.2 Leading/Trailing Whitespace
**Scenario**: Version with whitespace (` v1`, `v1 `, ` v1 `)

**Behavior**:
- Automatic trimming applied
- Proceed with trimmed value
- Log warning about whitespace (potential client bug)
- Success response as normal

### 1.3 Case Sensitivity
**Scenario**: Uppercase version (`V1`, `V2-BETA`)

**Behavior**:
- Strict case-sensitive matching
- `V1` ≠ `v1`
- HTTP 404 Not Found
- Error response suggests available versions
- Log at INFO level

### 1.4 Extremely Long Version IDs
**Scenario**: Version exceeds maxLength validation (>20 chars)

**Examples**:
- `v1-beta-experimental-feature-123`
- `v999999999999999999`

**Behavior**:
- HTTP 400 Bad Request
- Error code: `INVALID_VERSION_FORMAT`
- Message: "Version identifier must be 2-20 characters"
- Truncation not performed

### 1.5 Empty Version String
**Scenario**: Empty string provided (`""`, query param `?version=`)

**Behavior**:
- Treated as "no version specified"
- Falls back to default version
- No error (graceful degradation)

---

## 2. Configuration Scenarios

### 2.1 Zero Versions Configured
**Scenario**: Version registry is empty

**Behavior**:
- System initialization fails
- Returns HTTP 503 Service Unavailable
- Error: "Version registry not initialized"
- Health check `/health` returns `unhealthy`
- Prevent deployment with empty registry

**Recovery**:
- Load default configuration
- Require at least one `current` version
- Block API requests until registry populated

### 2.2 Single Version (No Alternatives)
**Scenario**: Only one version exists in registry

**Behavior**:
- Normal operation
- `default_version` = only version
- `available_versions` array has 1 element
- Deprecation endpoints return empty/null
- Migration guide links not applicable

**Acceptance**: Valid state for new APIs

### 2.3 No Current Version
**Scenario**: All versions are deprecated, sunset, or prerelease

**Behavior**:
- System validation fails at startup
- HTTP 503 Service Unavailable
- Error: "No current version available"
- Require exactly one version with `status: current`

### 2.4 Multiple Current Versions
**Scenario**: Registry has >1 version marked `current`

**Behavior**:
- Configuration validation error
- Fails at startup/reload
- Error: "Multiple current versions detected: v2, v3"
- Require explicit `default_version` designation
- Only allow one `current` status

### 2.5 Invalid Sunset Date (Past Date for Current Version)
**Scenario**: Current version has `sunset_at` in the past

**Behavior**:
- Configuration warning (not fatal)
- Version auto-transitions to `sunset` status
- Log ERROR level
- Alert operations team
- Serve version with 410 Gone responses

---

## 3. State Transition Edge Cases

### 3.1 Version Status Change During Active Requests
**Scenario**: Version transitions from `current` → `deprecated` while requests in-flight

**Behavior**:
- **In-flight requests**: Complete with original status
- **New requests**: See new status immediately
- **Headers**: Reflect request-time status
- **Atomic transition**: No partial state visible

**Implementation**: Version registry uses copy-on-write

### 3.2 Deprecation Announcement vs. Sunset
**Scenario**: `deprecated_at` is in future

**Behavior**:
- Status remains `current` until `deprecated_at`
- Scheduled transition at exact timestamp
- Background job checks every 60 seconds
- Precision: ±60 seconds for transition

### 3.3 Sunset Date Reached
**Scenario**: `sunset_at` timestamp reached

**Behavior**:
- Auto-transition to `sunset` status
- All requests return 410 Gone
- Include `Sunset` header (RFC 8594)
- Include `Link` header with successor version
- Log transition event

### 3.4 Prerelease to Current Promotion
**Scenario**: `v3-beta` promoted to `v3` stable

**Behavior**:
- Create new version entry `v3` with `status: current`
- Original `v3-beta` transitions to `deprecated`
- Consumers on `v3-beta` automatically migrate
- `available_versions` includes both temporarily
- Announcement via changelog

---

## 4. Authentication & Authorization Edge Cases

### 4.1 Missing API Key (Anonymous Request)
**Scenario**: No `X-API-Key` header, no OAuth token

**Behavior**:
- Allow request (anonymous access enabled)
- Apply anonymous rate limit (100 req/min)
- `X-RateLimit-Limit: 100`
- Read-only access (GET endpoints only)
- Log consumer as `anonymous`

### 4.2 Invalid API Key
**Scenario**: `X-API-Key` header present but invalid

**Behavior**:
- HTTP 401 Unauthorized
- Error code: `UNAUTHORIZED`
- Message: "Invalid API key"
- Do not hint at valid key format (security)
- Rate limit on invalid attempts: 10/min per IP

### 4.3 Expired OAuth Token
**Scenario**: OAuth token expired

**Behavior**:
- HTTP 401 Unauthorized
- Error code: `UNAUTHORIZED`
- Message: "OAuth token expired"
- Include WWW-Authenticate header
- Suggest token refresh flow

### 4.4 Prerelease Access Without Opt-In
**Scenario**: Request `v3-beta` without `X-API-Prerelease-Opt-In: true`

**Behavior**:
- HTTP 404 Not Found (not 403)
- Error code: `PRERELEASE_OPT_IN_REQUIRED`
- Message: "Version v3-beta requires prerelease opt-in header"
- Include header name in error details
- Do not expose prerelease existence to unauthenticated users

### 4.5 Rate Limit Exceeded
**Scenario**: Consumer exceeds rate limit

**Behavior**:
- HTTP 429 Too Many Requests
- `X-RateLimit-Remaining: 0`
- `Retry-After` header (seconds until reset)
- Error code: `RATE_LIMIT_EXCEEDED`
- Exponential backoff recommended

---

## 5. Registry & Configuration Errors

### 5.1 Configuration File Reload Failure
**Scenario**: Hot-reload of version configuration fails (invalid YAML, parse error)

**Behavior**:
- Continue with previous valid configuration
- Log ERROR with parse failure details
- Alert operations team
- Health check remains `healthy` (degraded mode)
- Expose `/config/status` endpoint showing last valid load time

**Recovery**: Manual intervention required, fix config file

### 5.2 Registry Corruption Detection
**Scenario**: Version registry data structure corrupted (missing required fields)

**Behavior**:
- Detect at access time
- Return HTTP 503 Service Unavailable
- Error: "Version registry corrupted"
- Health check returns `unhealthy`
- Trigger automatic registry rebuild from source

**Recovery**: Load from backup, rebuild from configuration

### 5.3 Version Deployment Rollback
**Scenario**: New version deployed but needs immediate rollback

**Behavior**:
- Remove version from registry
- Update `default_version` to previous stable
- In-flight requests to rolled-back version: complete
- New requests: routed to fallback version
- Log rollback event with reason

### 5.4 Metadata Unavailable (Cache Miss)
**Scenario**: Version metadata not in cache, database unavailable

**Behavior**:
- Graceful degradation mode
- Return minimal metadata (version_id, status only)
- Log WARNING
- `X-Degraded-Mode: metadata-unavailable` header
- Continue serving requests

---

## 6. Concurrent Access Scenarios

### 6.1 Concurrent Version Lookup (High Load)
**Scenario**: 10,000 req/s hitting version discovery

**Behavior**:
- Cache-first architecture
- No database queries for stable versions
- Memory-based lookup (O(1) hash map)
- Target latency maintained: <10ms p99
- Circuit breaker if external dependencies fail

### 6.2 Maximum Concurrent Versions
**Scenario**: System hosting 50+ versions

**Behavior**:
- Soft limit: 20 versions (warning)
- Hard limit: 100 versions (reject new additions)
- Registry size monitoring and alerting
- Performance degradation >20 versions
- Recommendation: sunset old versions aggressively

### 6.3 Version State Transition Under Load
**Scenario**: Version transitioned while 1000 req/s active

**Behavior**:
- Lock-free update (atomic pointer swap)
- No request delays during transition
- In-flight: see pre-transition state
- New requests: see post-transition state
- Transition completes in <100ms

---

## 7. Error Response Edge Cases

### 7.1 Contradictory Version Specifications
**Scenario**: Header=v2, URL path=v1, query param=v3

**Behavior**:
- HTTP 409 Conflict
- Error code: `VERSION_CONFLICT`
- Message: "Contradictory version specifications"
- Details: Lists all sources and values
- Precedence rule documentation included

### 7.2 Sunset Version Request
**Scenario**: Request to version past sunset_at date

**Behavior**:
- HTTP 410 Gone
- Error code: `VERSION_SUNSET`
- Include sunset timestamp
- Include successor version
- `Link` header to migration guide
- `Sunset` header (RFC 8594)

### 7.3 Not-Yet-Released Version
**Scenario**: Request to version with future `released_at`

**Behavior**:
- HTTP 404 Not Found
- Error code: `VERSION_NOT_FOUND`
- Do not expose future release information
- Treat as non-existent version

### 7.4 Internal Server Error (500)
**Scenario**: Unexpected exception during processing

**Behavior**:
- HTTP 500 Internal Server Error
- Error code: `INTERNAL_SERVER_ERROR`
- Generic message (no stack traces)
- Unique correlation_id for tracing
- Log full error with correlation_id
- Alert on-call engineer

### 7.5 Service Degradation (503)
**Scenario**: Dependency failure (database, cache down)

**Behavior**:
- HTTP 503 Service Unavailable
- `Retry-After` header (60 seconds)
- Error: "Version service temporarily unavailable"
- Circuit breaker activated
- Health check returns `unhealthy`

---

## 8. Header Handling Edge Cases

### 8.1 Multiple Version Headers
**Scenario**: Request includes multiple `X-API-Version` headers

**Behavior**:
- Use first occurrence
- Log WARNING about duplicate headers
- Ignore subsequent headers
- Continue processing

### 8.2 Header Injection Attack
**Scenario**: Version header includes newline/CRLF (`v1\r\nX-Injected: evil`)

**Behavior**:
- Sanitize: reject any header with control characters
- HTTP 400 Bad Request
- Error code: `INVALID_VERSION_FORMAT`
- Log as security event
- Rate limit IP address

### 8.3 Excessively Large Headers
**Scenario**: Version header >1KB

**Behavior**:
- Reject at load balancer/proxy level
- HTTP 431 Request Header Fields Too Large
- Never reaches application code

---

## 9. Performance Degradation Scenarios

### 9.1 Cold Start (First Request)
**Scenario**: First request after deployment

**Behavior**:
- Registry pre-loaded during startup
- Cache pre-warmed
- First request latency: <50ms (slightly elevated)
- Subsequent requests: <10ms target

### 9.2 Cache Invalidation Storm
**Scenario**: Massive cache invalidation (configuration reload)

**Behavior**:
- Staggered cache rebuild (100ms window)
- Avoid thundering herd
- Temporary latency spike: <100ms
- Rate limit cache rebuild requests

### 9.3 Memory Pressure
**Scenario**: System under memory pressure (>90% utilization)

**Behavior**:
- Garbage collection may increase latency
- Target: p99 <20ms even under pressure
- Circuit breaker if OOM risk
- Alert operations team at 80% memory

---

## 10. Monitoring & Observability Edge Cases

### 10.1 Missing Correlation ID
**Scenario**: Request without `X-Correlation-ID` header

**Behavior**:
- Generate new UUIDv4
- Include in response headers
- Use for all logging/tracing
- Propagate to downstream services

### 10.2 Distributed Tracing Failure
**Scenario**: Tracing system (Jaeger/Zipkin) unavailable

**Behavior**:
- Continue operation (non-blocking)
- Log locally as fallback
- Metrics still collected
- No user-visible impact

### 10.3 Metrics Collection Failure
**Scenario**: Metrics backend (Prometheus/CloudWatch) down

**Behavior**:
- Buffer metrics in memory (10-minute window)
- Flush when backend recovers
- Overflow: drop oldest metrics
- Alert operations team

---

## Testing Strategy

### Unit Tests
- Each edge case scenario has dedicated test
- Verify exact error codes and messages
- Assert response headers

### Integration Tests
- State transition scenarios
- Concurrent access patterns
- Configuration reload under load

### Chaos Tests
- Registry corruption injection
- Cache failure simulation
- Dependency timeouts

### Load Tests
- 10,000 concurrent requests
- Version transitions under load
- Memory pressure scenarios

---

## Acceptance Criteria

- [ ] All edge cases have defined behavior
- [ ] Error responses include correlation IDs
- [ ] Graceful degradation in failure modes
- [ ] No data loss during state transitions
- [ ] Monitoring captures all error scenarios
- [ ] Documentation covers troubleshooting
- [ ] Load tests validate concurrent behavior
- [ ] Security audit passed for injection prevention

---

## References

- [Specification](spec.md) - Functional requirements
- [Data Model](data-model.md) - Entity definitions
- [API Contract](contracts/api-versioning.openapi.yaml) - Error schemas
- [Tasks](tasks.md) - Implementation checklist
