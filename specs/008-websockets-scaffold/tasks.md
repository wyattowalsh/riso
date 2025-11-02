---
description: "Task breakdown for WebSocket Scaffold implementation"
---

# Tasks: WebSocket Scaffold

**Input**: Design documents from `/specs/008-websockets-scaffold/`  
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/ (complete), quickstart.md (complete)

**Tests**: Following Constitution Principle V (Test-First Development), tests MUST be written before implementation. Each user story phase includes test tasks that define expected behavior (RED → GREEN → REFACTOR).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

All paths assume template structure:
- Template files: `template/files/python/websocket/`
- Documentation: `docs/modules/`
- Rendered project tests: `tests/websocket/` (examples in template)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize WebSocket module structure and configuration

- [ ] T001 Create WebSocket module directory structure in template/files/python/websocket/
- [ ] T002 Add websocket_module option to template/copier.yml with enabled/disabled choices
- [ ] T003 [P] Create base __init__.py.jinja in template/files/python/websocket/
- [ ] T004 [P] Create config.py.jinja with WebSocketConfig settings model in template/files/python/websocket/
- [ ] T005 [P] Create exceptions.py.jinja with WebSocket error hierarchy in template/files/python/websocket/
- [ ] T006 Update template metadata in template/files/shared/module_catalog.json.jinja to include websocket module

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create models.py.jinja with Message, ConnectionState, and base Pydantic models in template/files/python/websocket/
- [ ] T008 Create connection.py.jinja with WebSocketConnection class in template/files/python/websocket/
- [ ] T009 Create manager.py.jinja with ConnectionManager singleton scaffold in template/files/python/websocket/
- [ ] T010 [P] Create utils.py.jinja with helper functions (UUID generation, timestamp utils) in template/files/python/websocket/
- [ ] T011 [P] Update pyproject.toml.jinja to include websockets library dependency when websocket_module=enabled
- [ ] T012 Create middleware.py.jinja with ConnectionMiddleware abstract base class in template/files/python/websocket/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic WebSocket Connection (Priority: P1) 🎯 MVP

**Goal**: Enable developers to establish persistent WebSocket connections with message send/receive and clean disconnection

**Independent Test**: Connect a WebSocket client to the endpoint, send a message, receive a response, and cleanly disconnect. Verify connection lifecycle is properly managed with no resource leaks.

### Tests for User Story 1 (Test-First Development)

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation (RED phase)

- [ ] T013 [P] [US1] Create test_connection_lifecycle.py in template/files/python/tests/websocket/ with tests for connect/disconnect
- [ ] T014 [P] [US1] Create test_message_exchange.py in template/files/python/tests/websocket/ with tests for send_json/send_text
- [ ] T015 [P] [US1] Create test_connection_state.py in template/files/python/tests/websocket/ with tests for state transitions

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement accept() method in connection.py.jinja for WebSocket handshake
- [ ] T017 [P] [US1] Implement send_json() method in connection.py.jinja for sending JSON messages
- [ ] T018 [P] [US1] Implement send_text() method in connection.py.jinja for sending text messages
- [ ] T019 [US1] Implement connect() method in manager.py.jinja to register new connections
- [ ] T020 [US1] Implement disconnect() method in manager.py.jinja to clean up connections
- [ ] T021 [US1] Implement close() method in connection.py.jinja with proper cleanup
- [ ] T022 [US1] Add connection state management (CONNECTING→CONNECTED→CLOSING→CLOSED) in connection.py.jinja
- [ ] T023 [US1] Create decorators.py.jinja with @websocket_endpoint decorator for FastAPI integration in template/files/python/websocket/
- [ ] T024 [US1] Add connection metadata tracking (IP, user agent, timestamps) in connection.py.jinja
- [ ] T025 [US1] Update manager.py.jinja to use asyncio.Lock for thread-safe connection registry access
- [ ] T026 [US1] Add example WebSocket endpoint in template/files/python/api/websocket_endpoints.py.jinja

**Checkpoint**: At this point, User Story 1 should be fully functional - basic connections work with message exchange

---

