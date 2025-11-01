# Implementation Plan: FastAPI API Scaffold

**Branch**: `001-fastapi-api-scaffold` | **Date**: November 1, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fastapi-api-scaffold/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a Copier template module that generates FastAPI applications with standardized project structure, modular routing, environment-based configuration, and automatic OpenAPI documentation. The scaffold integrates with existing Riso quality tools (ruff, mypy, pylint, pytest) and supports containerization. Template users can render production-ready API servers in under 2 minutes with clear extensibility patterns for adding endpoints.

## Technical Context

**Language/Version**: Python 3.11+ (managed by uv, matching Riso baseline)  
**Primary Dependencies**: FastAPI 0.104+, Uvicorn (ASGI server), Pydantic 2.x (validation), python-dotenv (config)  
**Storage**: N/A (scaffold does not include database integration)  
**Testing**: pytest with httpx (FastAPI test client), pytest-asyncio for async tests  
**Target Platform**: Cross-platform (Linux/macOS/Windows), containerized deployment via Docker  
**Project Type**: Web backend (API server) - single project structure within template  
**Performance Goals**: <3s startup time, <100ms health check response, handles 100 concurrent requests in local dev  
**Constraints**: Zero production dependencies beyond FastAPI ecosystem, integrates with existing Riso quality suite  
**Scale/Scope**: Scaffold supports small-to-medium APIs (dozens of endpoints), extensible to larger applications

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Template Sovereignty ✓

- **Compliance**: All FastAPI scaffold files will live in `template/files/python/api_fastapi/` as Jinja2 templates
- **Evidence**: New copier.yml prompts will control FastAPI generation (e.g., `api_tracks` includes `python`)
- **Shared Context**: Will add `.github/context/fastapi-patterns.md` synchronized with template documentation
- **Proof**: Sample renders will be regenerated with FastAPI variant, `copier diff` evidence will be provided
- **No Manual Edits**: Generated FastAPI apps must run immediately with `uv run uvicorn` after render

### II. Deterministic Generation ✓

- **Compliance**: FastAPI scaffold templates are platform-independent (pure Python, no OS-specific paths)
- **Evidence**: Hooks will validate FastAPI/Uvicorn availability but not install them (uv manages dependencies)
- **Sample Renders**: Will add `api-python` or extend `full-stack` sample to include FastAPI variant
- **Baseline Metrics**: Scaffold render time and startup time will be captured via existing metrics scripts
- **Module Success**: FastAPI module will be tracked in `samples/metadata/module_success.json`

### III. Minimal Baseline, Optional Depth ✓

- **Compliance**: FastAPI is opt-in via `api_tracks` prompt (defaults to empty/disabled)
- **Evidence**: Baseline render (default sample) will not include FastAPI unless explicitly selected
- **Dependency Isolation**: FastAPI dependencies only added to `pyproject.toml` when module enabled
- **Documentation**: `docs/modules/api-fastapi.md.jinja` will document activation, usage, and compatibility
- **No Baseline Bloat**: Default sample maintains minimal footprint; FastAPI is additive

### IV. Documented Scaffolds ✓

- **Compliance**: Will create comprehensive FastAPI module documentation
- **Evidence**:
  - `docs/modules/api-fastapi.md.jinja` - architecture, routing patterns, configuration
  - `docs/quickstart.md.jinja` - updated with FastAPI-specific commands when module enabled
  - `.github/context/fastapi-patterns.md` - extension patterns, adding endpoints, middleware
  - `template/files/python/api_fastapi/README.md.jinja` - in-project quickstart
- **Validation**: Quickstart commands (`uv run uvicorn`, `uv run pytest`) will be smoke-tested
- **Examples**: Generated scaffold includes working example routes with tests

### V. Automation-Governed Compliance ✓

- **Compliance**: Existing CI workflows will validate FastAPI module
- **Evidence**:
  - `riso-quality.yml` workflow already handles Python quality checks (ruff, mypy, pylint, pytest)
  - `riso-matrix.yml` workflow tests across Python 3.11/3.12/3.13
  - `riso-container-build.yml` workflow will validate FastAPI Dockerfile if containerization enabled
- **Module Success Rate**: FastAPI module must maintain ≥98% success rate in render matrix
- **Quality Gates**: All quality checks must pass on generated FastAPI code without modification
- **Performance**: FastAPI scaffold must meet <10 minute baseline render budget

### Constitution Compliance Summary

**Status**: ✅ PASS - All constitutional principles satisfied

