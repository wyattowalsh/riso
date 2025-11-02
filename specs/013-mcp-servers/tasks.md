# Tasks: MCP Server Scaffolds

**Input**: Design documents from `/specs/013-mcp-servers/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Template structure initialization and Copier configuration

- [ ] T001 Create MCP template directory structure: `template/files/mcp/python/` and `template/files/mcp/typescript/`
- [ ] T002 Add MCP module configuration to `template/copier.yml` with `mcp_module` and `mcp_language` questions
- [ ] T003 [P] Create Python project structure: src/mcp_server/, tests/unit/, tests/integration/
- [ ] T004 [P] Create TypeScript project structure: src/, tests/unit/, tests/integration/
- [ ] T005 [P] Create shared documentation templates in `template/files/mcp/shared/`: README.md.jinja, CONTRIBUTING.md.jinja
- [ ] T006 Update AGENTS.md with MCP technologies: FastMCP, @modelcontextprotocol/sdk, MCP Inspector, STDIO/HTTP transports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core protocol and transport infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Implement MCPConfiguration entity for Python in `template/files/mcp/python/src/mcp_server/config.py.jinja`
- [ ] T008 Implement MCPConfiguration entity for TypeScript in `template/files/mcp/typescript/src/config.ts.jinja`
- [ ] T009 [P] Create TOML configuration template in `template/files/mcp/python/config.toml.jinja`
- [ ] T010 [P] Create JSON configuration template in `template/files/mcp/typescript/config.json.jinja`
- [ ] T011 Implement MCPTransport abstraction for Python in `template/files/mcp/python/src/mcp_server/transport.py.jinja`
- [ ] T012 Implement MCPTransport abstraction for TypeScript in `template/files/mcp/typescript/src/transport.ts.jinja`
- [ ] T013 [P] Implement STDIO transport for Python in `template/files/mcp/python/src/mcp_server/transports/stdio.py.jinja`
- [ ] T014 [P] Implement STDIO transport for TypeScript in `template/files/mcp/typescript/src/transports/stdio.ts.jinja`
- [ ] T015 Configure Loguru structured logging for Python in `template/files/mcp/python/src/mcp_server/logging.py.jinja`
- [ ] T016 Configure structured logging for TypeScript in `template/files/mcp/typescript/src/logging.ts.jinja`
- [ ] T017 [P] Create error handling utilities for Python in `template/files/mcp/python/src/mcp_server/errors.py.jinja`
- [ ] T018 [P] Create error handling utilities for TypeScript in `template/files/mcp/typescript/src/errors.ts.jinja`
- [ ] T019 Create environment variable loader for Python in `template/files/mcp/python/src/mcp_server/env.py.jinja`
- [ ] T020 Create environment variable loader for TypeScript in `template/files/mcp/typescript/src/env.ts.jinja`
- [ ] T021 [P] Create .env.example template for Python in `template/files/mcp/python/.env.example.jinja`
- [ ] T022 [P] Create .env.example template for TypeScript in `template/files/mcp/typescript/.env.example.jinja`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Bootstrap Python MCP Server (Priority: P1) 🎯 MVP

**Goal**: Enable Python developers to scaffold a complete MCP server with example tool/resource/prompt implementations, achieving working server in <5 minutes

**Independent Test**: Run `copier copy` with Python settings, execute `uv sync && uv run python -m mcp_server`, connect with MCP Inspector, and successfully call echo tool

### Implementation for User Story 1

- [ ] T023 [P] [US1] Implement MCPServer class for Python in `template/files/mcp/python/src/mcp_server/server.py.jinja`
- [ ] T024 [P] [US1] Create MCPTool entity implementation for Python in `template/files/mcp/python/src/mcp_server/tool.py.jinja`
- [ ] T025 [P] [US1] Create MCPResource entity implementation for Python in `template/files/mcp/python/src/mcp_server/resource.py.jinja`
- [ ] T026 [P] [US1] Create MCPPrompt entity implementation for Python in `template/files/mcp/python/src/mcp_server/prompt.py.jinja`
- [ ] T027 [US1] Create example echo tool in `template/files/mcp/python/src/mcp_server/tools.py.jinja`
- [ ] T028 [US1] Create example about resource in `template/files/mcp/python/src/mcp_server/resources.py.jinja`
- [ ] T029 [US1] Create example greeting prompt in `template/files/mcp/python/src/mcp_server/prompts.py.jinja`
- [ ] T030 [US1] Create server entry point with FastMCP integration in `template/files/mcp/python/src/mcp_server/__main__.py.jinja`
- [ ] T031 [US1] Create package __init__.py in `template/files/mcp/python/src/mcp_server/__init__.py.jinja`
- [ ] T032 [US1] Create pyproject.toml template with FastMCP, Loguru, tomli dependencies in `template/files/mcp/python/pyproject.toml.jinja`
- [ ] T033 [P] [US1] Create unit tests for Python tools in `template/files/mcp/python/tests/unit/test_tools.py.jinja`
- [ ] T034 [P] [US1] Create unit tests for Python resources in `template/files/mcp/python/tests/unit/test_resources.py.jinja`
- [ ] T035 [P] [US1] Create unit tests for Python prompts in `template/files/mcp/python/tests/unit/test_prompts.py.jinja`
- [ ] T036 [US1] Create integration test for Python STDIO transport in `template/files/mcp/python/tests/integration/test_stdio.py.jinja`
- [ ] T037 [US1] Create pytest configuration in `template/files/mcp/python/pytest.ini.jinja`
- [ ] T038 [US1] Create conftest.py with test fixtures in `template/files/mcp/python/tests/conftest.py.jinja`
- [ ] T039 [US1] Create Python README with quickstart in `template/files/mcp/python/README.md.jinja`
- [ ] T040 [US1] Create Python Makefile with dev/test/run targets in `template/files/mcp/python/Makefile.jinja`
- [ ] T041 [US1] Add validation script for Python scaffold in `scripts/ci/validate_mcp_python.py`
- [ ] T042 [US1] Create Python sample render in `samples/mcp-servers/python-stdio/`
- [ ] T043 [US1] Validate Python scaffold meets SC-001 (bootstrap <5 min), SC-003 (quality checks pass), SC-004 (>80% coverage)

**Checkpoint**: At this point, User Story 1 should be fully functional - Python developers can scaffold and run MCP servers

---

## Phase 4: User Story 2 - Bootstrap TypeScript MCP Server (Priority: P1)

**Goal**: Enable TypeScript/Node.js developers to scaffold a complete MCP server with type safety and modern ESM syntax, achieving working server in <5 minutes

**Independent Test**: Run `copier copy` with TypeScript settings, execute `pnpm install && pnpm build && pnpm start`, connect with MCP Inspector, verify types and autocomplete

### Implementation for User Story 2

- [ ] T044 [P] [US2] Implement MCPServer class for TypeScript in `template/files/mcp/typescript/src/server.ts.jinja`
- [ ] T045 [P] [US2] Create TypeScript types for MCPTool in `template/files/mcp/typescript/src/types/tool.ts.jinja`
- [ ] T046 [P] [US2] Create TypeScript types for MCPResource in `template/files/mcp/typescript/src/types/resource.ts.jinja`
- [ ] T047 [P] [US2] Create TypeScript types for MCPPrompt in `template/files/mcp/typescript/src/types/prompt.ts.jinja`
- [ ] T048 [P] [US2] Create TypeScript interfaces for MCP protocol in `template/files/mcp/typescript/src/types/protocol.ts.jinja`
- [ ] T049 [US2] Create example echo tool in `template/files/mcp/typescript/src/tools/echo.ts.jinja`
- [ ] T050 [US2] Create example about resource in `template/files/mcp/typescript/src/resources/about.ts.jinja`
- [ ] T051 [US2] Create example greeting prompt in `template/files/mcp/typescript/src/prompts/greeting.ts.jinja`
- [ ] T052 [US2] Create tool registry in `template/files/mcp/typescript/src/tools/index.ts.jinja`
- [ ] T053 [US2] Create resource registry in `template/files/mcp/typescript/src/resources/index.ts.jinja`
- [ ] T054 [US2] Create prompt registry in `template/files/mcp/typescript/src/prompts/index.ts.jinja`
- [ ] T055 [US2] Create server entry point with SDK integration in `template/files/mcp/typescript/src/index.ts.jinja`
- [ ] T056 [US2] Create package.json template with @modelcontextprotocol/sdk, zod dependencies in `template/files/mcp/typescript/package.json.jinja`
- [ ] T057 [US2] Create tsconfig.json with ESM and strict settings in `template/files/mcp/typescript/tsconfig.json.jinja`
- [ ] T058 [US2] Create vitest configuration in `template/files/mcp/typescript/vitest.config.ts.jinja`
- [ ] T059 [P] [US2] Create unit tests for TypeScript tools in `template/files/mcp/typescript/tests/unit/tools.test.ts.jinja`
- [ ] T060 [P] [US2] Create unit tests for TypeScript resources in `template/files/mcp/typescript/tests/unit/resources.test.ts.jinja`
- [ ] T061 [P] [US2] Create unit tests for TypeScript prompts in `template/files/mcp/typescript/tests/unit/prompts.test.ts.jinja`
- [ ] T062 [US2] Create integration test for TypeScript STDIO transport in `template/files/mcp/typescript/tests/integration/stdio.test.ts.jinja`
- [ ] T063 [US2] Create TypeScript README with quickstart in `template/files/mcp/typescript/README.md.jinja`
- [ ] T064 [US2] Create build configuration with tsup in `template/files/mcp/typescript/tsup.config.ts.jinja`
- [ ] T065 [US2] Add npm scripts (dev, build, test, lint) to package.json template
- [ ] T066 [US2] Add validation script for TypeScript scaffold in `scripts/ci/validate_mcp_typescript.py`
- [ ] T067 [US2] Create TypeScript sample render in `samples/mcp-servers/typescript-stdio/`
- [ ] T068 [US2] Validate TypeScript scaffold meets SC-002 (bootstrap <5 min), SC-003 (quality checks pass), SC-004 (>80% coverage)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - both Python and TypeScript developers can scaffold MCP servers

---

## Phase 5: User Story 3 - Production-Ready Configuration (Priority: P2)

**Goal**: Add configuration management, structured logging, error handling, and observability for production deployments

**Independent Test**: Configure custom log levels, timeouts, and limits via config file; trigger errors; verify structured logs with correlation IDs

### Implementation for User Story 3

- [ ] T069 [P] [US3] Add timeout configuration to Python config.toml template (tool: 30s, resource: 10s, prompt: 5s)
- [ ] T070 [P] [US3] Add timeout configuration to TypeScript config.json template
- [ ] T071 [P] [US3] Add response size limits to Python configuration (100MB default)
- [ ] T072 [P] [US3] Add response size limits to TypeScript configuration
- [ ] T073 [US3] Implement timeout enforcement in Python tools/resources/prompts in `template/files/mcp/python/src/mcp_server/timeout.py.jinja`
- [ ] T074 [US3] Implement timeout enforcement in TypeScript tools/resources/prompts in `template/files/mcp/typescript/src/timeout.ts.jinja`
- [ ] T075 [P] [US3] Implement correlation ID generation in Python logging in `template/files/mcp/python/src/mcp_server/correlation.py.jinja`
- [ ] T076 [P] [US3] Implement correlation ID generation in TypeScript logging in `template/files/mcp/typescript/src/correlation.ts.jinja`
- [ ] T077 [US3] Add structured logging examples to Python tools showing context capture
- [ ] T078 [US3] Add structured logging examples to TypeScript tools showing context capture
- [ ] T079 [P] [US3] Create error sanitization utilities for Python in `template/files/mcp/python/src/mcp_server/sanitize.py.jinja`
- [ ] T080 [P] [US3] Create error sanitization utilities for TypeScript in `template/files/mcp/typescript/src/sanitize.ts.jinja`
- [ ] T081 [US3] Add graceful shutdown handling to Python server (SIGTERM/SIGINT)
- [ ] T082 [US3] Add graceful shutdown handling to TypeScript server
- [ ] T083 [P] [US3] Create unit tests for Python timeout enforcement in `template/files/mcp/python/tests/unit/test_timeout.py.jinja`
- [ ] T084 [P] [US3] Create unit tests for TypeScript timeout enforcement in `template/files/mcp/typescript/tests/unit/timeout.test.ts.jinja`
- [ ] T085 [P] [US3] Create unit tests for Python error sanitization in `template/files/mcp/python/tests/unit/test_sanitize.py.jinja`
- [ ] T086 [P] [US3] Create unit tests for TypeScript error sanitization in `template/files/mcp/typescript/tests/unit/sanitize.test.ts.jinja`
- [ ] T087 [US3] Add production configuration examples to Python README
- [ ] T088 [US3] Add production configuration examples to TypeScript README
- [ ] T089 [US3] Validate configuration meets FR-053 (timeouts), FR-055 (error sanitization), FR-057 (graceful shutdown)

**Checkpoint**: At this point, all three user stories should work independently - scaffolds are production-ready with observability

---

## Phase 6: User Story 4 - Comprehensive Documentation (Priority: P2)

**Goal**: Provide complete documentation with examples, best practices, and deployment guides to reduce onboarding time

**Independent Test**: Follow quickstart guide from zero to deployed server, implement each example, verify all code samples work

### Implementation for User Story 4

- [ ] T090 [P] [US4] Create architecture documentation in `template/files/mcp/shared/docs/architecture.md.jinja`
- [ ] T091 [P] [US4] Create tool implementation guide in `template/files/mcp/shared/docs/tools.md.jinja`
- [ ] T092 [P] [US4] Create resource implementation guide in `template/files/mcp/shared/docs/resources.md.jinja`
- [ ] T093 [P] [US4] Create prompt implementation guide in `template/files/mcp/shared/docs/prompts.md.jinja`
- [ ] T094 [US4] Create testing guide in `template/files/mcp/shared/docs/testing.md.jinja`
- [ ] T095 [US4] Create deployment guide for STDIO in `template/files/mcp/shared/docs/deployment-stdio.md.jinja`
- [ ] T096 [US4] Create Claude Desktop integration guide in `template/files/mcp/shared/docs/claude-desktop.md.jinja`
- [ ] T097 [P] [US4] Add complex tool example (fetch_url) to Python tools.py
- [ ] T098 [P] [US4] Add complex tool example (fetch_url) to TypeScript tools
- [ ] T099 [P] [US4] Add dynamic resource example (file browser) to Python resources.py
- [ ] T100 [P] [US4] Add dynamic resource example (file browser) to TypeScript resources
- [ ] T101 [P] [US4] Add multi-turn prompt example to Python prompts.py
- [ ] T102 [P] [US4] Add multi-turn prompt example to TypeScript prompts
- [ ] T103 [US4] Create troubleshooting guide in `template/files/mcp/shared/docs/troubleshooting.md.jinja`
- [ ] T104 [US4] Create best practices guide in `template/files/mcp/shared/docs/best-practices.md.jinja`
- [ ] T105 [US4] Add API reference to Python README linking to contracts/python-mcp-api.md
- [ ] T106 [US4] Add API reference to TypeScript README linking to contracts/typescript-mcp-api.md
- [ ] T107 [US4] Validate documentation meets SC-006 (custom tool in <15 min)

**Checkpoint**: Documentation enables rapid developer onboarding - all examples work as documented

---

## Phase 7: User Story 5 - Advanced MCP Features (Priority: P3)

**Goal**: Provide examples of sophisticated features like pagination, streaming, and multi-step tool chains for advanced use cases

**Independent Test**: Implement paginated resource, streaming tool, and multi-step workflow; verify via MCP Inspector

### Implementation for User Story 5

- [ ] T108 [P] [US5] Create paginated resource example in Python in `template/files/mcp/python/src/mcp_server/examples/paginated_resource.py.jinja`
- [ ] T109 [P] [US5] Create paginated resource example in TypeScript in `template/files/mcp/typescript/src/examples/paginatedResource.ts.jinja`
- [ ] T110 [P] [US5] Create streaming tool example in Python in `template/files/mcp/python/src/mcp_server/examples/streaming_tool.py.jinja`
- [ ] T111 [P] [US5] Create streaming tool example in TypeScript in `template/files/mcp/typescript/src/examples/streamingTool.ts.jinja`
- [ ] T112 [P] [US5] Create multi-step tool chain example in Python in `template/files/mcp/python/src/mcp_server/examples/tool_chain.py.jinja`
- [ ] T113 [P] [US5] Create multi-step tool chain example in TypeScript in `template/files/mcp/typescript/src/examples/toolChain.ts.jinja`
- [ ] T114 [US5] Add pagination utilities to Python in `template/files/mcp/python/src/mcp_server/pagination.py.jinja`
- [ ] T115 [US5] Add pagination utilities to TypeScript in `template/files/mcp/typescript/src/pagination.ts.jinja`
- [ ] T116 [P] [US5] Create unit tests for Python pagination in `template/files/mcp/python/tests/unit/test_pagination.py.jinja`
- [ ] T117 [P] [US5] Create unit tests for TypeScript pagination in `template/files/mcp/typescript/tests/unit/pagination.test.ts.jinja`
- [ ] T118 [US5] Document pagination pattern in advanced features guide in `template/files/mcp/shared/docs/advanced-features.md.jinja`
- [ ] T119 [US5] Document streaming pattern in advanced features guide
- [ ] T120 [US5] Document tool chaining pattern in advanced features guide

**Checkpoint**: Advanced features documented with working examples - enables sophisticated MCP server implementations

---

## Phase 8: User Story 6 - Multiple Transport Support (Priority: P3)

**Goal**: Add HTTP/SSE transport support for cloud-based MCP service deployments accessible to remote clients

**Independent Test**: Start server in HTTP mode, make REST/SSE requests, verify all MCP operations work identically to STDIO

### Implementation for User Story 6

- [ ] T121 [P] [US6] Implement HTTP transport for Python in `template/files/mcp/python/src/mcp_server/transports/http.py.jinja`
- [ ] T122 [P] [US6] Implement HTTP/SSE transport for TypeScript in `template/files/mcp/typescript/src/transports/http.ts.jinja`
- [ ] T123 [P] [US6] Add HTTP transport configuration to Python config.toml (host, port, CORS)
- [ ] T124 [P] [US6] Add HTTP transport configuration to TypeScript config.json
- [ ] T125 [US6] Implement rate limiting for Python HTTP transport in `template/files/mcp/python/src/mcp_server/rate_limit.py.jinja`
- [ ] T126 [US6] Implement rate limiting for TypeScript HTTP transport in `template/files/mcp/typescript/src/rateLimit.ts.jinja`
- [ ] T127 [P] [US6] Add authentication middleware for Python HTTP in `template/files/mcp/python/src/mcp_server/auth.py.jinja`
- [ ] T128 [P] [US6] Add authentication middleware for TypeScript HTTP in `template/files/mcp/typescript/src/auth.ts.jinja`
- [ ] T129 [US6] Create HTTP transport integration tests for Python in `template/files/mcp/python/tests/integration/test_http.py.jinja`
- [ ] T130 [US6] Create HTTP transport integration tests for TypeScript in `template/files/mcp/typescript/tests/integration/http.test.ts.jinja`
- [ ] T131 [P] [US6] Create Python HTTP sample render in `samples/mcp-servers/python-http/`
- [ ] T132 [P] [US6] Create TypeScript HTTP sample render in `samples/mcp-servers/typescript-http/`
- [ ] T133 [US6] Create HTTP deployment guide in `template/files/mcp/shared/docs/deployment-http.md.jinja`
- [ ] T134 [US6] Document rate limiting configuration in deployment guide
- [ ] T135 [US6] Document authentication setup in deployment guide
- [ ] T136 [US6] Validate HTTP transport meets FR-041 (REST endpoints), FR-042 (SSE), FR-044 (auth), FR-054 (rate limiting)
- [ ] T137 [US6] Validate transport abstraction meets SC-008 (config-only switch between STDIO/HTTP)

**Checkpoint**: All six user stories complete - full-featured MCP server scaffolds with both transport options

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T138 [P] Add Python scaffold to quality suite integration in `.github/workflows/riso-quality.yml.jinja`
- [ ] T139 [P] Add TypeScript scaffold to quality suite integration
- [ ] T140 [P] Create Dockerfile template for Python in `template/files/mcp/python/Dockerfile.jinja`
- [ ] T141 [P] Create Dockerfile template for TypeScript in `template/files/mcp/typescript/Dockerfile.jinja`
- [ ] T142 [P] Create docker-compose template for Python in `template/files/mcp/python/docker-compose.yml.jinja`
- [ ] T143 [P] Create docker-compose template for TypeScript in `template/files/mcp/typescript/docker-compose.yml.jinja`
- [ ] T144 Add health check endpoint to Python HTTP transport
- [ ] T145 Add health check endpoint to TypeScript HTTP transport
- [ ] T146 [P] Create Python .gitignore in `template/files/mcp/python/.gitignore.jinja`
- [ ] T147 [P] Create TypeScript .gitignore in `template/files/mcp/typescript/.gitignore.jinja`
- [ ] T148 Create CI validation workflow in `scripts/ci/validate_mcp_scaffolds.py`
- [ ] T149 Add MCP scaffolds to render matrix in `scripts/ci/render_matrix.py`
- [ ] T150 Update module success tracking in `scripts/ci/record_module_success.py`
- [ ] T151 Run full render matrix and validate all samples
- [ ] T152 Run quality suite on all rendered samples (Python and TypeScript)
- [ ] T153 Verify SC-001 through SC-012 success criteria on rendered samples
- [ ] T154 Run quickstart.md validation per contracts
- [ ] T155 Performance testing: Validate SC-007 (100 concurrent requests)
- [ ] T156 Performance testing: Validate bootstrap time SC-001/SC-002 (<5 min)
- [ ] T157 Update NEXT_FEATURES.md removing 013-mcp-servers
- [ ] T158 Final documentation review and polish

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User Story 1 (Python): Can start after Foundational - No dependencies on other stories
  - User Story 2 (TypeScript): Can start after Foundational - No dependencies on other stories
  - User Story 3 (Production Config): Can start after Foundational - Enhances US1 & US2 but independent
  - User Story 4 (Documentation): Can start after US1 & US2 complete - References their implementations
  - User Story 5 (Advanced Features): Can start after US1 & US2 complete - Builds on basic implementations
  - User Story 6 (HTTP Transport): Can start after Foundational - Adds transport option to US1 & US2
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Independence

Each user story (except US4 which documents others) can be:
- Implemented independently after Foundational phase completes
- Tested independently with its own acceptance criteria
- Deployed independently as an MVP increment

### Within Each User Story

- Configuration/types before implementation
- Core entities (server, tool, resource, prompt) before examples
- Examples before tests
- Tests before validation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- **Once Foundational phase completes**:
  - User Story 1 (Python) and User Story 2 (TypeScript) can proceed in parallel
  - User Story 3 (Config) and User Story 6 (HTTP) can proceed in parallel after US1/US2
  - User Story 5 (Advanced) can proceed after US1/US2 complete
- Within each story, all tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (Python Bootstrap)

```bash
# Launch foundational tasks together (after Setup):
Task T007: "MCPConfiguration for Python"
Task T008: "MCPConfiguration for TypeScript"
Task T009: "TOML config template"
Task T010: "JSON config template"
# ... (all [P] tasks in Foundational phase)

