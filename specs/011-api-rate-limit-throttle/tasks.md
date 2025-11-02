# Tasks: API Rate Limiting & Throttling

**Input**: Design documents from `/specs/011-api-rate-limit-throttle/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Test tasks are included per the feature specification requirement SC-010 (≥90% line coverage, ≥80% branch coverage)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Project Structure**: Single project (Riso template shared module)
- **Module**: `template/files/shared/rate_limiting/`
- **Tests**: `tests/rate_limiting/`
- **Config**: `template/files/shared/config/rate_limiting.toml.jinja`
- **Docs**: `docs/modules/rate-limiting.md.jinja`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and rate limiting module structure

- [ ] T001 Create rate limiting module directory structure per plan.md (template/files/shared/rate_limiting/ with subdirs: limiters/, backends/)
- [ ] T002 [P] Initialize Python package with __init__.py in template/files/shared/rate_limiting/__init__.py
- [ ] T003 [P] Initialize limiters subpackage in template/files/shared/rate_limiting/limiters/__init__.py
- [ ] T004 [P] Initialize backends subpackage in template/files/shared/rate_limiting/backends/__init__.py
- [ ] T005 [P] Create test directory structure (tests/rate_limiting/ with subdirs: unit/, integration/, load/, chaos/)
- [ ] T006 [P] Create TOML config template file in template/files/shared/config/rate_limiting.toml.jinja with schema from research.md
- [ ] T007 [P] Create module documentation file in docs/modules/rate-limiting.md.jinja based on quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration & Data Structures

- [ ] T008 Implement Pydantic configuration models in template/files/shared/rate_limiting/config.py (LimitConfig, EndpointConfig, TierConfig, ProgressivePenaltyConfig, RateLimitConfig per data-model.md)
- [ ] T009 [P] Implement configuration loading from TOML with environment variable overrides in template/files/shared/rate_limiting/config.py
- [ ] T010 [P] Implement custom exceptions in template/files/shared/rate_limiting/exceptions.py (RateLimitExceeded, RedisConnectionError, ConfigurationError)

### Backend Infrastructure

- [ ] T011 Create abstract backend interface in template/files/shared/rate_limiting/backends/base.py (BaseBackend with check_limit, record_violation methods)
- [ ] T012 Implement Redis backend in template/files/shared/rate_limiting/backends/redis.py with connection pooling and circuit breaker per research.md
- [ ] T013 [P] Load and register token bucket Lua script (60 lines from data-model.md) in Redis backend
- [ ] T014 [P] Implement in-memory backend in template/files/shared/rate_limiting/backends/memory.py for testing only
- [ ] T015 [P] Implement Redis Sentinel support in Redis backend per research.md (3-node topology configuration)

### Core Utilities

- [ ] T016 [P] Implement client ID extraction logic in template/files/shared/rate_limiting/client_id.py (extract_client_id function with rightmost untrusted IP strategy per research.md)
- [ ] T017 [P] Implement rate limit headers generation in template/files/shared/rate_limiting/headers.py (generate_headers function for X-RateLimit-*, Retry-After per contracts/openapi.yml)
- [ ] T018 [P] Implement Prometheus metrics in template/files/shared/rate_limiting/metrics.py (5 metrics from research.md: requests_total, exceeded_total, current_usage, redis_latency, redis_errors)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Per-Client Rate Limiting (Priority: P1) 🎯 MVP

**Goal**: Implement IP-based rate limiting with token bucket algorithm, return HTTP 429 when limit exceeded, include standard rate limit headers in all responses

**Independent Test**: 
```bash
# Start Redis and FastAPI app, send 101 requests from single IP
for i in {1..101}; do curl -i http://localhost:8000/api/v1/test; done
# Verify: First 100 return 200 with X-RateLimit-* headers, 101st returns 429 with Retry-After
```

### Tests for User Story 1 (Write tests FIRST, ensure they FAIL before implementation)

- [ ] T019 [P] [US1] Unit test for token bucket refill logic in tests/rate_limiting/unit/test_token_bucket.py (test_refill_tokens, test_consume_tokens, test_bucket_exhaustion per research.md)
- [ ] T020 [P] [US1] Unit test for client ID extraction (IPv4/IPv6) in tests/rate_limiting/unit/test_client_id.py (test_ipv4_extraction, test_ipv6_extraction, test_ipv6_normalization per research.md)
- [ ] T021 [P] [US1] Unit test for rate limit headers generation in tests/rate_limiting/unit/test_headers.py (test_headers_within_limit, test_headers_exceeded, test_retry_after_calculation per contracts/openapi.yml)
- [ ] T022 [P] [US1] Integration test for Redis backend atomic operations in tests/rate_limiting/integration/test_redis_backend.py (test_atomic_incr, test_counter_creation, test_ttl_expiration per research.md)
- [ ] T023 [P] [US1] Integration test for FastAPI middleware with Redis in tests/rate_limiting/integration/test_middleware.py (test_200_response_with_headers, test_429_response_format per contracts/openapi.yml)

### Implementation for User Story 1

- [ ] T024 [P] [US1] Implement token bucket algorithm in template/files/shared/rate_limiting/limiters/token_bucket.py (TokenBucket class with refill, consume methods per research.md)
- [ ] T025 [US1] Implement rate limit check logic in Redis backend using Lua script from data-model.md (check_limit method with atomic EVALSHA call)
- [ ] T026 [US1] Implement FastAPI middleware in template/files/shared/rate_limiting/middleware.py (RateLimitMiddleware class with dispatch method per research.md)
- [ ] T027 [US1] Add middleware logic to extract client IP, check limit, add headers, return 429 on rejection per quickstart.md
- [ ] T028 [US1] Implement JSON error response for 429 per contracts/openapi.yml (RateLimitError schema)
- [ ] T029 [US1] Add structured logging for rate limit events in middleware (JSON logs per research.md)

**Checkpoint**: At this point, basic IP-based rate limiting should be fully functional and testable independently

---

## Phase 4: User Story 2 - Per-Endpoint Rate Limiting (Priority: P1)

**Goal**: Support configuring different rate limits for different API endpoints with wildcard patterns, maintain separate counters per endpoint

**Independent Test**:
```bash
# Configure /health with 1000 req/min, /compute with 10 req/min in config.toml
# Send 15 requests to /health, 11 requests to /compute
# Verify: All /health succeed, 11th /compute returns 429, /health still accessible
```

### Tests for User Story 2 (Write tests FIRST, ensure they FAIL before implementation)

- [ ] T030 [P] [US2] Unit test for endpoint pattern matching in tests/rate_limiting/unit/test_config.py (test_exact_match, test_wildcard_match, test_default_fallback per spec.md US2)
- [ ] T031 [P] [US2] Integration test for per-endpoint counters in tests/rate_limiting/integration/test_middleware.py (test_independent_endpoint_counters, test_wildcard_pattern_matching per spec.md US2)

### Implementation for User Story 2

- [ ] T032 [P] [US2] Implement endpoint pattern matching in config.py (get_limit method with regex compilation for wildcard patterns per spec.md US2)
- [ ] T033 [US2] Update Redis backend to use endpoint in Redis key pattern (ratelimit:counter:{scope}:{identifier}:{endpoint} per data-model.md)
- [ ] T034 [US2] Update middleware to pass endpoint to rate limit check per quickstart.md advanced configuration
- [ ] T035 [US2] Add endpoint configuration parsing from TOML (endpoints array in RateLimitConfig per quickstart.md)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (IP-based + per-endpoint limiting)

---

## Phase 5: User Story 3 - Authenticated User Rate Limiting (Priority: P1)

**Goal**: Apply rate limits based on authenticated user identity from JWT tokens, with tier-based limits (anonymous, standard, premium)

**Independent Test**:
```bash
# Configure tiers: anonymous=100, standard=1000, premium=5000
# Send unauthenticated request → verify 100 req/min limit (IP-based)
# Send request with JWT (tier=standard) → verify 1000 req/min limit (user-based)
# Send request with JWT (tier=premium) → verify 5000 req/min limit
```

### Tests for User Story 3 (Write tests FIRST, ensure they FAIL before implementation)

- [ ] T036 [P] [US3] Unit test for JWT user extraction in tests/rate_limiting/unit/test_client_id.py (test_jwt_user_id_extraction, test_jwt_tier_extraction, test_invalid_jwt_fallback per spec.md US3)
- [ ] T037 [P] [US3] Unit test for tier-based limit resolution in tests/rate_limiting/unit/test_config.py (test_tier_lookup, test_tier_precedence_over_ip per spec.md US3)
- [ ] T038 [P] [US3] Integration test for user-based rate limiting in tests/rate_limiting/integration/test_middleware.py (test_user_limit_higher_than_ip, test_tier_based_limits per spec.md US3)

### Implementation for User Story 3

- [ ] T039 [P] [US3] Add JWT token parsing to client_id.py (extract user_id and tier claims from Authorization header per research.md)
- [ ] T040 [US3] Update client ID format to include user: prefix (user:{user_id} vs ip:{ip_address} per data-model.md)
- [ ] T041 [US3] Add tier-based limit resolution to config.py (get_limit method checks tier before default per spec.md US3)
- [ ] T042 [US3] Update middleware to extract JWT before client IP per research.md middleware pattern
- [ ] T043 [US3] Add tier configuration parsing from TOML (tiers array in RateLimitConfig per quickstart.md)

**Checkpoint**: All three P1 user stories should now be independently functional (IP + per-endpoint + user/tier limiting)

---

## Phase 6: User Story 4 - Rate Limit Configuration Management (Priority: P2)

**Goal**: Load rate limits from TOML files and environment variables, support hot reload via SIGHUP, validate configuration at startup

**Independent Test**:
```bash
# Start app with config.toml (default_limit=100)
# Verify 100 req/min limit applied
# Update config.toml (default_limit=200), send SIGHUP
# Verify 200 req/min limit applied without restart, existing counters preserved
```

### Tests for User Story 4 (Write tests FIRST, ensure they FAIL before implementation)

- [ ] T044 [P] [US4] Unit test for TOML configuration loading in tests/rate_limiting/unit/test_config.py (test_toml_parse, test_default_values, test_validation_errors per spec.md FR-010)
- [ ] T045 [P] [US4] Unit test for environment variable overrides in tests/rate_limiting/unit/test_config.py (test_env_var_precedence per spec.md FR-011)
- [ ] T046 [P] [US4] Integration test for configuration hot reload in tests/rate_limiting/integration/test_middleware.py (test_sighup_reload, test_counters_preserved per spec.md FR-012)

### Implementation for User Story 4

- [ ] T047 [P] [US4] Implement TOML file parsing with Pydantic validation in config.py (from_toml class method per quickstart.md)
- [ ] T048 [P] [US4] Implement environment variable override logic in config.py (check env vars before TOML values per spec.md FR-011)
- [ ] T049 [P] [US4] Implement configuration validation rules in config.py (limit > 0, window ≥ 1, pattern regex compilation per spec.md FR-013)
- [ ] T050 [US4] Implement SIGHUP signal handler for hot reload in middleware.py (reload_config method preserving Redis counters per spec.md FR-012)
- [ ] T051 [US4] Add configuration reload endpoint (optional admin API) in middleware.py per quickstart.md

**Checkpoint**: Configuration management complete, supports TOML + env vars + hot reload

---

## Phase 7: User Story 5 - Distributed Rate Limiting (Priority: P2)

**Goal**: Ensure rate limits are enforced consistently across multiple API server instances using Redis as shared state backend

**Independent Test**:
```bash
# Start 3 API instances behind load balancer, Redis backend
# Configure 100 req/min limit
# Send 40 requests to instance 1, 35 to instance 2, 25 to instance 3 (100 total)
# Verify: All 100 succeed, 101st to any instance returns 429
# Kill instance 2, verify rate limiting continues on instances 1 & 3
```

### Tests for User Story 5 (Write tests FIRST, ensure they FAIL before implementation)

- [ ] T052 [P] [US5] Integration test for distributed consistency in tests/rate_limiting/integration/test_distributed.py (test_multi_instance_counter, test_total_requests_accurate per spec.md FR-004)
- [ ] T053 [P] [US5] Integration test for Redis failover in tests/rate_limiting/integration/test_distributed.py (test_sentinel_failover, test_counter_preservation per research.md)
- [ ] T054 [P] [US5] Chaos test for Redis failure modes in tests/rate_limiting/chaos/test_redis_failures.py (test_fail_open_mode, test_fail_closed_mode per spec.md FR-005)

### Implementation for User Story 5

- [ ] T055 [P] [US5] Verify Lua script atomicity in Redis backend (EVALSHA ensures no race conditions per research.md)
- [ ] T056 [P] [US5] Implement circuit breaker pattern in Redis backend (open after N failures, half-open after timeout per research.md)
- [ ] T057 [US5] Add fail-open/fail-closed modes in Redis backend (return allow/deny on Redis error per spec.md FR-005)
- [ ] T058 [US5] Implement Redis connection retry logic with exponential backoff in Redis backend per research.md
- [ ] T059 [US5] Add Redis Cluster support (optional) in Redis backend per spec.md dependencies

**Checkpoint**: Distributed rate limiting complete with HA, failover, and error handling

---

## Phase 8: User Story 6 - Rate Limit Monitoring & Observability (Priority: P2)

**Goal**: Export Prometheus metrics and structured logs for rate limiting activity

**Independent Test**:
```bash
# Start app with Prometheus metrics enabled
# Send requests that hit rate limit
# Verify /metrics endpoint shows rate_limit_requests_total, rate_limit_exceeded_total
# Verify JSON logs contain client_id, endpoint, limit, current_count per spec.md FR-017
```

### Tests for User Story 6 (Write tests FIRST, ensure they FAIL before implementation)

- [ ] T060 [P] [US6] Unit test for Prometheus metrics initialization in tests/rate_limiting/unit/test_metrics.py (test_counter_creation, test_histogram_buckets per research.md)
- [ ] T061 [P] [US6] Integration test for metrics export in tests/rate_limiting/integration/test_middleware.py (test_metrics_endpoint, test_counter_increments per spec.md FR-016)
- [ ] T062 [P] [US6] Integration test for structured logging in tests/rate_limiting/integration/test_middleware.py (test_json_log_format, test_log_fields per spec.md FR-017)

### Implementation for User Story 6

- [ ] T063 [P] [US6] Initialize Prometheus metrics in metrics.py (5 metrics from research.md: requests_total, exceeded_total, current_usage, redis_latency, redis_errors)
- [ ] T064 [P] [US6] Add metric recording to middleware (increment counters, update gauges, record histograms per research.md)
- [ ] T065 [P] [US6] Implement structured logging with structlog in middleware (JSON format with required fields per spec.md FR-017)
- [ ] T066 [US6] Add metrics endpoint mounting logic in quickstart.md example (mount /metrics with make_asgi_app)
- [ ] T067 [US6] Add cardinality control for gauge metrics (limit client_id labels to top N clients per research.md)

**Checkpoint**: Observability complete with Prometheus metrics and structured logs

---

## Phase 9: User Story 7 - Rate Limit Response Headers (Priority: P3)

**Goal**: Include standard rate limit headers (X-RateLimit-*, Retry-After) in all API responses with JSON error body on 429

**Independent Test**:
```bash
# Send requests to rate-limited endpoint
# Verify headers in 200 response: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
# Verify headers in 429 response: Same headers + Retry-After
# Verify 429 JSON body matches RateLimitError schema from contracts/openapi.yml
```

### Tests for User Story 7 (Write tests FIRST, ensure they FAIL before implementation)

- [ ] T068 [P] [US7] Integration test for header presence in tests/rate_limiting/integration/test_middleware.py (test_headers_in_200, test_headers_in_429, test_headers_in_500 per spec.md FR-002)
- [ ] T069 [P] [US7] Integration test for Retry-After accuracy in tests/rate_limiting/integration/test_middleware.py (test_retry_after_matches_reset per spec.md FR-014)
- [ ] T070 [P] [US7] Integration test for JSON error body schema in tests/rate_limiting/integration/test_middleware.py (test_429_json_schema per contracts/openapi.yml)

### Implementation for User Story 7

- [ ] T071 [P] [US7] Verify headers.py generates all required headers (X-RateLimit-Limit, Remaining, Reset, Retry-After per contracts/openapi.yml)
- [ ] T072 [P] [US7] Update middleware to inject headers into all responses (200, 429, 5xx per spec.md FR-002)
- [ ] T073 [US7] Implement 429 JSON error response with RateLimitError schema in middleware per contracts/openapi.yml
- [ ] T074 [US7] Add support for multiple time windows in error response (limits_exceeded array per contracts/openapi.yml)
- [ ] T075 [US7] Add documentation_url field to error responses per contracts/openapi.yml

**Checkpoint**: Response headers and error bodies complete per OpenAPI spec

---

## Phase 10: Optional Features (FR-018 to FR-021)

**Purpose**: Implement optional features from specification

### Rate Limit Exemptions (FR-018)

- [ ] T076 [P] Implement exemption list checking in config.py (is_exempted method for IP and user_id per spec.md FR-018)
- [ ] T077 [P] Update middleware to skip rate limiting for exempted clients per quickstart.md
- [ ] T078 [P] Add exemption configuration parsing from TOML (exemptions array per quickstart.md)

### Sliding Window Algorithm (FR-019)

- [ ] T079 [P] Implement sliding window algorithm in template/files/shared/rate_limiting/limiters/sliding_window.py (SlidingWindow class with ZSET operations per research.md)
- [ ] T080 [P] Add algorithm selection logic in Redis backend (check config.algorithm field per quickstart.md)
- [ ] T081 [P] Add unit tests for sliding window in tests/rate_limiting/unit/test_sliding_window.py

### Multiple Time Windows (FR-020)

- [ ] T082 [P] Extend LimitConfig to support multiple windows in config.py (windows: list[tuple[int, int]] per spec.md FR-020)
- [ ] T083 Update Redis backend to check all configured windows per spec.md FR-020
- [ ] T084 Update error response to include all exceeded limits per contracts/openapi.yml multiple_limits_exceeded example

### Progressive Rate Limit Penalties (FR-021)

- [ ] T085 [P] Implement violation tracking in Redis backend (record_violation method with ZSET per data-model.md)
- [ ] T086 [P] Implement penalty calculation in Redis backend (check_progressive_penalty method per research.md)
- [ ] T087 Update middleware to apply penalty multiplier to cooldown per quickstart.md
- [ ] T088 [P] Add progressive penalty tests in tests/rate_limiting/integration/test_middleware.py (test_penalty_escalation per spec.md FR-021)

---

## Phase 11: Performance & Load Testing

**Purpose**: Validate performance targets and accuracy under load

- [ ] T089 [P] Implement Locust load test scenario in tests/rate_limiting/load/test_performance.py (1000 req/s, 100 concurrent clients per research.md)
- [ ] T090 [P] Add latency measurement to load tests (verify P95 < 10ms per spec.md SC-003)
- [ ] T091 Run load tests and record baseline metrics in samples/metadata/ (throughput, latency, accuracy per spec.md SC-002)
- [ ] T092 [P] Implement chaos test for Redis shutdown in tests/rate_limiting/chaos/test_redis_failures.py (verify fail-open/closed per research.md)
- [ ] T093 [P] Implement chaos test for Sentinel failover in tests/rate_limiting/chaos/test_redis_failures.py (verify <1s disruption per research.md)

---

## Phase 12: Documentation & Polish

**Purpose**: Complete documentation and final refinements

- [ ] T094 [P] Finalize module documentation in docs/modules/rate-limiting.md.jinja (include all features, configuration examples, troubleshooting per quickstart.md)
- [ ] T095 [P] Add inline code documentation and docstrings to all public APIs (middleware, config, backends per SC-009)
- [ ] T096 [P] Create integration examples for rendered projects in docs/ (FastAPI middleware setup, config.toml examples)
- [ ] T097 [P] Update AGENTS.md with rate limiting technologies (FastAPI middleware, Redis Sentinel, Lua scripting, token bucket per plan.md)
- [ ] T098 Run full test suite and verify coverage targets (≥90% line, ≥80% branch per spec.md SC-010)
- [ ] T099 Run quickstart.md validation per quickstart.md steps (Docker Redis, FastAPI app, curl tests)
- [ ] T100 Code review and refactoring for code quality per spec.md constitution check

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - Phase 3 (US1): Basic rate limiting - NO dependencies on other stories (MVP)
  - Phase 4 (US2): Per-endpoint - depends on US1 (builds on basic limiting)
  - Phase 5 (US3): User-based - depends on US1 (builds on basic limiting)
  - Phase 6 (US4): Configuration - can run in parallel with US2/US3 after US1
  - Phase 7 (US5): Distributed - depends on US1 (tests basic limiting across instances)
  - Phase 8 (US6): Observability - can run in parallel after US1
  - Phase 9 (US7): Headers - depends on US1 (adds to basic limiting responses)
- **Optional Features (Phase 10)**: Depend on relevant user stories being complete
- **Performance Testing (Phase 11)**: Depends on US1-US5 being complete
- **Documentation (Phase 12)**: Depends on all implemented features being complete

### User Story Dependencies

- **US1 (P1)**: FOUNDATION - Must complete first, all other stories build on this
- **US2 (P1)**: Depends on US1 (extends basic limiting with per-endpoint configuration)
- **US3 (P1)**: Depends on US1 (extends basic limiting with user identification)
- **US4 (P2)**: Depends on US1 (configuration system for basic limiting)
- **US5 (P2)**: Depends on US1 (distributed version of basic limiting)
- **US6 (P2)**: Depends on US1 (observability for basic limiting)
- **US7 (P3)**: Depends on US1 (headers for basic limiting)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach per research.md)
- Unit tests [P] can run in parallel (different test files)
- Models/utilities [P] can run in parallel (different source files)
- Integration happens after core components complete
- Story validation before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T002, T003, T004, T005, T006, T007 can all run in parallel (different files)
- **Phase 2 (Foundational)**: T009, T010, T014, T015, T016, T017, T018 can run in parallel (different files)
- **Within US1 Tests**: T019, T020, T021, T022, T023 can run in parallel (different test files)
- **Within US1 Implementation**: T024 can run parallel with other non-dependent tasks
- **After US1 Complete**: US2, US3, US4, US6, US7 can start in parallel (if team capacity allows)
- **Optional Features**: T076-T078 (exemptions), T079-T081 (sliding window), T082-T084 (multiple windows), T085-T088 (penalties) can run in parallel

---

## Parallel Example: User Story 1 (MVP)

```bash
# Launch all tests for User Story 1 together:
Task T019: "Unit test for token bucket refill logic"
Task T020: "Unit test for client ID extraction (IPv4/IPv6)"
Task T021: "Unit test for rate limit headers generation"
Task T022: "Integration test for Redis backend atomic operations"
Task T023: "Integration test for FastAPI middleware with Redis"

