# Tasks: FastAPI API Scaffold

**Feature**: 001-fastapi-api-scaffold  
**Input**: Design documents from `/specs/001-fastapi-api-scaffold/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included as this is a scaffold feature that requires comprehensive test examples per FR-011.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **Checkbox**: All tasks start with `- [ ]` for tracking
- **[ID]**: Sequential task number (T001, T002, etc.)
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Template structure (this repository):
- `template/files/python/api_fastapi/` - FastAPI Jinja2 templates
- `template/copier.yml` - Template configuration
- `template/hooks/` - Generation hooks
- `docs/modules/` - Module documentation
- `.github/context/` - Extension patterns

Generated project structure (after render):
- `{package_name}/api/` - FastAPI application code
- `tests/api/` - API tests
- `pyproject.toml` - Dependencies
- `.env.example` - Configuration template

---

## Phase 1: Setup (Template Infrastructure)

**Purpose**: Initialize template structure for FastAPI module

- [ ] T001 Create template directory structure at template/files/python/api_fastapi/ with subdirectories: routes/, models/, middleware/, tests/
- [ ] T002 [P] Create __init__.py.jinja templates in template/files/python/api_fastapi/ and all subdirectories
- [ ] T003 [P] Update template/copier.yml with api_tracks prompt configuration (choices: "", "python", "node", "python,node")
- [ ] T004 [P] Create template/prompts/api_tracks.yml.jinja for API framework selection prompt

**Checkpoint**: Template structure initialized - ready for template file creation

---

## Phase 2: Foundational (Core Template Files)

**Purpose**: Create reusable template components that ALL user stories depend on

**⚠️ CRITICAL**: No user story implementation can begin until these templates exist

- [ ] T005 Create template/files/python/api_fastapi/config.py.jinja with Pydantic Settings class (host, port, reload, cors_origins, app_name, version, log_level, environment)
- [ ] T006 Create template/files/python/api_fastapi/models/__init__.py.jinja with model exports
- [ ] T007 [P] Create template/files/python/api_fastapi/models/responses.py.jinja with ErrorResponse model (detail, status_code, request_id fields)
- [ ] T008 [P] Create template/files/python/api_fastapi/middleware/__init__.py.jinja with middleware exports
- [ ] T009 Create template/files/python/api_fastapi/middleware/cors.py.jinja with CORS middleware configuration using settings.cors_origins
- [ ] T010 [P] Create template/files/python/api_fastapi/middleware/errors.py.jinja with global exception handlers (RequestValidationError, HTTPException)
- [ ] T011 Create template/files/python/api_fastapi/tests/conftest.py.jinja with TestClient fixture for API testing
- [ ] T012 Update template/files/shared/pyproject.toml.jinja to add FastAPI dependencies when api_tracks includes python (fastapi>=0.104.0, uvicorn[standard]>=0.24.0, pydantic>=2.0.0, pydantic-settings>=2.0.0, python-dotenv>=1.0.0, httpx>=0.25.0, pytest-asyncio>=0.21.0)
- [ ] T013 Update template/hooks/post_gen_project.py to validate FastAPI module generation and log FastAPI scaffold creation

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Initialize New API Project (Priority: P1) 🎯 MVP

**Goal**: Template users can render a project that includes a functional FastAPI application with standardized directory structure, ready to serve HTTP endpoints

**Independent Test**: Render project with FastAPI enabled, run `uv run uvicorn {package_name}.api.main:app`, make HTTP request to /health/ endpoint, verify 200 response with status="healthy"

### Models for User Story 1

- [ ] T014 [P] [US1] Create template/files/python/api_fastapi/models/responses.py.jinja with HealthResponse model (status, version, timestamp, checks fields)

### Routes for User Story 1

- [ ] T015 [P] [US1] Create template/files/python/api_fastapi/routes/__init__.py.jinja with router exports
- [ ] T016 [US1] Create template/files/python/api_fastapi/routes/health.py.jinja with APIRouter and 3 endpoints: GET /health/ (overall health), GET /health/ready (readiness probe), GET /health/live (liveness probe)

### Application Entry Point for User Story 1

- [ ] T017 [US1] Create template/files/python/api_fastapi/main.py.jinja with FastAPI app initialization, CORS middleware registration, error handler registration, health router registration, and root endpoint (depends on T005, T009, T010, T016)

### Tests for User Story 1

- [ ] T018 [P] [US1] Create template/files/python/api_fastapi/tests/__init__.py.jinja for test package
- [ ] T019 [US1] Create template/files/python/api_fastapi/tests/test_health.py.jinja with tests for all 3 health endpoints (test_health_check, test_readiness_check, test_liveness_check)

### Configuration Files for User Story 1

- [ ] T020 [P] [US1] Create template/files/shared/.env.example.jinja with FastAPI environment variables when api_tracks includes python (HOST, PORT, CORS_ORIGINS, APP_NAME, VERSION, LOG_LEVEL, ENVIRONMENT)

**Checkpoint**: User Story 1 complete - can render functional FastAPI app with health checks

---

## Phase 4: User Story 2 - Add New API Endpoints (Priority: P2)

**Goal**: Developers can add new API endpoints by creating route modules that automatically integrate with the application's routing system

**Independent Test**: Add new route file in routes/ directory, register in main.py, restart application, verify new endpoint is accessible and appears in /docs

### Models for User Story 2

- [ ] T021 [P] [US2] Create template/files/python/api_fastapi/models/requests.py.jinja with ExampleCreateRequest model (name: str with min_length=1, max_length=100; value: int with ge=0; description: Optional[str] with max_length=500; tags: Optional[list[str]] with max_length=10; includes field validators for name whitespace and tag length)
- [ ] T022 [P] [US2] Create template/files/python/api_fastapi/models/requests.py.jinja with ExampleUpdateRequest model (all fields optional: name, value, description, tags)
- [ ] T023 [P] [US2] Add ExampleResponse model to template/files/python/api_fastapi/models/responses.py.jinja (id: str, name: str, value: int, description: Optional[str], tags: list[str], created_at: str, updated_at: str)

### Routes for User Story 2

- [ ] T024 [US2] Create template/files/python/api_fastapi/routes/examples.py.jinja with APIRouter and 5 CRUD endpoints: GET /examples/ (list with pagination), POST /examples/ (create), GET /examples/{example_id} (get one), PUT /examples/{example_id} (update), DELETE /examples/{example_id} (delete); use in-memory dict storage for demo
- [ ] T025 [US2] Update template/files/python/api_fastapi/main.py.jinja to register examples router with app.include_router(examples.router)

### Tests for User Story 2

- [ ] T026 [US2] Create template/files/python/api_fastapi/tests/test_examples.py.jinja with 7 tests: test_list_examples_empty, test_create_example, test_create_example_validation_error, test_get_example, test_get_example_not_found, test_update_example, test_delete_example

**Checkpoint**: User Story 2 complete - example endpoints demonstrate extensibility pattern

---

## Phase 5: User Story 3 - Configure Application Settings (Priority: P3)

**Goal**: Operators can customize application behavior through environment-based configuration without modifying code

**Independent Test**: Create .env file with custom values (PORT=8001, LOG_LEVEL=DEBUG), start application, verify it uses custom port and log level; test with missing required variable, verify clear error message

### Configuration Enhancement for User Story 3

- [ ] T027 [US3] Update template/files/python/api_fastapi/config.py.jinja to add comprehensive docstrings explaining each setting, environment variable mapping, and example values
- [ ] T028 [US3] Update template/files/shared/.env.example.jinja to include detailed comments explaining each variable, valid values, and production vs development recommendations

### Documentation for User Story 3

- [ ] T029 [P] [US3] Create docs/modules/api-fastapi.md.jinja configuration section documenting all environment variables, their defaults, validation rules, and environment-specific best practices
- [ ] T030 [P] [US3] Create .github/context/fastapi-patterns.md with configuration patterns section covering: environment-specific config files, secrets management, feature flags, and deployment configuration

### Validation for User Story 3

- [ ] T031 [US3] Update template/files/python/api_fastapi/config.py.jinja to add custom validation for production environment (e.g., reload must be False, stricter CORS origins)
- [ ] T032 [US3] Add startup logging to template/files/python/api_fastapi/main.py.jinja that logs loaded configuration (sanitized, no secrets) for debugging

**Checkpoint**: User Story 3 complete - configuration is flexible and well-documented

---

## Phase 6: User Story 4 - Access API Documentation (Priority: P2)

**Goal**: Developers and API consumers can view interactive API documentation that is automatically generated from the code

**Independent Test**: Start application, navigate to http://localhost:8000/docs, verify all endpoints are listed with parameters and schemas; use "Try it out" to test an endpoint; navigate to http://localhost:8000/redoc for alternative documentation view

### Documentation Enhancement for User Story 4

- [ ] T033 [US4] Update template/files/python/api_fastapi/main.py.jinja to customize FastAPI app initialization with enhanced OpenAPI metadata (title from settings.app_name, description, version from settings.version, openapi_tags with descriptions for each tag)
- [ ] T034 [P] [US4] Update template/files/python/api_fastapi/routes/health.py.jinja to add comprehensive docstrings to all route handlers with parameter descriptions and response examples
- [ ] T035 [P] [US4] Update template/files/python/api_fastapi/routes/examples.py.jinja to add comprehensive docstrings to all route handlers, use Pydantic Field() descriptions in models, and add response_model annotations
- [ ] T036 [P] [US4] Update template/files/python/api_fastapi/models/requests.py.jinja to enhance Field() definitions with detailed descriptions and example values for OpenAPI schema generation
- [ ] T037 [P] [US4] Update template/files/python/api_fastapi/models/responses.py.jinja to add Field() descriptions and example values to all response models

### Documentation Files for User Story 4

- [ ] T038 [P] [US4] Create docs/modules/api-fastapi.md.jinja documentation section covering: accessing /docs and /redoc, understanding OpenAPI schema, testing endpoints interactively, downloading openapi.json for client generation
- [ ] T039 [P] [US4] Update .github/context/fastapi-patterns.md to add documentation patterns: adding custom examples, versioning APIs, organizing tags, customizing schemas

### Verification for User Story 4

- [ ] T040 [US4] Add root endpoint test to template/files/python/api_fastapi/tests/test_health.py.jinja that verifies / endpoint returns welcome message with docs URL

**Checkpoint**: User Story 4 complete - comprehensive auto-generated documentation is accessible

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize the feature

### Documentation

- [ ] T041 [P] Create comprehensive docs/modules/api-fastapi.md.jinja with sections: Overview, Quick Start, Project Structure, Adding Endpoints, Configuration, Testing, Deployment, Troubleshooting, Performance Considerations
- [ ] T042 [P] Complete .github/context/fastapi-patterns.md with advanced patterns: authentication/authorization, database integration, background tasks, WebSockets, caching, rate limiting
- [ ] T043 [P] Update docs/quickstart.md.jinja to add FastAPI-specific commands when api_tracks includes python (starting server, running tests, accessing docs)
- [ ] T044 [P] Create template/files/python/api_fastapi/README.md.jinja as in-project quickstart guide with essential commands and links to full documentation

### Container Support

- [ ] T045 [P] Update template/files/shared/Dockerfile.jinja to add FastAPI-specific stage when api_tracks includes python (multi-stage build, uv sync --extra api, expose 8000, healthcheck using /health/, CMD with uvicorn)
- [ ] T046 [P] Update template/files/shared/docker-compose.yml.jinja to add FastAPI service when api_tracks includes python (ports 8000:8000, environment variables, depends_on if other services exist, healthcheck)

### Quality Integration

- [ ] T047 Update template/files/shared/pyproject.toml.jinja to ensure FastAPI code is included in quality tool configurations (ruff, mypy, pylint paths include {package_name}/api/)
- [ ] T048 Update template/files/shared/pytest.ini.jinja to include tests/api/ directory in test discovery when api_tracks includes python
- [ ] T049 Create template/files/shared/.coveragerc.jinja section for API code coverage reporting when api_tracks includes python

### Sample Project

- [ ] T050 Create samples/api-python/copier-answers.yml with FastAPI enabled (api_tracks: python, project_name: riso-api-sample, package_name: riso_api)
- [ ] T051 Create samples/api-python/metadata.json documenting sample configuration
- [ ] T052 Update samples/full-stack/copier-answers.yml to include FastAPI (api_tracks: python,node)

### Module Tracking

- [ ] T053 Update template/files/shared/module_catalog.json.jinja to add FastAPI module entry (name, description, dependencies, compatibility, activation prompt)
- [ ] T054 Update scripts/ci/record_module_success.py to track FastAPI module in samples/metadata/module_success.json

### Validation & Testing

- [ ] T055 Run scripts/render-samples.sh --variant api-python to generate sample with FastAPI enabled
- [ ] T056 Validate rendered sample: cd samples/api-python/render && uv sync --extra api && uv run uvicorn {package_name}.api.main:app (verify starts in <3s)
- [ ] T057 Test health endpoints: curl http://localhost:8000/health/ (verify response in <100ms)
- [ ] T058 Test example endpoints: curl -X POST http://localhost:8000/examples/ -H "Content-Type: application/json" -d '{"name":"Test","value":42}' (verify 201 response)
- [ ] T059 Test documentation: open http://localhost:8000/docs (verify all endpoints listed, try interactive testing)
- [ ] T060 Run quality checks: cd samples/api-python/render && QUALITY_PROFILE=standard uv run task quality (verify all pass)
- [ ] T061 Run tests with coverage: cd samples/api-python/render && uv run pytest tests/api/ --cov={package_name}.api --cov-report=term-missing (verify ≥80% coverage)
- [ ] T062 Validate success criteria from spec.md (SC-001 through SC-009) using metrics in samples/api-python/baseline_quickstart_metrics.json
- [ ] T063 Run scripts/ci/validate_workflows.py to ensure FastAPI module works with existing CI workflows
- [ ] T064 Execute quickstart commands from specs/001-fastapi-api-scaffold/quickstart.md to verify all steps work correctly

**Checkpoint**: All polish tasks complete - feature ready for integration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) and User Story 1 (Phase 3) for main.py integration
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - Can run in parallel with US2/US4
- **User Story 4 (Phase 6)**: Depends on User Story 1 (Phase 3) and User Story 2 (Phase 4) for endpoints to document
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation → US1 ✓ (Independent after foundation)
- **User Story 2 (P2)**: Foundation → US1 → US2 (Needs main.py from US1)
- **User Story 3 (P3)**: Foundation → US3 ✓ (Independent, parallel with US2)
- **User Story 4 (P2)**: Foundation → US1 → US2 → US4 (Needs endpoints to document)

### Within Each User Story

1. Models before routes (data structures needed for handlers)
2. Routes before tests (implementation before verification)
3. Core functionality before documentation
4. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup) - Parallel Tasks**:
- T002 (init files), T003 (copier.yml), T004 (prompts) can run in parallel

**Phase 2 (Foundational) - Parallel Tasks**:
- T007 (responses.py), T008 (middleware init), T009 (CORS), T010 (errors) can run in parallel after T005/T006
- T012 (pyproject.toml), T013 (hooks) can run in parallel

**Phase 3 (US1) - Parallel Tasks**:
- T014 (HealthResponse), T015 (routes init) can run in parallel
- T018 (test init), T019 (test_health), T020 (.env.example) can run in parallel after T016/T017

**Phase 4 (US2) - Parallel Tasks**:
- T021, T022, T023 (all models) can run in parallel
- T026 (tests) can run after T024/T025

**Phase 5 (US3) - Parallel Tasks**:
- T029, T030 (documentation) can run in parallel

**Phase 6 (US4) - Parallel Tasks**:
- T034, T035, T036, T037 (all docstring updates) can run in parallel
- T038, T039 (documentation) can run in parallel

**Phase 7 (Polish) - Parallel Tasks**:
- T041, T042, T043, T044 (all documentation) can run in parallel
- T045, T046 (container files) can run in parallel
- T047, T048, T049 (quality configs) can run in parallel
- T050, T051, T052 (sample files) can run in parallel
- T053, T054 (module tracking) can run in parallel

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes:

# Step 1: Create models in parallel
Task T014: "Create HealthResponse model"

# Step 2: Create routes in parallel  
Task T015: "Create routes __init__.py"
Task T016: "Create health routes"

# Step 3: Create main app (depends on T016)
Task T017: "Create main.py"

# Step 4: Create tests and config in parallel
Task T018: "Create tests __init__.py"
Task T019: "Create test_health.py"
Task T020: "Create .env.example"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T013) **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T014-T020)
4. **STOP and VALIDATE**: 
   - Render sample: `./scripts/render-samples.sh --variant api-python`
   - Start server: `uv run uvicorn {package_name}.api.main:app`
   - Test health: `curl http://localhost:8000/health/`
   - Run tests: `uv run pytest tests/api/`