# Once Foundational completes, launch User Story 1 parallel tasks:
Task T023: "MCPServer class for Python"
Task T024: "MCPTool entity for Python"
Task T025: "MCPResource entity for Python"
Task T026: "MCPPrompt entity for Python"

# After core entities, launch example implementations:
Task T027: "Echo tool example"
Task T028: "About resource example"
Task T029: "Greeting prompt example"

# After examples, launch all tests in parallel:
Task T033: "Unit tests for Python tools"
Task T034: "Unit tests for Python resources"
Task T035: "Unit tests for Python prompts"
```

---

## Parallel Example: After Foundational Phase Completes

```bash
# Two developers can work in parallel on different languages:
Developer A: User Story 1 (Python) - Tasks T023-T043
Developer B: User Story 2 (TypeScript) - Tasks T044-T068

# Or three developers split user stories:
Developer A: User Story 1 (Python)
Developer B: User Story 2 (TypeScript)
Developer C: User Story 6 (HTTP Transport for both) - Tasks T121-T137
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T022) - **CRITICAL GATE**
3. Complete Phase 3: User Story 1 - Python Bootstrap (T023-T043)
4. Complete Phase 4: User Story 2 - TypeScript Bootstrap (T044-T068)
5. **STOP and VALIDATE**: Test both scaffolds independently, deploy/demo if ready

