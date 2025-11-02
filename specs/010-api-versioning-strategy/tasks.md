# Tasks: Comprehensive API Versioning Strategy

**Input**: Design documents from `/specs/010-api-versioning-strategy/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-versioning.openapi.yaml

**Tests**: Tests are NOT explicitly requested in this specification, so test tasks are excluded. Focus is on implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure (API middleware/library):
- `src/api_versioning/` - Source code
- `tests/` - Test files
- `config/` - Configuration files

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure per plan.md: src/api_versioning/{core,middleware,handlers,logging,utils}/, tests/{unit,integration,contract}/, config/
- [ ] T002 Initialize Python project with pyproject.toml including dependencies: pyyaml, asgiref, and optional watchdog
- [ ] T003 [P] Create config/api_versions.yaml.example with sample version configuration structure
- [ ] T004 [P] Setup pytest configuration in pyproject.toml with coverage and asyncio support
- [ ] T005 [P] Create README.md with installation and quick start instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create VersionStatus enum in src/api_versioning/core/version.py with values: CURRENT, DEPRECATED, SUNSET, PRERELEASE
- [ ] T007 Create VersionMetadata dataclass in src/api_versioning/core/version.py with all attributes from data-model.md (frozen=True for immutability)
- [ ] T008 Implement VersionRegistry singleton in src/api_versioning/core/registry.py with load_from_file, get_version, get_current_version, list_all_versions, list_active_versions methods
- [ ] T009 Add YAML configuration loading and validation in VersionRegistry with error handling for malformed configs
- [ ] T010 [P] Create SpecificationSource enum in src/api_versioning/middleware/parser.py with values: HEADER, URL_PATH, QUERY_PARAM, DEFAULT
- [ ] T011 [P] Create VersionSpecification dataclass in src/api_versioning/middleware/parser.py with version_id, source, raw_value, precedence_rank
- [ ] T012 [P] Implement semantic versioning utilities in src/api_versioning/utils/semver.py for version parsing and validation
- [ ] T013 [P] Implement version ID validation in src/api_versioning/utils/validation.py matching pattern ^v[0-9]+(-[a-z]+)?$
- [ ] T014 Create base error classes in src/api_versioning/handlers/error.py: VersionNotFoundError, VersionSunsetError, VersionConflictError, PrereleaseOptInRequiredError

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - API Consumer Discovers Version Support (Priority: P1) 🎯 MVP

**Goal**: Enable consumers to discover available versions, specify desired version via header/URL/query, and receive version information in responses

**Independent Test**: Query /versions endpoint to see all versions, make requests with header/URL/query version specifications, verify correct version served and X-API-Version header present in responses

### Implementation for User Story 1

- [ ] T015 [P] [US1] Implement version extraction from header in src/api_versioning/middleware/parser.py (_from_header method checking X-API-Version and API-Version headers)
- [ ] T016 [P] [US1] Implement version extraction from URL path in src/api_versioning/middleware/parser.py (_from_url method with regex pattern ^/v(\d+)/)
- [ ] T017 [P] [US1] Implement version extraction from query parameter in src/api_versioning/middleware/parser.py (_from_query method parsing version=vN)
- [ ] T018 [US1] Implement version precedence resolution in src/api_versioning/middleware/precedence.py applying Header > URL > Query > Default order
- [ ] T019 [US1] Create APIVersionMiddleware ASGI middleware class in src/api_versioning/middleware/__init__.py with __call__ method extracting version and storing in scope["api_version"]
- [ ] T020 [US1] Add response header injection in APIVersionMiddleware to include X-API-Version header in all responses
- [ ] T021 [US1] Implement default version fallback when no version specified (from VersionRegistry.get_current_version)
- [ ] T022 [P] [US1] Create GET /versions endpoint in src/api_versioning/api/discovery.py returning VersionListResponse with all active versions
- [ ] T023 [P] [US1] Create GET /versions/{version_id} endpoint in src/api_versioning/api/discovery.py returning VersionMetadata for specific version
- [ ] T024 [P] [US1] Create GET /versions/current endpoint in src/api_versioning/api/discovery.py returning current default version metadata
- [ ] T025 [US1] Implement version validation in middleware checking if requested version exists in registry
- [ ] T026 [US1] Return 404 error with available versions list when requested version not found
- [ ] T027 [US1] Add package __init__.py exports in src/api_versioning/__init__.py for public API (VersionRegistry, APIVersionMiddleware, get_version_metadata)

**Checkpoint**: At this point, User Story 1 should be fully functional - consumers can discover versions and specify them in requests

---

## Phase 4: User Story 2 - Breaking Changes Handled Gracefully (Priority: P1)

**Goal**: Support multiple concurrent versions with strict contract isolation, ensuring v1 consumers continue working when v2 with breaking changes is deployed

**Independent Test**: Deploy v1 and v2 handlers with different schemas, send concurrent requests to both versions, verify each gets routed to correct handler without interference

### Implementation for User Story 2

- [ ] T028 [P] [US2] Create VersionRoute dataclass in src/api_versioning/core/router.py with version_id, endpoint_pattern, handler, request_schema, response_schema
- [ ] T029 [US2] Implement version-aware router in src/api_versioning/core/router.py maintaining separate route maps per version
- [ ] T030 [US2] Add route registration method register_route(version_id, endpoint_pattern, handler) ensuring version isolation
- [ ] T031 [US2] Implement route lookup by version in src/api_versioning/core/router.py get_handler(version_id, endpoint_pattern)
- [ ] T032 [US2] Add version-to-handler routing in middleware after version extraction
- [ ] T033 [P] [US2] Create example v1 handler in examples/handlers/users_v1.py demonstrating version 1 contract
- [ ] T034 [P] [US2] Create example v2 handler in examples/handlers/users_v2.py demonstrating breaking changes from v1
- [ ] T035 [US2] Add scope["api_version_metadata"] to middleware storing full VersionMetadata object for handlers to access
- [ ] T036 [US2] Document version-specific handler pattern in quickstart.md with code examples

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - multiple versions can coexist with isolated handlers

---

## Phase 5: User Story 3 - Deprecation Communication and Migration (Priority: P2)

**Goal**: Provide deprecation warnings via response headers, enforce sunset dates, and offer migration guidance to consumers

**Independent Test**: Mark v1 as deprecated in config, send request to v1, verify Deprecation and Sunset headers present with dates and migration guide link

### Implementation for User Story 3

- [ ] T037 [P] [US3] Create DeprecationNotice dataclass in src/api_versioning/handlers/deprecation.py with all attributes from data-model.md
- [ ] T038 [US3] Implement deprecation checking in src/api_versioning/handlers/deprecation.py checking if version.is_deprecated() returns true
- [ ] T039 [US3] Add RFC 8594 Deprecation header injection in middleware when version is deprecated (format: date="YYYY-MM-DD")
- [ ] T040 [US3] Add RFC 8594 Sunset header injection in middleware when version has sunset_date (format: HTTP-date)
- [ ] T041 [US3] Add RFC 8288 Link header with rel="migration-guide" pointing to version.migration_guide_url
- [ ] T042 [US3] Implement sunset enforcement in middleware checking if date.today() > version.sunset_date
- [ ] T043 [US3] Return 410 Gone error when sunset version is requested with VersionSunsetError details
- [ ] T044 [US3] Include recommended_version and migration_guide_url in 410 error response body
- [ ] T045 [P] [US3] Create GET /versions/{version_id}/deprecation endpoint in src/api_versioning/api/discovery.py returning DeprecationNotice
- [ ] T046 [P] [US3] Add days_until_sunset calculation in DeprecationNotice response
- [ ] T047 [US3] Return 404 from deprecation endpoint if version not deprecated

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should work - deprecation warnings communicated, sunset dates enforced

---

## Phase 6: User Story 4 - Version-Specific Feature Discovery (Priority: P2)

**Goal**: Enable consumers to query version metadata and understand feature differences between versions programmatically

**Independent Test**: Query /versions endpoint with include_prerelease=true, verify response includes version status, supported_features, breaking_changes_from, and migration URLs

### Implementation for User Story 4

- [ ] T048 [P] [US4] Add include_sunset query parameter handling to GET /versions endpoint in src/api_versioning/api/discovery.py
- [ ] T049 [P] [US4] Add include_prerelease query parameter handling to GET /versions endpoint
- [ ] T050 [US4] Filter versions by status in list_all_versions based on query parameters (exclude sunset/prerelease by default)
- [ ] T051 [US4] Include supported_features array in VersionMetadata JSON responses
- [ ] T052 [US4] Include breaking_changes_from field in responses indicating which version introduced breaking changes
- [ ] T053 [US4] Include release_date, deprecation_date, sunset_date in ISO 8601 format in all version responses
- [ ] T054 [US4] Add version comparison logic to identify feature differences between versions
- [ ] T055 [P] [US4] Document changelog structure in config/api_versions.yaml showing how to document breaking_changes_summary
- [ ] T056 [US4] Add default_version field to VersionListResponse identifying which version is used when none specified

**Checkpoint**: At this point, all P1-P2 user stories complete - consumers can discover, use, and understand all version capabilities

---

## Phase 7: User Story 5 - Backward-Compatible Enhancements (Priority: P3)

**Goal**: Support adding optional parameters/fields to existing versions without breaking backward compatibility

**Independent Test**: Add optional field to v1 response schema, send v1 request without new parameter, verify old behavior preserved; send request with new parameter, verify new functionality works

### Implementation for User Story 5

- [ ] T057 [P] [US5] Create pre-release version handling in src/api_versioning/handlers/prerelease.py checking opt_in_required flag
- [ ] T058 [US5] Implement opt-in header check (X-API-Prerelease-Opt-In) for pre-release versions
- [ ] T059 [US5] Return 403 Forbidden with PrereleaseOptInRequiredError when pre-release accessed without opt-in
- [ ] T060 [US5] Add X-API-Version-Stability header to responses indicating "stable" or "prerelease"
- [ ] T061 [US5] Document pre-release access pattern in quickstart.md with header example
- [ ] T062 [P] [US5] Create validation logic in src/api_versioning/utils/validation.py for backward-compatible schema changes
- [ ] T063 [US5] Add example of adding optional field to existing version in examples/backward_compatible_change.py

**Checkpoint**: All user stories complete - full versioning system operational with pre-release support

---

## Phase 8: Usage Metrics & Monitoring

**Goal**: Enable tracking of version adoption and deprecation impact through structured logging

- [ ] T064 [P] Create VersionUsageMetric dataclass in src/api_versioning/logging/metrics.py with fields from data-model.md
- [ ] T065 Implement metrics collection in middleware capturing: timestamp, version_id, endpoint_path, http_status, latency_ms, consumer_id, source
- [ ] T066 [P] Add consumer_id extraction from request (API key, OAuth client ID, or IP address fallback)
- [ ] T067 Implement structured JSON logging in src/api_versioning/logging/metrics.py using standard library logging
- [ ] T068 [P] Add is_deprecated_access flag to metrics when deprecated version is used
- [ ] T069 [P] Document metrics format and log aggregation patterns in docs/metrics.md

---

## Phase 9: Error Handling & Edge Cases

**Goal**: Handle all edge cases identified in spec.md with appropriate error responses

- [ ] T070 [P] Implement version conflict detection in src/api_versioning/middleware/precedence.py when contradictory specifications provided
- [ ] T071 Return 400 Bad Request with VersionConflictError when conflict detected, including all detected version specifications in error details
- [ ] T072 [P] Implement version negotiation failure handling when consumer requires unsupported version
- [ ] T073 Return 406 Not Acceptable with list of supported versions when negotiation fails
- [ ] T074 [P] Add version-specific error response handling preserving error schema per version
- [ ] T075 Include X-API-Version header in all error responses for debugging
- [ ] T076 [P] Document error response formats in contracts/api-versioning.openapi.yaml

---

## Phase 10: Hot Reload & Development Tools

**Goal**: Enable development-time configuration hot reload and production graceful restart

- [ ] T077 [P] Implement file watcher in src/api_versioning/utils/reload.py using watchdog library
- [ ] T078 Create ConfigReloadHandler extending FileSystemEventHandler to detect config changes
- [ ] T079 Implement VersionRegistry.reload() method to re-parse and validate configuration file
- [ ] T080 [P] Add start_config_watcher() function for development mode only
- [ ] T081 [P] Document hot reload usage and production restart patterns in quickstart.md

---

## Phase 11: Integration Examples & Documentation

**Goal**: Provide working examples for all major frameworks

- [ ] T082 [P] Create FastAPI integration example in examples/fastapi_app.py with middleware setup
- [ ] T083 [P] Create Starlette integration example in examples/starlette_app.py
- [ ] T084 [P] Create Flask + ASGI adapter example in examples/flask_app.py
- [ ] T085 [P] Create Django ASGI integration example in examples/django_asgi.py
- [ ] T086 [P] Add example version-aware route handlers in examples/versioned_endpoints.py
- [ ] T087 [P] Create migration guide template in docs/migrations/migration_template.md
- [ ] T088 Update quickstart.md with all working examples and error response documentation

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [ ] T089 [P] Add comprehensive docstrings to all public classes and methods following Google style
- [ ] T090 [P] Create type hints for all functions using Python 3.11+ syntax
- [ ] T091 Run ruff linting on entire codebase and fix issues: uv run ruff check src/
- [ ] T092 Run mypy type checking and resolve issues: uv run mypy src/
- [ ] T093 [P] Add py.typed marker file to enable type checking for library consumers
- [ ] T094 Validate against quickstart.md - test all code examples work as documented
- [ ] T095 [P] Add performance benchmark tests in tests/performance/ validating <10ms routing overhead
- [ ] T096 [P] Create CHANGELOG.md documenting versioning system capabilities
- [ ] T097 [P] Add CONTRIBUTING.md with development setup and testing instructions
- [ ] T098 Final review of OpenAPI contract ensuring all endpoints documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - MVP ready after this
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - Can run parallel to US1 if staffed
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) + User Story 1 (needs version routing)
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) + User Story 1 (needs discovery endpoints)
- **User Story 5 (Phase 7)**: Depends on Foundational (Phase 2) + User Story 2 (needs version routing)
- **Metrics (Phase 8)**: Depends on User Story 1 (needs middleware hooks)
- **Error Handling (Phase 9)**: Depends on User Story 1 (needs middleware and routing)
- **Hot Reload (Phase 10)**: Depends on Foundational (Phase 2) - Independent of user stories
- **Examples (Phase 11)**: Depends on all user stories being complete
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - no other story dependencies
- **User Story 2 (P1)**: Foundation only - can run parallel to US1
- **User Story 3 (P2)**: Requires US1 (version routing) - deprecation headers injected after version extraction
- **User Story 4 (P2)**: Requires US1 (discovery API foundation) - extends discovery endpoints
- **User Story 5 (P3)**: Requires US2 (version routing) - pre-release handled by routing logic

### Critical Path (Minimum for MVP)

1. Phase 1: Setup → Phase 2: Foundational → Phase 3: User Story 1
2. **STOP HERE** for MVP - consumers can discover and use versions
3. Add Phase 4 (US2) for multi-version support
4. Add Phase 5 (US3) for deprecation handling

### Parallel Opportunities

**Setup Phase (Phase 1)**: Tasks T003, T004, T005 can run in parallel

**Foundational Phase (Phase 2)**: Tasks T010-T014 can run in parallel after T006-T009 complete

**User Story 1 (Phase 3)**: 
- Tasks T015, T016, T017 can run in parallel (different version extraction methods)
- Tasks T022, T023, T024 can run in parallel (different discovery endpoints)

**User Story 2 (Phase 4)**:
- Tasks T033, T034 can run in parallel (example handlers)

**User Story 3 (Phase 5)**:
- Tasks T037, T045, T046 can run in parallel

**User Story 4 (Phase 6)**:
- Tasks T048, T049, T055 can run in parallel

**User Story 5 (Phase 7)**:
- Tasks T057, T062 can run in parallel

**Multiple User Stories**: After Foundational phase, US1 and US2 can proceed in parallel with separate team members

---

## Parallel Example: User Story 1

```bash
# Launch all version extraction methods together:
Task T015: "Implement version extraction from header in src/api_versioning/middleware/parser.py"
Task T016: "Implement version extraction from URL path in src/api_versioning/middleware/parser.py"  
Task T017: "Implement version extraction from query parameter in src/api_versioning/middleware/parser.py"