## Phase 4: User Story 2 - Connection Health & Heartbeats (Priority: P1)

**Goal**: Automatically detect stale connections and clean them up via heartbeat ping/pong mechanism

**Independent Test**: Establish a connection, simulate network interruption (block packets without closing socket), verify the server detects the dead connection within timeout period and cleans up resources.

### Tests for User Story 2 (Test-First Development)

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation (RED phase)

- [ ] T027 [P] [US2] Create test_heartbeat.py in template/files/python/tests/websocket/ with tests for ping/pong mechanism
- [ ] T028 [P] [US2] Create test_idle_timeout.py in template/files/python/tests/websocket/ with tests for idle connection cleanup
- [ ] T029 [P] [US2] Create test_dead_connection.py in template/files/python/tests/websocket/ with tests for timeout detection

### Implementation for User Story 2

- [ ] T030 [P] [US2] Implement heartbeat_loop() in utils.py.jinja with ping/pong protocol
- [ ] T031 [P] [US2] Add heartbeat configuration to config.py.jinja (interval, timeout settings)
- [ ] T032 [US2] Integrate heartbeat_loop as background task in connection.py.jinja
- [ ] T033 [US2] Implement pong handler in connection.py.jinja to track last_pong timestamp
- [ ] T034 [US2] Add heartbeat timeout detection in utils.py.jinja that closes dead connections
- [ ] T035 [US2] Implement idle timeout tracking in connection.py.jinja with time_since_activity()
- [ ] T036 [US2] Add idle_timeout background task in manager.py.jinja to close silent connections
- [ ] T037 [US2] Update connection.py.jinja to set last_activity_at on every message send/receive
- [ ] T038 [US2] Add heartbeat.ping and heartbeat.pong message types to models.py.jinja
- [ ] T039 [US2] Update example endpoint in websocket_endpoints.py.jinja to demonstrate heartbeat handling

**Checkpoint**: Connection health monitoring is complete - dead and idle connections are automatically detected and cleaned up

---

## Phase 5: User Story 3 - Authentication & Authorization (Priority: P1)

**Goal**: Secure WebSocket endpoints so only authenticated users can connect, integrating with existing FastAPI auth

**Independent Test**: Attempt to connect without credentials (should fail with 403), connect with valid credentials (should succeed), verify authentication state is maintained throughout connection lifecycle.

### Tests for User Story 3 (Test-First Development)

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation (RED phase)

- [ ] T040 [P] [US3] Create test_authentication.py in template/files/python/tests/websocket/ with tests for JWT validation
- [ ] T041 [P] [US3] Create test_authorization.py in template/files/python/tests/websocket/ with tests for permission checks
- [ ] T042 [P] [US3] Create test_auth_failures.py in template/files/python/tests/websocket/ with tests for rejection scenarios

### Implementation for User Story 3

- [ ] T043 [P] [US3] Create authentication middleware in middleware.py.jinja extending ConnectionMiddleware
- [ ] T044 [P] [US3] Implement get_current_user_websocket() dependency in decorators.py.jinja for JWT/token extraction
- [ ] T045 [US3] Add authentication validation in decorators.py.jinja that closes connection on auth failure
- [ ] T046 [US3] Update connection.py.jinja to store authenticated user in connection metadata
- [ ] T047 [US3] Add authorization check helper can_perform_action() in middleware.py.jinja
- [ ] T048 [US3] Implement token extraction from query params/headers/cookies in decorators.py.jinja
- [ ] T049 [US3] Add AUTH_REQUIRED and AUTH_FAILED error codes to exceptions.py.jinja
- [ ] T050 [US3] Update manager.py.jinja to track connections by user_id for multi-connection support
- [ ] T051 [US3] Add example authenticated endpoint in websocket_endpoints.py.jinja with Depends(get_current_user_websocket)
- [ ] T052 [US3] Update models.py.jinja to include user field in WebSocketConnectionModel

**Checkpoint**: Authentication is fully integrated - only authorized users can establish connections

---

## Phase 6: User Story 4 - Broadcasting to Multiple Clients (Priority: P2)

**Goal**: Enable room-based broadcasting where messages from one client are efficiently sent to multiple other clients