**Key Compliance Points**:

1. FastAPI scaffold is purely additive, no baseline changes
2. Template-based generation ensures deterministic output
3. Opt-in architecture preserves minimal baseline
4. Comprehensive documentation with executable examples
5. Existing CI/CD workflows provide automation governance

**No Complexity Violations**: FastAPI scaffold aligns with single-project structure, no architectural complexity added

## Project Structure

### Documentation (this feature)

```text
specs/001-fastapi-api-scaffold/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0: Technology decisions and patterns
├── data-model.md        # Phase 1: API entities and validation rules
├── quickstart.md        # Phase 1: Setup and validation commands
├── contracts/           # Phase 1: OpenAPI specifications
│   ├── health.yaml      # Health check endpoint contract
│   ├── examples.yaml    # Example CRUD endpoints contract
│   └── errors.yaml      # Error response schemas
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2: /speckit.tasks output (not yet created)
```

### Template Structure (template/)

```text
template/
├── copier.yml           # Updated with api_tracks prompt and FastAPI conditionals
├── files/
│   └── python/
│       └── api_fastapi/ # FastAPI scaffold templates (Jinja2)
│           ├── __init__.py.jinja
│           ├── main.py.jinja           # Application entry point
│           ├── config.py.jinja         # Environment-based configuration
│           ├── routes/
│           │   ├── __init__.py.jinja
│           │   ├── health.py.jinja    # Health check endpoint
│           │   └── examples.py.jinja  # Example CRUD routes
│           ├── models/
│           │   ├── __init__.py.jinja
│           │   ├── requests.py.jinja  # Pydantic request models
│           │   └── responses.py.jinja # Pydantic response models
│           ├── middleware/
│           │   ├── __init__.py.jinja
│           │   ├── cors.py.jinja      # CORS configuration
│           │   └── errors.py.jinja    # Global error handlers
│           └── tests/
│               ├── __init__.py.jinja
│               ├── conftest.py.jinja  # Pytest fixtures (test client)
│               ├── test_health.py.jinja
│               └── test_examples.py.jinja
├── hooks/
│   └── post_gen_project.py          # Updated to validate FastAPI module generation
└── prompts/
    └── api_tracks.yml.jinja         # Prompt configuration for API selection

docs/
└── modules/
    └── api-fastapi.md.jinja         # FastAPI module documentation

.github/
└── context/
    └── fastapi-patterns.md          # FastAPI extension patterns and best practices
```

### Generated Project Structure (rendered output when FastAPI enabled)

```text
{project_name}/                      # User's rendered project
├── pyproject.toml                   # Updated with FastAPI dependencies
├── {package_name}/
│   ├── api/                         # FastAPI application directory
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app instance and configuration
│   │   ├── config.py                # Settings class with environment vars
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py           # GET /health, GET /health/ready, GET /health/live
│   │   │   └── examples.py         # Example CRUD: GET, POST, PUT, DELETE
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── requests.py         # ExampleCreateRequest, ExampleUpdateRequest
│   │   │   └── responses.py        # ExampleResponse, HealthResponse, ErrorResponse
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── cors.py             # CORS middleware configuration
│   │       └── errors.py           # HTTP exception handlers
│   └── ...                          # Other project modules (CLI, shared, etc.)
├── tests/
│   └── api/
│       ├── __init__.py
│       ├── conftest.py             # TestClient fixture
│       ├── test_health.py          # Health endpoint tests
│       └── test_examples.py        # Example route tests
├── .env.example                     # Environment variable template
├── Dockerfile                       # Multi-stage build for FastAPI (if containers enabled)
└── docs/
    └── modules/
        └── api-fastapi.md          # Rendered FastAPI documentation
```

**Structure Decision**: Single project structure with API as a subpackage within the main package. This aligns with Riso's principle of minimal baseline complexity - FastAPI is simply another module alongside CLI, MCP, etc. The `{package_name}/api/` directory contains all FastAPI-specific code, making it easy to locate and extend. Tests mirror the source structure under `tests/api/`. This structure supports the 98% module success rate requirement by keeping FastAPI isolated and composable with other Riso modules.

## Complexity Tracking

**No Constitutional Violations**: This feature requires no justification table. The FastAPI scaffold:

- Uses single project structure (no additional projects)
- Adds no architectural patterns beyond FastAPI's built-in router system
- Maintains opt-in module design consistent with Riso principles
- Introduces no dependencies beyond the FastAPI ecosystem
- Aligns with existing quality, testing, and containerization infrastructure
