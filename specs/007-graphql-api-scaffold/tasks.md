# Tasks: GraphQL API Scaffold (Strawberry)

**Input**: Design documents from `/specs/007-graphql-api-scaffold/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/schema.graphql

**Tests**: Tests are included per specification requirements for GraphQL API validation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Riso template structure:

- **Template files**: `template/files/python/graphql_api/`
- **Shared files**: `template/files/shared/graphql/`
- **Test templates**: `template/files/tests/graphql/`
- **Documentation**: `docs/modules/`
- **CI scripts**: `scripts/ci/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Template structure and module scaffolding

- [ ] T001 Create template directory structure at template/files/python/graphql_api/
- [ ] T002 Create shared graphql directory at template/files/shared/graphql/
- [ ] T003 [P] Create test templates directory at template/files/tests/graphql/
- [ ] T004 [P] Add graphql_api_module option to template/copier.yml
- [ ] T005 [P] Create module documentation structure at docs/modules/graphql.md.jinja

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core GraphQL infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create GraphQL context module at template/files/python/graphql_api/context.py.jinja
- [ ] T007 Create base schema module at template/files/python/graphql_api/schema.py.jinja
- [ ] T008 [P] Create FastAPI integration at template/files/python/graphql_api/main.py.jinja
- [ ] T009 [P] Create configuration file at template/files/shared/graphql/config.toml.jinja
- [ ] T010 [P] Create `__init__` modules for graphql_api package structure
- [ ] T011 Create error handling utilities at template/files/python/graphql_api/errors.py.jinja
- [ ] T012 [P] Add Strawberry and FastAPI dependencies to template pyproject.toml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Query Data with Flexible Fields (Priority: P1) 🎯 MVP

**Goal**: Enable flexible field selection in GraphQL queries with example User and Post types

**Independent Test**: Create User type with multiple fields, query with different field selections, verify only requested fields returned

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Create query test template at template/files/tests/graphql/test_queries.py.jinja
- [ ] T014 [P] [US1] Add field selection test scenarios for User type queries

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create types directory at template/files/python/graphql_api/types/
- [ ] T016 [P] [US1] Create User type at template/files/python/graphql_api/types/user.py.jinja
- [ ] T017 [P] [US1] Create Post type at template/files/python/graphql_api/types/post.py.jinja
- [ ] T018 [P] [US1] Create types `__init__` module at template/files/python/graphql_api/types/`__init__`.py.jinja
- [ ] T019 [P] [US1] Create queries directory at template/files/python/graphql_api/queries/
- [ ] T020 [US1] Implement user queries resolver at template/files/python/graphql_api/queries/user_queries.py.jinja
- [ ] T021 [US1] Create queries `__init__` module at template/files/python/graphql_api/queries/`__init__`.py.jinja
- [ ] T022 [US1] Wire User queries into root Query type in schema.py.jinja
- [ ] T023 [US1] Add example resolver implementations with flexible field handling
- [ ] T024 [US1] Document field selection in docs/modules/graphql.md.jinja

**Checkpoint**: At this point, User Story 1 should be fully functional - basic GraphQL queries with flexible fields work

---

## Phase 4: User Story 2 - Interactive Playground (Priority: P1)

**Goal**: Provide GraphQL playground for schema exploration and query testing

**Independent Test**: Access playground URL, view schema docs, execute test query successfully

### Tests for User Story 2

- [ ] T025 [P] [US2] Create playground integration test at template/files/tests/graphql/test_playground.py.jinja
- [ ] T026 [P] [US2] Add schema introspection test scenarios

### Implementation for User Story 2

- [ ] T027 [US2] Enable GraphQL playground in main.py.jinja (GraphiQL/Strawberry default)
- [ ] T028 [US2] Configure playground endpoint and settings in config.toml.jinja
- [ ] T029 [US2] Add schema documentation strings to all types and fields
- [ ] T030 [US2] Configure introspection query support in schema.py.jinja
- [ ] T031 [US2] Add playground usage examples to docs/modules/graphql.md.jinja
- [ ] T032 [US2] Document playground URL and features in quickstart

**Checkpoint**: Developers can now explore API via playground - US1 queries testable through UI

---

## Phase 5: User Story 3 - DataLoader Optimization (Priority: P2)

**Goal**: Implement DataLoader batching to prevent N+1 query problems

**Independent Test**: Query list with nested resources, monitor DB queries, verify batching (2 queries not N+1)

### Tests for User Story 3