This delivers a working MVP: developers can scaffold both Python and TypeScript MCP servers in <5 minutes.

### Incremental Delivery

1. **Foundation** (Setup + Foundational) → Core infrastructure ready
2. **MVP Release** (US1 + US2) → Basic scaffolds work, both languages supported
3. **Production Release** (+ US3) → Add config/logging/error handling for production deployments
4. **Documentation Release** (+ US4) → Comprehensive guides reduce onboarding time
5. **Advanced Release** (+ US5) → Sophisticated features for complex use cases
6. **Cloud Release** (+ US6) → HTTP transport enables cloud deployments
7. **Polish** (Phase 9) → Final validation and CI integration

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

- **2 developers**: Split Python (US1) and TypeScript (US2) work
- **3 developers**: Dev A = Python (US1), Dev B = TypeScript (US2), Dev C = HTTP Transport (US6)
- **4+ developers**: Additional devs can work on US3 (Config), US4 (Docs), US5 (Advanced) in parallel

Stories are designed to minimize conflicts and enable independent progress.

---

## Success Criteria Validation Checklist

After implementation, verify all success criteria from spec.md:

- [ ] SC-001: Python bootstrap <5 minutes (measure T001-T043 end-to-end)
- [ ] SC-002: TypeScript bootstrap <5 minutes (measure T001-T006 + T007-T022 + T044-T068)
- [ ] SC-003: Quality checks pass without modification (run ruff/mypy/pylint on Python, eslint/tsc on TypeScript)
- [ ] SC-004: Test coverage >80% (run pytest --cov for Python, vitest --coverage for TypeScript)
- [ ] SC-005: Claude Desktop integration works (test echo tool invocation)
- [ ] SC-006: Custom tool implementation <15 minutes (follow documentation from US4)
- [ ] SC-007: Handle 100 concurrent requests (load test with T155)
- [ ] SC-008: Transport switch config-only (validate with T137)
- [ ] SC-009: Graceful edge case handling (test disconnection, malformed requests, resource exhaustion)
- [ ] SC-010: CI validation <3 minutes (measure T148 workflow time)
- [ ] SC-011: Seamless riso integration (validate quality suite and workflows work)
- [ ] SC-012: >90% developer success rate (post-generation survey after release)