# Launch parallel implementations:
Task T024: "Implement token bucket algorithm (limiters/token_bucket.py)"
# (Other US1 implementation tasks follow sequentially due to dependencies)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T018) - CRITICAL foundation
3. Complete Phase 3: User Story 1 (T019-T029) - Basic IP-based rate limiting
4. **STOP and VALIDATE**: Run quickstart.md test (101 requests, verify 100 succeed, 101st fails with 429)
5. Deploy/demo if ready - this is a working MVP!

**MVP Deliverable**: IP-based rate limiting with token bucket, Redis backend, standard headers, 429 responses

### Incremental Delivery

1. **Foundation** (Phases 1-2): ~15 tasks → Redis backend, config system, utilities ready
2. **MVP** (Phase 3 - US1): ~11 tasks → Basic rate limiting working end-to-end
3. **Per-Endpoint** (Phase 4 - US2): ~6 tasks → Add endpoint-specific limits
4. **User-Based** (Phase 5 - US3): ~7 tasks → Add JWT authentication and tiers
5. **Configuration** (Phase 6 - US4): ~5 tasks → Add hot reload and env var overrides
6. **Distributed** (Phase 7 - US5): ~5 tasks → Production-ready with HA
7. **Observability** (Phase 8 - US6): ~5 tasks → Add metrics and logging
8. **Polish** (Phases 9-12): ~28 tasks → Headers, optional features, testing, docs

