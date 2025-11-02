# Tasks: API Rate Limiting & Throttling

**Feature**: 010-api-rate-limit-throttle  
**Input**: Design documents from `/specs/010-api-rate-limit-throttle/`  
**Prerequisites**: spec.md, checklists/requirements.md, depends on 006-fastapi-api-scaffold

**Tests**: Comprehensive tests included (unit, integration, load tests) per FR-010 (?90% line coverage, ?80% branch coverage).

**Organization**: Tasks grouped by functional components to enable independent implementation and testing.

## Format: `- [ ] [ID] [P?] [Component] Description`

- **Checkbox**: All tasks start with `- [ ]` for tracking
- **[ID]**: Sequential task number (T001, T002, etc.)
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Component]**: Which component this task belongs to

## Path Conventions

Template structure (this repository):
- `template/files/python/src/{{ package_name }}/api/rate_limit/` - Rate limiting implementation
- `template/files/python/tests/` - Test templates
- `template/copier.yml` - Template configuration (add rate_limiting_enabled prompt)
- `docs/modules/` - Rate limiting documentation

Generated project structure (after render):
- `{package_name}/api/rate_limit/` - Rate limiting module
- `tests/api/` - Rate limiting tests
- `config.toml` - Rate limit configuration

---

## Phase 1: Core Infrastructure

**Purpose**: Foundation for rate limiting - configuration, Redis backend, algorithms

### Configuration (Pydantic Models)

- [ ] T001 Create template/files/python/src/{{ package_name }}/api/rate_limit/__init__.py.jinja with module exports
- [ ] T002 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/config.py.jinja with RateLimitConfig (default_limit, default_window, algorithm, failure_mode, enabled, progressive_penalties settings)
- [ ] T003 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/config.py.jinja with EndpointConfig (pattern, limit, window) and TierConfig (name, limit, window) models
- [ ] T004 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/config.py.jinja with RedisConfig (url, topology, pool_size, socket_timeout, circuit_breaker settings, sentinel config)
- [ ] T005 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/config.py.jinja with ClientIdentificationConfig (trusted_proxy_depth) model
- [ ] T006 Create template/files/python/src/{{ package_name }}/api/rate_limit/config.py.jinja with ExemptionConfig (type, value) and load_config() function supporting TOML + env var overrides

**Checkpoint**: Configuration models complete with validation

### Redis Backend

- [ ] T007 Create template/files/python/src/{{ package_name }}/api/rate_limit/backends/__init__.py.jinja with backend exports
- [ ] T008 Create template/files/python/src/{{ package_name }}/api/rate_limit/backends/base.py.jinja with abstract RateLimitBackend interface (increment, get_count, reset methods)
- [ ] T009 Create template/files/python/src/{{ package_name }}/api/rate_limit/backends/redis.py.jinja with RedisBackend implementation (connection pooling, circuit breaker, atomic INCR+EXPIRE)
- [ ] T010 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/backends/redis.py.jinja with Redis Sentinel support (service discovery, failover handling)
- [ ] T011 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/backends/memory.py.jinja with in-memory backend for testing (not distributed, single-instance only)
- [ ] T012 Create template/files/python/src/{{ package_name }}/api/rate_limit/backends/redis.py.jinja with graceful failure handling (fail-open/fail-closed based on config)

**Checkpoint**: Redis backend with connection pooling and failure handling complete

### Rate Limiting Algorithms

- [ ] T013 Create template/files/python/src/{{ package_name }}/api/rate_limit/algorithms/__init__.py.jinja with algorithm exports
- [ ] T014 Create template/files/python/src/{{ package_name }}/api/rate_limit/algorithms/base.py.jinja with abstract RateLimiter interface (check_limit, get_remaining, get_reset_time methods)
- [ ] T015 Create template/files/python/src/{{ package_name }}/api/rate_limit/algorithms/token_bucket.py.jinja with TokenBucketLimiter implementation (atomic refill+decrement, burst handling)
- [ ] T016 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/algorithms/sliding_window.py.jinja with SlidingWindowLimiter implementation (Redis ZSET-based, timestamp tracking)
- [ ] T017 Create template/files/python/src/{{ package_name }}/api/rate_limit/algorithms/token_bucket.py.jinja with Lua script for atomic token bucket operations (prevents race conditions)