5. **MVP COMPLETE**: Working FastAPI scaffold with health checks

### Incremental Delivery

1. **Foundation** (T001-T013) → Template structure ready
2. **+User Story 1** (T014-T020) → Working API with health checks (MVP! 🎯)
3. **+User Story 2** (T021-T026) → Extensibility with example CRUD
4. **+User Story 3** (T027-T032) → Flexible configuration
5. **+User Story 4** (T033-T040) → Comprehensive documentation
6. **+Polish** (T041-T064) → Production-ready feature

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers (after Foundational phase):

- **Developer A**: User Story 1 (T014-T020) - Core API
- **Developer B**: User Story 3 (T027-T032) - Configuration (parallel with A)
- **Developer C**: After US1 completes → User Story 2 (T021-T026)
- **Developer D**: After US1+US2 complete → User Story 4 (T033-T040)

---

## Success Criteria Validation

Map tasks to success criteria from spec.md:

- **SC-001** (Render in <2 min): Validated by T055, T056
- **SC-002** (Pass quality checks): Validated by T060
- **SC-003** (Auto documentation): Validated by T059
- **SC-004** (Add endpoint <5 min): Validated by T024 example pattern
- **SC-005** (Startup <3s): Validated by T056
- **SC-006** (Example endpoints work): Validated by T058
- **SC-007** (Health <100ms): Validated by T057
- **SC-008** (≥80% coverage): Validated by T061
- **SC-009** (100 concurrent requests): Validated by T062

---

## Task Summary

- **Total Tasks**: 64
- **Setup Phase**: 4 tasks
- **Foundational Phase**: 9 tasks
- **User Story 1 (P1)**: 7 tasks
- **User Story 2 (P2)**: 6 tasks
- **User Story 3 (P3)**: 6 tasks
- **User Story 4 (P2)**: 8 tasks
- **Polish Phase**: 24 tasks

**Parallel Opportunities**: 32 tasks marked [P] can run in parallel with other tasks
**MVP Scope**: Phases 1-3 (Tasks T001-T020) = 20 tasks for working API

---

## Notes

- All tasks follow checklist format: `- [ ] [ID] [P?] [Story] Description with path`
- [P] tasks work on different files with no cross-dependencies
- [Story] labels (US1-US4) map to user stories from spec.md for traceability
- Each user story is independently testable after its phase completes
- Template files use .jinja extension for Copier template processing
- Generated code must pass quality checks without modification (FR-012)
- Commit after each task or logical group
- Stop at checkpoints to validate story independence
- Follow constitutional principles: template sovereignty, deterministic generation, minimal baseline, documented scaffolds, automation governance