Each milestone adds value and can be independently deployed/demoed.

### Parallel Team Strategy

With 3 developers after Foundation complete:

1. **Team**: Complete Setup (Phase 1) + Foundational (Phase 2) together
2. **Split after Foundational**:
   - Developer A: User Story 1 (Phase 3) - MVP critical path
   - Developer B: Configuration (Phase 6 US4) - can run parallel with US1
   - Developer C: Observability (Phase 8 US6) - can run parallel with US1
3. **After US1 Complete**:
   - Developer A: User Story 2 (Phase 4)
   - Developer B: User Story 3 (Phase 5)
   - Developer C: User Story 7 (Phase 9)
4. **Final Integration**: Distributed (Phase 7 US5) + Performance Testing (Phase 11) + Documentation (Phase 12)

---

## Test Coverage Targets

Per spec.md SC-010:
- **Line Coverage**: ≥90%
- **Branch Coverage**: ≥80%

**Test Count by Type**:
- Unit tests: ~15 test tasks (T019-T021, T030, T036-T038, T044-T046, T060, T068-T070, T081)
- Integration tests: ~10 test tasks (T022-T023, T031, T052-T054, T061-T062, T088)
- Load tests: ~2 test tasks (T089-T090)
- Chaos tests: ~2 test tasks (T092-T093)
- **Total**: ~29 test tasks out of 100 tasks (29% test focus)