**Checkpoint**: Both token bucket and sliding window algorithms implemented

---

## Phase 2: Client Identification & Request Processing

**Purpose**: Extract client identity, handle IP spoofing, JWT parsing

### Client Identification

- [ ] T018 Create template/files/python/src/{{ package_name }}/api/rate_limit/identification.py.jinja with get_client_ip() function (X-Forwarded-For parsing, trusted proxy depth, rightmost untrusted IP strategy)
- [ ] T019 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/identification.py.jinja with normalize_ip() for IPv4/IPv6 canonical form (prevents duplicate counters)
- [ ] T020 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/identification.py.jinja with extract_user_from_jwt() function (parse JWT, extract user_id and tier claims, handle missing/invalid tokens)
- [ ] T021 Create template/files/python/src/{{ package_name }}/api/rate_limit/identification.py.jinja with ClientIdentity dataclass (client_id, client_type: ip|user, tier, metadata)

**Checkpoint**: Client identification with IP and JWT support complete

### Endpoint Matching

- [ ] T022 Create template/files/python/src/{{ package_name }}/api/rate_limit/matcher.py.jinja with EndpointMatcher class (pattern matching with wildcards, priority ordering, caching)
- [ ] T023 Create template/files/python/src/{{ package_name }}/api/rate_limit/matcher.py.jinja with get_applicable_limit() function (match endpoint pattern, get tier config, return merged limit config)

**Checkpoint**: Endpoint pattern matching with wildcard support complete

---

## Phase 3: FastAPI Integration

**Purpose**: Middleware, headers, error responses, exemptions

### Middleware

- [ ] T024 Create template/files/python/src/{{ package_name }}/api/rate_limit/middleware.py.jinja with RateLimitMiddleware class (extract identity, check limit, add headers, handle 429)
- [ ] T025 Create template/files/python/src/{{ package_name }}/api/rate_limit/middleware.py.jinja with middleware integration for FastAPI app (app.add_middleware registration)
- [ ] T026 Create template/files/python/src/{{ package_name }}/api/rate_limit/middleware.py.jinja with exemption list checking (bypass rate limiting for exempted IPs/users)
- [ ] T027 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/middleware.py.jinja with health endpoint exemption (/health, /metrics, /docs, /redoc)

### Response Headers