**Independent Test**: Connect multiple clients to the same room, send a message from one client, verify all other clients in that room receive the message with <100ms latency.

### Tests for User Story 4 (Test-First Development)

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation (RED phase)

- [ ] T053 [P] [US4] Create test_room_management.py in template/files/python/tests/websocket/ with tests for join/leave operations
- [ ] T054 [P] [US4] Create test_broadcasting.py in template/files/python/tests/websocket/ with tests for message fan-out
- [ ] T055 [P] [US4] Create test_room_isolation.py in template/files/python/tests/websocket/ with tests ensuring room boundaries

### Implementation for User Story 4

- [ ] T056 [P] [US4] Add Room model to models.py.jinja with room_id, connection_ids, metadata
- [ ] T057 [P] [US4] Create rooms registry in manager.py.jinja as Dict[str, Room]
- [ ] T058 [US4] Implement join_room() method in manager.py.jinja to add connection to room
- [ ] T059 [US4] Implement leave_room() method in manager.py.jinja to remove connection from room
- [ ] T060 [US4] Implement broadcast_to_room() in manager.py.jinja using asyncio.gather for parallel sends
- [ ] T061 [US4] Add connection_rooms tracking in manager.py.jinja (Dict[str, Set[str]]) for reverse lookup
- [ ] T062 [US4] Implement room cleanup in manager.py.jinja when last member leaves
- [ ] T063 [US4] Add exclude_sender parameter to broadcast_to_room() in manager.py.jinja
- [ ] T064 [US4] Add room.join, room.leave, room.broadcast message types to models.py.jinja
- [ ] T065 [US4] Implement broadcast error handling in manager.py.jinja with per-connection try/except
- [ ] T066 [US4] Add room membership validation in manager.py.jinja before broadcasting
- [ ] T067 [US4] Update connection.py.jinja with rooms: Set[str] attribute
- [ ] T068 [US4] Add room operations to example endpoint in websocket_endpoints.py.jinja

**Checkpoint**: Room-based broadcasting is operational - multi-client scenarios work efficiently

---

## Phase 7: User Story 5 - Connection Management & Monitoring (Priority: P2)

**Goal**: Provide visibility into active WebSocket connections for monitoring, debugging, and graceful shutdown

**Independent Test**: Establish connections, query the connection registry to see metadata, trigger graceful shutdown and verify all connections receive closure notification.

### Tests for User Story 5 (Test-First Development)

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation (RED phase)

- [ ] T069 [P] [US5] Create test_connection_queries.py in template/files/python/tests/websocket/ with tests for registry inspection
- [ ] T070 [P] [US5] Create test_graceful_shutdown.py in template/files/python/tests/websocket/ with tests for clean closure
- [ ] T071 [P] [US5] Create test_connection_limits.py in template/files/python/tests/websocket/ with tests for limit enforcement

### Implementation for User Story 5

- [ ] T072 [P] [US5] Implement get_all_connections() in manager.py.jinja returning connection metadata list
- [ ] T073 [P] [US5] Implement get_connections_by_user() in manager.py.jinja for user-specific queries
- [ ] T074 [P] [US5] Implement get_connection_count() in manager.py.jinja for metrics
- [ ] T075 [US5] Implement graceful_shutdown() in manager.py.jinja to close all connections with notification
- [ ] T076 [US5] Add connection limits to config.py.jinja (max_connections_global, max_per_user, max_per_ip)
- [ ] T077 [US5] Implement connection limit enforcement in manager.py.jinja connect() method
- [ ] T078 [US5] Add connection duration tracking in connection.py.jinja (connected_at to disconnect time)
- [ ] T079 [US5] Implement get_connections_by_room() in manager.py.jinja for room inspection
- [ ] T080 [US5] Add ConnectionMetadata model to models.py.jinja with all tracking fields
- [ ] T081 [US5] Create monitoring endpoint example in websocket_endpoints.py.jinja for admin dashboard
- [ ] T082 [US5] Add connection metrics (total, per room, per user) to manager.py.jinja

**Checkpoint**: Full operational visibility is available - connections can be monitored and gracefully managed