- [ ] T033 [P] [US3] Create DataLoader test template at template/files/tests/graphql/test_dataloaders.py.jinja
- [ ] T034 [P] [US3] Add N+1 prevention test scenarios with query counting (assert query reduction from N+1 queries to 2 queries, e.g., 11→2 = 82% reduction, meeting SC-003 80% threshold)

### Implementation for User Story 3

- [ ] T035 [P] [US3] Create DataLoader base implementation at template/files/python/graphql_api/dataloaders.py.jinja
- [ ] T036 [US3] Implement user DataLoader with batching function
- [ ] T037 [US3] Implement posts-by-author DataLoader with batching
- [ ] T038 [US3] Integrate DataLoaders into GraphQL context (context.py.jinja)
- [ ] T039 [US3] Update User type resolver to use DataLoader for posts field
- [ ] T040 [US3] Add DataLoader configuration options to config.toml.jinja
- [ ] T041 [US3] Document DataLoader patterns in docs/modules/graphql.md.jinja
- [ ] T042 [US3] Add DataLoader usage examples to quickstart

**Checkpoint**: N+1 queries eliminated - performance optimized for nested queries

---

## Phase 6: User Story 4 - Mutations (Priority: P2)

**Goal**: Enable data modification through GraphQL mutations (create, update, delete)

**Independent Test**: Execute createUser mutation, verify creation in data store, confirm response fields

### Tests for User Story 4

- [ ] T043 [P] [US4] Create mutations test template at template/files/tests/graphql/test_mutations.py.jinja
- [ ] T044 [P] [US4] Add create/update/delete test scenarios for User mutations

### Implementation for User Story 4

- [ ] T045 [P] [US4] Create mutations directory at template/files/python/graphql_api/mutations/
- [ ] T046 [P] [US4] Define input types (CreateUserInput, UpdateUserInput) in types/user.py.jinja
- [ ] T047 [US4] Implement createUser mutation at template/files/python/graphql_api/mutations/user_mutations.py.jinja
- [ ] T048 [US4] Implement updateUser mutation in user_mutations.py.jinja
- [ ] T049 [US4] Implement deleteUser mutation in user_mutations.py.jinja
- [ ] T050 [US4] Create mutations `__init__` module at template/files/python/graphql_api/mutations/`__init__`.py.jinja
- [ ] T051 [US4] Wire mutations into root Mutation type in schema.py.jinja
- [ ] T052 [US4] Add input validation with pydantic in mutations
- [ ] T053 [US4] Document mutation patterns in docs/modules/graphql.md.jinja

**Checkpoint**: Full CRUD operations available - API supports both read and write operations

---

## Phase 7: User Story 6 - Error Handling (Priority: P2)

**Goal**: Provide clear, actionable error messages for validation, auth, and system failures

**Independent Test**: Send invalid queries, verify clear error messages with helpful context

### Tests for User Story 6

- [ ] T054 [P] [US6] Create error handling test at template/files/tests/graphql/test_errors.py.jinja
- [ ] T055 [P] [US6] Add test scenarios for validation, auth, and system errors

### Implementation for User Story 6

- [ ] T056 [P] [US6] Create custom error classes in errors.py.jinja covering all error scenarios: ValidationError (field validation, type mismatches), AuthError (authentication failures, permission denials), SystemError (database errors, network failures, external service errors), QueryError (syntax errors, invalid fields, depth/complexity violations)
- [ ] T057 [US6] Implement error formatter for GraphQL responses
- [ ] T058 [US6] Add field-level validation error handling in mutations
- [ ] T059 [US6] Configure error sanitization for production (no stack traces)
- [ ] T060 [US6] Add error handling middleware to FastAPI integration
- [ ] T061 [US6] Document error patterns and examples in docs/modules/graphql.md.jinja

**Checkpoint**: Clear error messages improve developer experience significantly

---

## Phase 8: User Story 5 - Real-time Subscriptions (Priority: P3)

**Goal**: Enable WebSocket subscriptions for real-time data updates

**Independent Test**: Establish subscription, trigger event, verify client receives update message

### Tests for User Story 5

- [ ] T062 [P] [US5] Create subscriptions test template at template/files/tests/graphql/test_subscriptions.py.jinja
- [ ] T063 [P] [US5] Add WebSocket connection and event delivery test scenarios

### Implementation for User Story 5