- [ ] T028 Create template/files/python/src/{{ package_name }}/api/rate_limit/headers.py.jinja with add_rate_limit_headers() function (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- [ ] T029 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/headers.py.jinja with calculate_retry_after() function (seconds until limit reset)
- [ ] T030 Create template/files/python/src/{{ package_name }}/api/rate_limit/headers.py.jinja with headers included in all responses (200, 429, 5xx)

### Error Responses

- [ ] T031 Create template/files/python/src/{{ package_name }}/api/rate_limit/exceptions.py.jinja with RateLimitExceeded exception (error code, message, retry_after, limit, window)
- [ ] T032 Create template/files/python/src/{{ package_name }}/api/rate_limit/exceptions.py.jinja with rate_limit_exception_handler() for FastAPI (return 429 with JSON body, Retry-After header)
- [ ] T033 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/exceptions.py.jinja with MultipleWindowsExceeded exception (handle multiple time windows)

**Checkpoint**: FastAPI middleware with headers and error handling complete

---

## Phase 4: Observability & Monitoring

**Purpose**: Metrics, logging, debugging

### Prometheus Metrics

- [ ] T034 Create template/files/python/src/{{ package_name }}/api/rate_limit/metrics.py.jinja with rate_limit_requests_total counter (endpoint, tier, status labels)
- [ ] T035 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/metrics.py.jinja with rate_limit_exceeded_total counter (endpoint, tier, client_type labels)
- [ ] T036 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/metrics.py.jinja with rate_limit_current_usage gauge (endpoint, tier, client_id labels - handle cardinality)
- [ ] T037 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/metrics.py.jinja with rate_limit_redis_latency_seconds histogram (operation label)
- [ ] T038 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/metrics.py.jinja with rate_limit_redis_errors_total counter (operation, error_type labels)
- [ ] T039 Create template/files/python/src/{{ package_name }}/api/rate_limit/metrics.py.jinja with integrate_metrics() function to emit metrics in middleware

### Structured Logging

- [ ] T040 Create template/files/python/src/{{ package_name }}/api/rate_limit/logging.py.jinja with log_rate_limit_event() function (JSON format with timestamp, client_id, endpoint, limit_config, current_count, status)
- [ ] T041 Create template/files/python/src/{{ package_name }}/api/rate_limit/logging.py.jinja with log rate limit violations at INFO level (not ERROR)
- [ ] T042 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/logging.py.jinja with debug logging for rate limit checks (only when debug enabled)

**Checkpoint**: Prometheus metrics and structured logging complete

---

## Phase 5: Advanced Features

**Purpose**: Progressive penalties, multiple windows, hot reload

### Progressive Penalties

- [ ] T043 Create template/files/python/src/{{ package_name }}/api/rate_limit/penalties.py.jinja with ProgressivePenalty class (track violations, calculate penalty multiplier, default disabled)
- [ ] T044 Create template/files/python/src/{{ package_name }}/api/rate_limit/penalties.py.jinja with Redis-backed penalty counter (violation tracking in detection window)
- [ ] T045 Create template/files/python/src/{{ package_name }}/api/rate_limit/penalties.py.jinja with exponential cooldown calculation (1x, 2x, 4x, 8x multipliers)

### Multiple Time Windows

- [ ] T046 Create template/files/python/src/{{ package_name }}/api/rate_limit/windows.py.jinja with MultiWindowChecker class (check multiple windows: 60s, 3600s)
- [ ] T047 Create template/files/python/src/{{ package_name }}/api/rate_limit/windows.py.jinja with shortest Retry-After calculation (return minimum across all exceeded windows)

### Configuration Hot Reload

- [ ] T048 Create template/files/python/src/{{ package_name }}/api/rate_limit/reload.py.jinja with SIGHUP handler for config reload (preserve counters, update limits)
- [ ] T049 [P] Create template/files/python/src/{{ package_name }}/api/rate_limit/reload.py.jinja with admin endpoint for config reload (/admin/rate-limit/reload)

**Checkpoint**: Advanced features (penalties, multiple windows, hot reload) complete

---

## Phase 6: Testing

**Purpose**: Comprehensive test coverage (?90% line, ?80% branch)

### Unit Tests

- [ ] T050 [P] Create template/files/python/tests/api/rate_limit/test_config.py.jinja with config loading tests (TOML, env vars, validation, defaults)
- [ ] T051 [P] Create template/files/python/tests/api/rate_limit/test_token_bucket.py.jinja with token bucket algorithm tests (happy path, burst, refill, edge cases)
- [ ] T052 [P] Create template/files/python/tests/api/rate_limit/test_sliding_window.py.jinja with sliding window algorithm tests (accuracy, timestamp handling, pruning)
- [ ] T053 [P] Create template/files/python/tests/api/rate_limit/test_identification.py.jinja with client identification tests (IPv4, IPv6, X-Forwarded-For, JWT parsing, normalization)
- [ ] T054 [P] Create template/files/python/tests/api/rate_limit/test_matcher.py.jinja with endpoint pattern matching tests (wildcards, priorities, caching)
- [ ] T055 [P] Create template/files/python/tests/api/rate_limit/test_headers.py.jinja with header generation tests (all required headers, Retry-After calculation)
- [ ] T056 [P] Create template/files/python/tests/api/rate_limit/test_penalties.py.jinja with progressive penalty tests (violation tracking, multiplier calculation, disabled by default)

### Integration Tests

- [ ] T057 Create template/files/python/tests/api/rate_limit/test_middleware_integration.py.jinja with FastAPI middleware tests (request flow, headers in response, 429 on limit exceeded)
- [ ] T058 Create template/files/python/tests/api/rate_limit/test_redis_backend.py.jinja with Redis backend tests (connection, atomic operations, failure handling, circuit breaker)
- [ ] T059 [P] Create template/files/python/tests/api/rate_limit/test_sentinel_failover.py.jinja with Redis Sentinel failover tests (requires docker-compose with Sentinel)
- [ ] T060 Create template/files/python/tests/api/rate_limit/test_exemptions.py.jinja with exemption list tests (bypass for exempted IPs/users, health endpoints exempt)

### Load Tests

- [ ] T061 Create template/files/python/tests/api/rate_limit/test_load.py.jinja with concurrent request tests (1000 req/s, 100 clients, accuracy within 2%)
- [ ] T062 Create template/files/python/tests/api/rate_limit/test_distributed.py.jinja with distributed tests (3 FastAPI instances + Redis, verify total count accuracy)

### Edge Case Tests

- [ ] T063 [P] Create template/files/python/tests/api/rate_limit/test_edge_cases.py.jinja with zero-request limits test (maintenance mode)
- [ ] T064 [P] Create template/files/python/tests/api/rate_limit/test_edge_cases.py.jinja with clock skew test (use Redis TIME)
- [ ] T065 [P] Create template/files/python/tests/api/rate_limit/test_edge_cases.py.jinja with burst traffic test (100 requests in 1 second)
- [ ] T066 [P] Create template/files/python/tests/api/rate_limit/test_edge_cases.py.jinja with config change test (reduce limit while active)
- [ ] T067 [P] Create template/files/python/tests/api/rate_limit/test_edge_cases.py.jinja with Redis key expiration race condition test
- [ ] T068 [P] Create template/files/python/tests/api/rate_limit/test_edge_cases.py.jinja with missing JWT claims test (fallback to IP-based)

**Checkpoint**: Comprehensive test suite complete with ?90% coverage

---

## Phase 7: Documentation & Examples

**Purpose**: User documentation, configuration examples, troubleshooting

### Documentation

- [ ] T069 [P] Create docs/modules/rate-limiting.md.jinja with Overview, Quick Start, Configuration, Usage, Algorithms, Best Practices
- [ ] T070 [P] Create docs/modules/rate-limiting.md.jinja with configuration examples (TOML schema, env vars, common patterns)
- [ ] T071 [P] Create docs/modules/rate-limiting.md.jinja with client retry guidance (exponential backoff + jitter example in Python/JS)
- [ ] T072 [P] Create docs/modules/rate-limiting.md.jinja with troubleshooting section (Redis connection, clock skew, high cardinality metrics)
- [ ] T073 [P] Update docs/quickstart.md.jinja to add rate limiting setup steps when rate_limiting_enabled=true

### Context Documentation

- [ ] T074 [P] Create .github/context/rate-limiting-patterns.md with advanced patterns (tier-based limits, progressive penalties, geographic limiting)
- [ ] T075 [P] Update .github/context/fastapi-patterns.md to add rate limiting integration patterns

### Configuration Examples

- [ ] T076 Create template/files/shared/config.toml.example.jinja with rate limiting section when rate_limiting_enabled=true
- [ ] T077 Update template/files/shared/.env.example.jinja to add rate limiting env vars (RATE_LIMIT_DEFAULT, REDIS_URL, etc.)

### Client Examples

- [ ] T078 [P] Create docs/modules/rate-limiting.md.jinja with Python client example (respecting headers, exponential backoff)
- [ ] T079 [P] Create docs/modules/rate-limiting.md.jinja with JavaScript/TypeScript client example (fetch with retry logic)

**Checkpoint**: Comprehensive documentation with examples complete

---

## Phase 8: Template Integration & Configuration

**Purpose**: Integrate rate limiting into Copier template, update dependencies

### Template Configuration

- [ ] T080 Update template/copier.yml to add rate_limiting_enabled prompt (bool, default=false, when api_tracks includes python)
- [ ] T081 Update template/copier.yml to add rate_limit_default_limit prompt (int, default=100, when rate_limiting_enabled=true)
- [ ] T082 Update template/copier.yml to add rate_limit_redis_url prompt (str, default="redis://localhost:6379/0", when rate_limiting_enabled=true)

### Dependencies

- [ ] T083 Update template/files/python/pyproject.toml.jinja to add rate limiting dependencies when rate_limiting_enabled=true (redis>=5.0, prometheus-client>=0.16.0, PyJWT>=2.8.0)
- [ ] T084 Update template/files/python/pyproject.toml.jinja to add rate limiting dev dependencies (fakeredis>=2.20.0 for testing)

### API Integration

- [ ] T085 Update template/files/python/src/{{ package_name }}/api/main.py.jinja to register rate limit middleware when rate_limiting_enabled=true
- [ ] T086 Update template/files/python/src/{{ package_name }}/api/main.py.jinja to register rate limit exception handlers
- [ ] T087 Update template/files/python/src/{{ package_name }}/api/settings.py.jinja to add RateLimitSettings (include config path, Redis URL, default limits)

### Container Support

- [ ] T088 Update template/files/shared/docker-compose.yml.jinja to add Redis service when rate_limiting_enabled=true (redis:7-alpine, ports 6379, healthcheck)
- [ ] T089 Update template/files/shared/docker-compose.yml.jinja to add Redis Sentinel services when rate_limit_topology=sentinel (3 nodes: master + 2 replicas)
- [ ] T090 Update template/files/shared/Dockerfile.jinja to expose Redis connection env vars when rate_limiting_enabled=true

### Module Tracking

- [ ] T091 Update template/files/shared/module_catalog.json.jinja to add rate limiting module entry (name, description, dependencies, activation prompt)
- [ ] T092 Update scripts/ci/record_module_success.py to track rate limiting module in samples/metadata/module_success.json

**Checkpoint**: Rate limiting fully integrated into template

---

## Phase 9: Validation & Polish

**Purpose**: End-to-end validation, performance testing, spec compliance

### Sample Projects

- [ ] T093 Create samples/api-rate-limit/copier-answers.yml with rate limiting enabled (rate_limiting_enabled=true, api_tracks=python)
- [ ] T094 Update samples/full-stack/copier-answers.yml to include rate limiting (rate_limiting_enabled=true)

### Validation

- [ ] T095 Run scripts/render-samples.sh --variant api-rate-limit to generate sample with rate limiting
- [ ] T096 Validate sample: cd samples/api-rate-limit/render && uv sync && docker-compose up -d redis
- [ ] T097 Test rate limiting: make 101 requests, verify 429 on 101st request, verify headers present
- [ ] T098 Test exemptions: add IP to exemption list, verify bypass
- [ ] T099 Test tier-based limits: create JWT with tier=premium, verify higher limits
- [ ] T100 Test Redis failover: stop Redis, verify fail-open mode allows requests
- [ ] T101 Test configuration reload: update config.toml, send SIGHUP, verify new limits applied
- [ ] T102 Run quality checks: make quality (verify all pass)
- [ ] T103 Run tests with coverage: uv run pytest tests/api/rate_limit/ --cov --cov-report=term-missing (verify ?90% line, ?80% branch)
- [ ] T104 Validate Prometheus metrics: curl http://localhost:8000/metrics | grep rate_limit
- [ ] T105 Validate structured logs: check logs for rate limit events in JSON format

### Performance Testing

- [ ] T106 Benchmark P95 latency: verify <5ms overhead (SC-003)
- [ ] T107 Benchmark P99 latency: verify <10ms overhead (SC-003)
- [ ] T108 Test accuracy: 99% accuracy ?1 request per 100 limit (SC-002)
- [ ] T109 Test distributed accuracy: 98% accuracy with 3 instances (SC-006)
- [ ] T110 Test concurrent handling: 1000 concurrent requests, verify within 2% of limits (SC-005)
- [ ] T111 Verify Redis connection pool: ?10 connections per instance (SC-004)

### Success Criteria Validation

- [ ] T112 Validate SC-001: Configuration in <5 minutes (measure with fresh user)
- [ ] T113 Validate SC-007: 100% of responses include rate limit headers
- [ ] T114 Validate SC-008: Retry-After within ?2 seconds of actual reset
- [ ] T115 Validate SC-009: All user stories have documentation with examples
- [ ] T116 Validate SC-011: Metrics exported within 1 second of events
- [ ] T117 Validate SC-012: 0% rejection in fail-open mode during Redis outage
- [ ] T118 Validate SC-013: 100% of invalid configs rejected with clear error
- [ ] T119 Validate SC-014: Headers parseable by Python requests, JS fetch, curl
- [ ] T120 Validate SC-015: Documentation includes retry algorithm examples

### Spec Compliance

- [ ] T121 Verify FR-001 through FR-020: All functional requirements validated
- [ ] T122 Verify US1: Basic per-client rate limiting (100 req/min IP-based)
- [ ] T123 Verify US2: Per-endpoint rate limiting (different limits per endpoint)
- [ ] T124 Verify US3: Authenticated user rate limiting (JWT-based, tier support)
- [ ] T125 Verify US4: Configuration management (TOML + env vars, hot reload)
- [ ] T126 Verify US5: Distributed rate limiting (Redis-backed, 3+ instances)
- [ ] T127 Verify US6: Monitoring & observability (Prometheus + logs)
- [ ] T128 Verify US7: Response headers (X-RateLimit-*, Retry-After)

**Checkpoint**: All validation complete, feature production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Core Infrastructure)**: No dependencies - can start immediately
- **Phase 2 (Client Identification)**: Depends on Phase 1 (config models)
- **Phase 3 (FastAPI Integration)**: Depends on Phase 1 + Phase 2
- **Phase 4 (Observability)**: Can run in parallel with Phase 3
- **Phase 5 (Advanced Features)**: Depends on Phase 1-3
- **Phase 6 (Testing)**: Depends on Phase 1-5 being complete
- **Phase 7 (Documentation)**: Can run in parallel with Phase 5-6
- **Phase 8 (Template Integration)**: Depends on Phase 1-5 being complete
- **Phase 9 (Validation)**: Depends on all previous phases