# Launch all discovery endpoints together after routing is ready:
Task T022: "Create GET /versions endpoint in src/api_versioning/api/discovery.py"
Task T023: "Create GET /versions/{version_id} endpoint in src/api_versioning/api/discovery.py"
Task T024: "Create GET /versions/current endpoint in src/api_versioning/api/discovery.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (5 tasks, ~1 hour)
2. Complete Phase 2: Foundational (9 tasks, ~3-4 hours)
3. Complete Phase 3: User Story 1 (13 tasks, ~4-6 hours)
4. **STOP and VALIDATE**: Test version discovery, version specification, response headers
5. **MVP READY** - consumers can discover and use API versions
6. Estimated MVP time: 8-11 hours total

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + Core entities → 4-5 hours
2. **MVP** (Phase 3): Add User Story 1 → Version discovery working → 4-6 hours → **DEPLOY**
3. **Multi-Version** (Phase 4): Add User Story 2 → Multiple versions with isolation → 3-4 hours → **DEPLOY**
4. **Deprecation** (Phase 5): Add User Story 3 → Sunset enforcement → 3-4 hours → **DEPLOY**
5. **Discovery** (Phase 6): Add User Story 4 → Feature discovery → 2-3 hours → **DEPLOY**
6. **Pre-release** (Phase 7): Add User Story 5 → Beta versions → 2-3 hours → **DEPLOY**
7. **Complete** (Phases 8-12): Add metrics, examples, polish → 6-8 hours → **FINALIZE**