---

## Phase 8: User Story 6 - Error Handling & Resilience (Priority: P2)

**Goal**: Robust error handling that gracefully manages invalid messages, protocol violations, and network errors without crashing

**Independent Test**: Send malformed messages, trigger exceptions in handlers, simulate network errors, verify system recovers gracefully without affecting other connections.

### Tests for User Story 6 (Test-First Development)

> **CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation (RED phase)

- [ ] T083 [P] [US6] Create test_error_handling.py in template/files/python/tests/websocket/ with tests for exception recovery
- [ ] T084 [P] [US6] Create test_message_validation.py in template/files/python/tests/websocket/ with tests for malformed messages
- [ ] T085 [P] [US6] Create test_backpressure.py in template/files/python/tests/websocket/ with tests for queue limits

### Implementation for User Story 6

- [ ] T086 [P] [US6] Create error message models in models.py.jinja with ErrorCode enum
- [ ] T087 [P] [US6] Implement message validation in utils.py.jinja using Pydantic
- [ ] T088 [P] [US6] Add RateLimiter class to utils.py.jinja with sliding window algorithm
- [ ] T089 [US6] Implement message size validation in connection.py.jinja with configurable MAX_MESSAGE_SIZE
- [ ] T090 [US6] Add bounded queue implementation in connection.py.jinja using asyncio.Queue(maxsize)
- [ ] T091 [US6] Implement backpressure error response in connection.py.jinja when queue full
- [ ] T092 [US6] Add rate limiting middleware in middleware.py.jinja that tracks message frequency
- [ ] T093 [US6] Implement exception handling wrapper in decorators.py.jinja for message handlers
- [ ] T094 [US6] Add structured error logging in exceptions.py.jinja with correlation IDs
- [ ] T095 [US6] Implement network error recovery in connection.py.jinja with retry logic
- [ ] T096 [US6] Add all error codes to exceptions.py.jinja (BACKPRESSURE, MESSAGE_TOO_LARGE, RATE_LIMIT, etc.)
- [ ] T097 [US6] Create error response helper format_error_message() in utils.py.jinja
- [ ] T098 [US6] Update manager.py.jinja to log errors without disrupting other connections
- [ ] T099 [US6] Add protocol violation handling in connection.py.jinja for invalid frames

**Checkpoint**: Error handling is comprehensive - system is resilient to failures without cascading

---

## Phase 9: User Story 7 - Testing Support (Priority: P3)

**Goal**: Provide pytest fixtures and utilities for developers to write automated WebSocket tests

**Independent Test**: Write a test suite using provided fixtures, verify tests run correctly and can simulate multi-user scenarios.

**Note**: US7 IS the testing infrastructure, so test tasks are not required here (would be meta-tests of test utilities)

### Implementation for User Story 7

- [ ] T100 [P] [US7] Create testing/\_\_init\_\_.py.jinja in template/files/python/websocket/testing/
- [ ] T101 [P] [US7] Create fixtures.py.jinja with ws_client fixture in template/files/python/websocket/testing/
- [ ] T102 [P] [US7] Add authenticated_ws_client fixture in fixtures.py.jinja with JWT support
- [ ] T103 [P] [US7] Create utilities.py.jinja with multi_client_simulator helper in template/files/python/websocket/testing/
- [ ] T104 [US7] Add conftest.py.jinja in template/files/python/tests/websocket/ with shared fixtures
- [ ] T105 [US7] Create test_connection.py.jinja example test in template/files/python/tests/websocket/
- [ ] T106 [US7] Create test_heartbeat.py.jinja example test in template/files/python/tests/websocket/
- [ ] T107 [US7] Create test_broadcasting.py.jinja example test in template/files/python/tests/websocket/
- [ ] T108 [US7] Add async test utilities in utilities.py.jinja for event loop management
- [ ] T109 [US7] Create test_authentication.py.jinja example in template/files/python/tests/websocket/
- [ ] T110 [US7] Add WebSocket assertion helpers in utilities.py.jinja (assert_message_received, etc.)

**Checkpoint**: Complete testing infrastructure is available - developers can easily write WebSocket tests

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, integration, and final refinements