- [ ] T064 [P] [US5] Create subscriptions directory at template/files/python/graphql_api/subscriptions/
- [ ] T065 [US5] Implement userCreated subscription at template/files/python/graphql_api/subscriptions/user_subscriptions.py.jinja
- [ ] T066 [US5] Create subscriptions `__init__` module at template/files/python/graphql_api/subscriptions/`__init__`.py.jinja
- [ ] T067 [US5] Wire subscriptions into root Subscription type in schema.py.jinja
- [ ] T068 [US5] Configure WebSocket support in main.py.jinja
- [ ] T069 [US5] Implement event broadcasting mechanism (in-memory or Redis)
- [ ] T070 [US5] Add subscription cleanup on disconnect
- [ ] T071 [US5] Document subscription patterns in docs/modules/graphql.md.jinja

**Checkpoint**: Real-time features enabled - API supports live updates via WebSocket

---

## Phase 9: Security & Performance Controls

**Purpose**: Query depth limiting, complexity analysis, authentication, pagination

### Authentication (FR-016)

- [ ] T072 [P] Create auth module at template/files/python/graphql_api/auth.py.jinja
- [ ] T073 [P] Implement @auth decorator for per-field authentication
- [ ] T074 [P] Add authentication test at template/files/tests/graphql/test_auth.py.jinja
- [ ] T075 Integrate auth into context with user identity injection
- [ ] T076 Apply @auth decorator to mutations in user_mutations.py.jinja
- [ ] T077 Document authentication patterns in docs/modules/graphql.md.jinja

### Query Complexity & Depth (FR-008, FR-009)

- [ ] T078 [P] Create complexity module at template/files/python/graphql_api/complexity.py.jinja
- [ ] T079 [P] Implement depth validation (max 15 levels)
- [ ] T080 [P] Implement complexity scoring (max 5000 points)
- [ ] T081 [P] Add complexity test at template/files/tests/graphql/test_complexity.py.jinja
- [ ] T082 Integrate validation into schema execution in main.py.jinja
- [ ] T083 Configure thresholds in config.toml.jinja (depth: 15, complexity: 5000)
- [ ] T084 Document security controls in docs/modules/graphql.md.jinja

### Pagination (FR-017, FR-018)

- [ ] T085 [P] Create pagination module at template/files/python/graphql_api/pagination.py.jinja
- [ ] T086 [P] Implement cursor-based pagination (Relay Connection pattern)
- [ ] T087 [P] Implement offset-based pagination helpers
- [ ] T088 Add Connection and Edge types to types module
- [ ] T089 Update user queries to support both pagination modes
- [ ] T090 Configure pagination defaults in config.toml.jinja (default: 20, max: 100)
- [ ] T091 Document pagination patterns in docs/modules/graphql.md.jinja

**Checkpoint**: Security and performance controls in place - production-ready API

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories, documentation, CI/CD

- [ ] T092 [P] Create CI schema validation script at scripts/ci/validate_graphql_schemas.py
- [ ] T093 [P] Add GitHub Actions workflow for GraphQL schema validation
- [ ] T094 [P] Create comprehensive module documentation at docs/modules/graphql.md.jinja
- [ ] T095 [P] Add quickstart guide updates with all features
- [ ] T096 [P] Create example queries and mutations in documentation
- [ ] T097 [P] Add Docker Compose service definition for GraphQL API
- [ ] T098 [P] Configure GraphQL-specific linting rules (schema validation)
- [ ] T099 [P] Add performance benchmarking examples
- [ ] T100 [P] Create migration guide from REST to GraphQL
- [ ] T101 Validate all acceptance scenarios from spec.md
- [ ] T102 Run quickstart.md end-to-end validation
- [ ] T103 Generate sample project with graphql_api_module=enabled
- [ ] T104 Test sample project with all user stories
- [ ] T105 [P] Create concurrent query load test (100 simultaneous requests, assert <100ms p95 latency, zero errors) for SC-008
- [ ] T106 [P] Create subscription latency benchmark test (emit event, measure delivery time, assert <100ms) for SC-006
- [ ] T107 [P] Create pagination consistency test (query same dataset with cursor and offset, assert identical results) for SC-009

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Queries): Can start after Foundational - **MVP target**
  - US2 (Playground): Can start after Foundational, enhances US1
  - US3 (DataLoaders): Can start after US1 (needs queries to optimize)
  - US4 (Mutations): Can start after US1 (needs types), independent of US3
  - US6 (Errors): Can start after US1 (needs queries/mutations to handle errors)
  - US5 (Subscriptions): Can start after Foundational, independent of others