Total estimated time: 24-32 hours for complete implementation

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

**Team A (Senior)**:
- Phase 3: User Story 1 (version discovery & routing)
- Phase 8: Metrics logging

**Team B (Mid)**:
- Phase 4: User Story 2 (multi-version support)
- Phase 9: Error handling

**Team C (Junior)**:
- Phase 5: User Story 3 (deprecation)
- Phase 11: Examples & documentation

Estimated parallel completion: 12-16 hours with 3 developers

---

## Task Summary

**Total Tasks**: 98
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 9 tasks
- Phase 3 (US1 - P1): 13 tasks ← **MVP**
- Phase 4 (US2 - P1): 9 tasks
- Phase 5 (US3 - P2): 11 tasks
- Phase 6 (US4 - P2): 9 tasks
- Phase 7 (US5 - P3): 7 tasks
- Phase 8 (Metrics): 6 tasks
- Phase 9 (Errors): 7 tasks
- Phase 10 (Reload): 5 tasks
- Phase 11 (Examples): 7 tasks
- Phase 12 (Polish): 10 tasks

**Parallel Tasks**: 39 tasks marked [P] can run in parallel within their phase

**MVP Scope**: 27 tasks (Phase 1 + Phase 2 + Phase 3) = 8-11 hours

---

## Notes

- All tasks follow format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] indicates tasks that can run in parallel (different files, no blocking dependencies)
- [Story] label (US1-US5) maps each task to specific user story for traceability
- Each user story is independently completable and testable
- Stop at any phase checkpoint to validate story independently before proceeding
- Commit after each task or logical group for incremental progress
- Framework: Pure ASGI middleware (framework-agnostic)
- Storage: YAML config + in-memory registry
- Performance target: <10ms routing overhead (expected: 0.1-1ms)
- All file paths are relative to repository root