- [ ] T111 [P] Create docs/modules/websockets.md.jinja with comprehensive module documentation
- [ ] T112 [P] Update docs/quickstart.md.jinja with WebSocket usage examples
- [ ] T113 [P] Add WebSocket section to AGENTS.md with active technologies
- [ ] T114 [P] Create contract validation tests in scripts/ci/ for message schemas
- [ ] T115 [P] Add CORS configuration to config.py.jinja with websocket_origins setting (FR-013)
- [ ] T116 Update template/files/shared/.github/workflows/riso-quality.yml.jinja to test WebSocket module when enabled
- [ ] T117 Add WebSocket smoke tests to scripts/automation/render_client.py
- [ ] T118 Update samples/default/copier-answers.yml with websocket_module=enabled
- [ ] T119 Update samples/full-stack/copier-answers.yml with websocket_module=enabled
- [ ] T120 [P] Add multi-server Redis pattern documentation to docs/modules/websockets.md.jinja
- [ ] T121 [P] Add container support documentation (Docker/compose) to docs/modules/websockets.md.jinja
- [ ] T122 [P] Add monitoring integration examples (Prometheus metrics) to docs/modules/websockets.md.jinja
- [ ] T123 [P] Create load testing script validating 10K connections and <100ms broadcast latency (SC-002, SC-003, SC-009)
- [ ] T124 Create upgrade guide section in docs/upgrade-guide.md.jinja for WebSocket module
- [ ] T125 Validate all contract JSON schemas in contracts/ directory against JSON Schema Draft-07
- [ ] T126 Run ./scripts/render-samples.sh with websocket_module=enabled and verify smoke tests pass
- [ ] T127 Update copilot-instructions.md with WebSocket scaffold information

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-9)**: All depend on Foundational phase completion
  - US1 (Basic Connection) is foundational for all other stories
  - US2 (Heartbeats) depends on US1 completion
  - US3 (Authentication) depends on US1 completion
  - US4 (Broadcasting) depends on US1 and US2 completion
  - US5 (Monitoring) can start after US1, benefits from US3-US4 being complete
  - US6 (Error Handling) can start after US1, integrates with all other stories
  - US7 (Testing) can start anytime but benefits from having stories to test
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

```
US1 (Basic Connection) ─┬─→ US2 (Heartbeats)
                        ├─→ US3 (Authentication)
                        └─→ US4 (Broadcasting) ──→ US5 (Monitoring)
                                                   US6 (Error Handling)
                                                   US7 (Testing)
```

- **US1**: No dependencies on other stories
- **US2**: Depends on US1 (needs working connections)
- **US3**: Depends on US1 (needs working connections)
- **US4**: Depends on US1 and US2 (needs healthy connections)
- **US5**: Depends on US1; enhanced by US3-US4
- **US6**: Depends on US1; integrates with all other stories
- **US7**: Can start after US1; benefits from having multiple stories to test

### Within Each User Story

- Models before services
- Services before managers
- Core implementation before examples
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005 can run in parallel (different files)

**Phase 2 (Foundational)**: T010, T011, T012 can run in parallel after T007-T009 complete

**Phase 3 (US1)**: T013, T014, T015 can run in parallel (different methods in connection.py.jinja)

**Phase 4 (US2)**: T024, T025 can run in parallel (different files)

**Phase 5 (US3)**: T034, T035 can run in parallel (different files)

**Phase 6 (US4)**: T044, T045 can run in parallel (models vs manager logic)

**Phase 7 (US5)**: T057, T058, T059 can run in parallel (different query methods)

**Phase 8 (US6)**: T068, T069, T070 can run in parallel (different concerns)

**Phase 9 (US7)**: T082, T083, T084, T085 can run in parallel (different test utilities)

**Phase 10 (Polish)**: T093, T094, T095, T096, T101, T102, T103 can run in parallel (different documentation files)

---

## Parallel Example: User Story 1