### Critical Path

1. Phase 1 (Core Infrastructure) ? BLOCKING all other phases
2. Phase 2 (Client Identification) ? Needed for Phase 3
3. Phase 3 (FastAPI Integration) ? Needed for Phase 6 (testing)
4. Phase 6 (Testing) ? Validates implementation
5. Phase 8 (Template Integration) ? Makes feature usable
6. Phase 9 (Validation) ? Production readiness

### Parallel Opportunities

- Phase 4 (Observability) can run in parallel with Phase 3
- Phase 5 (Advanced Features) subtasks can run in parallel
- Phase 7 (Documentation) can run in parallel with Phase 5-6
- Most tasks within each phase marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (Basic Rate Limiting)

1. Complete Phase 1: Core Infrastructure (T001-T017)
2. Complete Phase 2: Client Identification (T018-T023)
3. Complete Phase 3: FastAPI Integration (T024-T033)
4. **STOP and VALIDATE**:
   - Render sample with rate limiting
   - Make 100 requests ? verify success
   - Make 101st request ? verify 429
   - Verify headers present
5. **MVP COMPLETE**: Working rate limiting with token bucket, IP-based limits

### Incremental Delivery

1. **Foundation** (Phase 1-3) ? Basic rate limiting works (MVP! ??)
2. **+Observability** (Phase 4) ? Metrics and logging
3. **+Advanced Features** (Phase 5) ? Progressive penalties, multiple windows
4. **+Testing** (Phase 6) ? Comprehensive test coverage
5. **+Documentation** (Phase 7) ? User guides and examples
6. **+Integration** (Phase 8) ? Template integration
7. **+Validation** (Phase 9) ? Production-ready feature