---

## Success Criteria Mapping

Tasks map to success criteria from spec.md:

- **SC-001** (Configuration Simplicity): T001-T007, T047-T051, T094-T096
- **SC-002** (Rate Limit Accuracy): T019, T022, T052, T089, T091
- **SC-003** (Low Performance Overhead): T089-T091
- **SC-004** (Redis Connection Pooling): T012, T015
- **SC-005** (Concurrent Request Handling): T089, T091
- **SC-006** (Distributed Consistency): T052, T055-T059
- **SC-007** (Header Compliance): T017, T021, T068, T071-T072
- **SC-008** (Retry-After Accuracy): T069, T074
- **SC-009** (Documentation Completeness): T007, T094-T096
- **SC-010** (Test Coverage): T019-T023, T030-T031, T036-T038, T044-T046, T052-T054, T060-T062, T068-T070, T088-T093
- **SC-011** (Prometheus Metrics Availability): T063-T067
- **SC-012** (Redis Failure Recovery): T054, T057-T058, T092
- **SC-013** (Configuration Validation): T049
- **SC-014** (Client Library Compatibility): T071-T075
- **SC-015** (Client Retry Guidance): T094, T096

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US1-US7) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD Approach**: Write tests FIRST, ensure they FAIL, then implement to make them PASS
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Phase 3 (US1) is the MVP - can stop here for minimal viable implementation
- Lua script (60 lines) is pre-written in data-model.md - copy into T013
- OpenAPI spec is complete in contracts/ - use for T023, T028, T070, T073-T075

---

## Total Task Count: 100 tasks

- Setup: 7 tasks
- Foundational: 11 tasks (BLOCKS all user stories)
- User Story 1 (P1 MVP): 11 tasks
- User Story 2 (P1): 6 tasks
- User Story 3 (P1): 7 tasks
- User Story 4 (P2): 5 tasks
- User Story 5 (P2): 5 tasks
- User Story 6 (P2): 5 tasks
- User Story 7 (P3): 8 tasks
- Optional Features: 13 tasks
- Performance Testing: 5 tasks
- Documentation & Polish: 7 tasks

**Suggested MVP Scope**: Phases 1-3 (29 tasks) → Working IP-based rate limiting with Redis, headers, 429 responses