```bash
# Launch core connection methods together:
Task: "Implement accept() method in connection.py.jinja"
Task: "Implement send_json() method in connection.py.jinja"
Task: "Implement send_text() method in connection.py.jinja"

# Then launch manager operations:
Task: "Implement connect() method in manager.py.jinja"
Task: "Implement disconnect() method in manager.py.jinja"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup → Module structure ready
2. Complete Phase 2: Foundational → Core models ready
3. Complete Phase 3: User Story 1 → Basic connections work
4. Complete Phase 4: User Story 2 → Connection health monitoring active
5. Complete Phase 5: User Story 3 → Secure connections enforced
6. **STOP and VALIDATE**: Test US1-US3 independently, verify authentication and heartbeats
7. Deploy/demo MVP with secure, healthy connections

### Incremental Delivery

1. Setup + Foundational → Foundation ready (T001-T012)
2. Add US1 → Test independently → Basic WebSocket works (T013-T023)
3. Add US2 → Test independently → Dead connections detected (T024-T033)
4. Add US3 → Test independently → Secure endpoints enforced (T034-T043)
5. Add US4 → Test independently → Broadcasting operational (T044-T056)
6. Add US5 → Test independently → Full monitoring available (T057-T067)
7. Add US6 → Test independently → Error resilience complete (T068-T081)
8. Add US7 → Test independently → Testing utilities available (T082-T092)
9. Polish → Documentation and integration complete (T093-T107)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T012)
2. Once Foundational is done:
   - **Developer A**: US1 (Basic Connection) - T013-T023
   - **Developer B**: US2 (Heartbeats) - T024-T033 (waits for US1 to reach T020)
   - **Developer C**: US3 (Authentication) - T034-T043 (waits for US1 to reach T020)
3. After US1-US3 complete:
   - **Developer A**: US4 (Broadcasting) - T044-T056
   - **Developer B**: US6 (Error Handling) - T068-T081
   - **Developer C**: US7 (Testing) - T082-T092
4. After US4 completes:
   - **Developer A**: US5 (Monitoring) - T057-T067
5. All developers: Polish phase in parallel (T093-T107)

---

## Task Count Summary

- **Total Tasks**: 127 tasks (was 107, added 20 test tasks)
- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (US1)**: 14 tasks (3 test + 11 implementation)
- **Phase 4 (US2)**: 13 tasks (3 test + 10 implementation)
- **Phase 5 (US3)**: 13 tasks (3 test + 10 implementation)
- **Phase 6 (US4)**: 16 tasks (3 test + 13 implementation)
- **Phase 7 (US5)**: 14 tasks (3 test + 11 implementation)
- **Phase 8 (US6)**: 17 tasks (3 test + 14 implementation)
- **Phase 9 (US7)**: 11 tasks (0 test - IS testing infrastructure)
- **Phase 10 (Polish)**: 17 tasks (added CORS config + load testing)

**Parallel Opportunities**: 49 tasks can run in parallel (marked with [P])

**Independent Test Criteria**:
- US1: Connect, send, receive, disconnect → No resource leaks
- US2: Dead connection detection within 60s → Resources cleaned
- US3: Auth rejection on invalid credentials → User context maintained
- US4: Broadcast to multiple clients → <100ms latency (p95)
- US5: Query connections, graceful shutdown → Metadata accurate
- US6: Malformed messages handled → No crashes, isolated errors
- US7: Test fixtures work → Multi-client simulation successful

**Suggested MVP Scope**: Phase 1-2 (Setup + Foundational) + Phase 3-5 (US1-US3) = 42 tasks for secure, healthy WebSocket connections (including test-first development)

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability (US1-US7)
- **Test-First Development**: Following Constitution Principle V, all tests written before implementation (RED → GREEN → REFACTOR)
- **Template paths**: All implementation in `template/files/python/websocket/`
- **Jinja suffix**: All template files use `.jinja` suffix for Copier rendering
- **Module sovereignty**: WebSocket module is optional via `websocket_module=enabled` in copier.yml
- **Minimal baseline**: Zero impact when disabled, ~15 files + tests when enabled
- **Constitution compliance**: All tasks maintain deterministic generation, quality integration, test-first development, documentation standards
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Verify rendered project passes quality checks (`make quality`) after implementation