---

## Task Summary

- **Total Tasks**: 128
- **Phase 1 (Core Infrastructure)**: 17 tasks
- **Phase 2 (Client Identification)**: 6 tasks
- **Phase 3 (FastAPI Integration)**: 10 tasks
- **Phase 4 (Observability)**: 9 tasks
- **Phase 5 (Advanced Features)**: 7 tasks
- **Phase 6 (Testing)**: 19 tasks
- **Phase 7 (Documentation)**: 11 tasks
- **Phase 8 (Template Integration)**: 13 tasks
- **Phase 9 (Validation)**: 36 tasks

**Parallel Opportunities**: 50+ tasks marked [P] can run in parallel
**MVP Scope**: Phases 1-3 (Tasks T001-T033) = 33 tasks for working rate limiting

---

## Notes

- All tasks follow checklist format: `- [ ] [ID] [P?] [Component] Description with path`
- [P] tasks work on different files with no cross-dependencies
- Rate limiting is optional via `rate_limiting_enabled` prompt in copier.yml
- Template files use .jinja extension for Copier template processing
- Generated code must pass quality checks without modification
- Commit after each logical group of tasks
- Stop at checkpoints to validate component independence
- Follow spec requirements: FR-001 through FR-021, US1 through US7, SC-001 through SC-015