---

## Notes

- **[P] tasks**: Different files, no dependencies within phase - can parallelize
- **[Story] labels**: Map task to specific user story for traceability (US1, US2, US3, US4, US5, US6)
- **Foundational phase is critical**: Must complete before ANY user story work begins
- **User stories are independent**: Each can be completed and tested on its own after Foundational
- **MVP = US1 + US2**: Both Python and TypeScript basic scaffolds working
- **Transport abstraction (FR-045)**: Ensures tool/resource/prompt implementations work with both STDIO and HTTP
- **Dual-language parity**: Python and TypeScript scaffolds should have equivalent functionality
- **Commit strategy**: Commit after each task or logical group
- **Testing**: All scaffolds must pass quality checks and achieve >80% coverage
- **Validation**: Use MCP Inspector and Claude Desktop for end-to-end testing

---

## Total Task Count: 158 tasks

**By Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 16 tasks
- Phase 3 (US1 - Python): 21 tasks
- Phase 4 (US2 - TypeScript): 25 tasks
- Phase 5 (US3 - Config): 21 tasks
- Phase 6 (US4 - Docs): 18 tasks
- Phase 7 (US5 - Advanced): 13 tasks
- Phase 8 (US6 - HTTP): 17 tasks
- Phase 9 (Polish): 21 tasks

**By User Story**:
- US1 (Python Bootstrap): 21 tasks
- US2 (TypeScript Bootstrap): 25 tasks
- US3 (Production Config): 21 tasks
- US4 (Documentation): 18 tasks
- US5 (Advanced Features): 13 tasks
- US6 (HTTP Transport): 17 tasks

**Parallelization**:
- 58 tasks marked [P] for parallel execution
- User Stories 1 & 2 can proceed in parallel after Foundational
- User Stories 3, 5, 6 can start in parallel after US1 & US2
- Within each story, multiple [P] tasks enable concurrent work

**Suggested MVP Scope**: Phases 1-4 (Setup + Foundational + US1 + US2) = 68 tasks
This delivers both Python and TypeScript scaffolds with basic functionality in <5 minutes bootstrap time.