- **Security & Performance (Phase 9)**: Can start after Foundational, recommended after US1-US4
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1 - Queries)**: No story dependencies - can start after Foundational
- **US2 (P1 - Playground)**: No story dependencies - enhances US1 but independent
- **US3 (P2 - DataLoaders)**: Requires US1 types/queries to exist
- **US4 (P2 - Mutations)**: Requires US1 types but independent of US2/US3
- **US6 (P2 - Errors)**: Works with US1/US4 but can be implemented independently
- **US5 (P3 - Subscriptions)**: Independent - can be implemented anytime after Foundational

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Types before queries/mutations
- Queries/Mutations before integration
- Core implementation before documentation
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks can run in parallel (T003, T004, T005)

**Phase 2 (Foundational)**: These can run in parallel:

- T008 (FastAPI integration)
- T009 (Configuration)
- T010 (Init modules)
- T011 (Error utilities)
- T012 (Dependencies)

**Phase 3 (US1)**: These can run in parallel after tests:

- T016 (User type)
- T017 (Post type)
- T018 (Types init)

**Phase 4 (US2)**: All tasks can overlap with other stories once US1 types exist

**Cross-Story Parallelization** (if team capacity allows):

- Once Foundational completes, US1 and US2 can proceed in parallel
- Once US1 completes, US3, US4, US6 can all proceed in parallel
- US5 can proceed in parallel with any other story

---

## Parallel Example: Multiple Stories

```bash
# After Foundational Phase completes, launch multiple stories:

Team Member A:
- Phase 3 (US1): Implement basic queries with types

Team Member B:
- Phase 4 (US2): Setup playground while US1 types are being created

Team Member C:
- Phase 7 (US6): Implement error handling framework

# Once US1 completes, expand parallelization:

Team Member A:
- Phase 5 (US3): Add DataLoaders to optimize US1 queries

Team Member B:
- Phase 6 (US4): Implement mutations using US1 types

Team Member C:
- Phase 8 (US5): Implement subscriptions independently
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (5 tasks)
2. Complete Phase 2: Foundational (7 tasks) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 - Queries (12 tasks)
4. Complete Phase 4: User Story 2 - Playground (8 tasks)
5. **STOP and VALIDATE**: Test basic GraphQL queries via playground
6. Deploy/demo MVP - developers can query data with flexible fields

### Incremental Delivery

1. **Foundation**: Setup + Foundational → Template structure ready (12 tasks)
2. **MVP**: Add US1 + US2 → Basic GraphQL API with playground (20 tasks) → Deploy/Demo
3. **Performance**: Add US3 → DataLoader optimization (10 tasks) → Deploy/Demo
4. **Full CRUD**: Add US4 → Mutations enabled (11 tasks) → Deploy/Demo
5. **Robustness**: Add US6 → Error handling (8 tasks) → Deploy/Demo
6. **Real-time**: Add US5 → Subscriptions (10 tasks) → Deploy/Demo
7. **Production**: Add Phase 9 → Security controls (21 tasks) → Deploy/Demo
8. **Polish**: Add Phase 10 → Documentation, CI/CD (13 tasks) → Final Release

### Parallel Team Strategy

With 3 developers:

1. **Together**: Complete Setup + Foundational (Phases 1-2, 12 tasks)
2. **Parallel** (after Foundational):
   - Developer A: US1 Queries
   - Developer B: US2 Playground
   - Developer C: US6 Error Handling (prep for future integration)
3. **Parallel** (after US1):
   - Developer A: US3 DataLoaders
   - Developer B: US4 Mutations
   - Developer C: US5 Subscriptions
4. **Together**: Phase 9 Security & Phase 10 Polish

---

## Task Summary

- **Total Tasks**: 107
- **Setup Phase**: 5 tasks
- **Foundational Phase**: 7 tasks (BLOCKS all stories)
- **US1 (P1 - Queries)**: 12 tasks - MVP CORE
- **US2 (P1 - Playground)**: 8 tasks - MVP UX
- **US3 (P2 - DataLoaders)**: 10 tasks
- **US4 (P2 - Mutations)**: 11 tasks
- **US6 (P2 - Errors)**: 8 tasks
- **US5 (P3 - Subscriptions)**: 10 tasks
- **Security & Performance**: 21 tasks
- **Polish**: 16 tasks (includes 3 new performance validation tasks)

**MVP Scope** (Recommended for first release):

- Setup + Foundational + US1 + US2 = 32 tasks
- Delivers: Basic GraphQL API with flexible queries and interactive playground
- Time estimate: 1-2 weeks for solo developer, 3-5 days with team

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are written FIRST and must FAIL before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- File paths follow Riso template Jinja structure
- All GraphQL code goes in template/files/python/graphql_api/
- Tests go in template/files/tests/graphql/
- This is a TEMPLATE - files are Jinja2 templates (.jinja extension)
