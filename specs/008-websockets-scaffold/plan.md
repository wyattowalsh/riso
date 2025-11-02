# Implementation Plan: WebSocket Scaffold

**Branch**: `008-websockets-scaffold` | **Date**: 2025-11-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-websockets-scaffold/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement production-ready WebSocket integration for FastAPI with real-time bidirectional communication, connection management, authentication, broadcasting, and testing utilities. The scaffold provides FastAPI endpoints with automatic heartbeats, room-based broadcasting, connection lifecycle management, and pytest fixtures. Target: 10,000 concurrent connections with <50ms latency (99th percentile) for 1,000-client broadcasts.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI ≥0.104.0 (WebSocket support), websockets library, pydantic ≥2.0.0  
**Storage**: In-memory connection registry (default), optional Redis for multi-server (documented pattern)  
**Testing**: pytest with async support, pytest-asyncio, WebSocket test client utilities  
**Target Platform**: Linux/macOS server (ASGI deployment via uvicorn/hypercorn)  
**Project Type**: Python module (optional, added to existing FastAPI projects)  
**Performance Goals**: 10,000 concurrent connections, <50ms broadcast latency (p99) for 1,000 clients, <10MB memory per 1,000 connections  
**Constraints**: <60s dead connection detection, <100ms room broadcast (p95), ≥80% test coverage  
**Scale/Scope**: Single module with ~15 files (manager, middleware, models, utilities, tests), integrates with existing FastAPI (006), Auth (009), Monitoring (010)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Version**: 1.0.0 | **Check Date**: 2025-11-01

### Principle Compliance

✅ **Module Sovereignty**: WebSocket support is optional module controlled by `websocket_module=enabled` in copier.yml. No baseline impact. Independent documentation in `docs/modules/websockets.md.jinja`. Smoke tests in `samples/` prove standalone functionality.

✅ **Deterministic Generation**: Same Copier answers produce identical WebSocket scaffold. No timestamps, random values, or system paths in generated code. All connection IDs use deterministic UUID generation from request context.

✅ **Minimal Baseline**: Zero impact on baseline template (module disabled by default). When enabled, adds ~15 files and 3 production dependencies (FastAPI already required, adds websockets + optional async-timeout). Renders in <5 seconds.

✅ **Quality Integration**: All generated WebSocket code passes ruff, mypy (strict mode with generics), pylint, pytest. Includes type hints for all public APIs. Test coverage target ≥80%. Integrates with `riso-quality.yml` and `riso-matrix.yml` workflows.

✅ **Test-First Development**: Implementation plan follows TDD discipline. Tests written before each component (connection manager, broadcast system, middleware). Pytest fixtures provided for testing WebSocket endpoints. Smoke tests verify template rendering.

✅ **Documentation Standards**: Comprehensive Jinja-templated documentation:

- `docs/modules/websockets.md.jinja` - Module overview, architecture, API reference
- `docs/quickstart.md` updates - WebSocket endpoint examples
- Code docstrings with usage examples
- Multi-server scaling patterns documented

✅ **Technology Consistency**: Uses approved stack (Python 3.11+ via uv, FastAPI, pytest). Leverages existing quality tools. GitHub Actions workflows. Container support via existing Docker infrastructure (005). No new tooling introduced.

### Gate Status: ✅ PASS

All constitution principles satisfied. No violations requiring justification. Module maintains sovereignty, determinism, and minimal baseline principles.

## Project Structure

### Documentation (this feature)

```text
specs/008-websockets-scaffold/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification with 7 user stories
├── research.md          # Phase 0 output (WebSocket patterns, FastAPI integration)
├── data-model.md        # Phase 1 output (Connection, Message, Room entities)
├── quickstart.md        # Phase 1 output (Getting started guide)
├── contracts/           # Phase 1 output (WebSocket message schemas)
│   ├── connection-lifecycle.json   # Connect, disconnect events
│   ├── message-schema.json         # Text/binary message formats
│   └── broadcast-protocol.json     # Room broadcasting protocol
├── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created yet)
└── checklists/          # Validation checklists
    └── requirements.md  # Specification quality checklist (complete)
```

### Source Code (rendered project with websocket_module=enabled)

```text
# Template files (before rendering)
template/files/python/websocket/
├── __init__.py.jinja
├── connection.py.jinja          # WebSocketConnection model
├── manager.py.jinja             # ConnectionManager singleton
├── middleware.py.jinja          # Lifecycle and auth middleware
├── models.py.jinja              # Message, Room, ConnectionMetadata
├── decorators.py.jinja          # @websocket_endpoint decorator
├── exceptions.py.jinja          # WebSocketError hierarchy
├── config.py.jinja              # Configuration (timeouts, limits, queue depth)
└── utils.py.jinja               # Heartbeat, backpressure, validation

template/files/python/websocket/testing/
├── __init__.py.jinja
├── fixtures.py.jinja            # Pytest fixtures (ws_client, auth_ws_client)
└── utilities.py.jinja           # Test helpers (multi-client simulator)

# Rendered project (after copier with websocket_module=enabled)
{package_name}/
├── websocket/
│   ├── __init__.py
│   ├── connection.py            # Connection lifecycle management
│   ├── manager.py               # Connection registry and broadcasting
│   ├── middleware.py            # Request interceptors
│   ├── models.py                # Data models with Pydantic validation
│   ├── decorators.py            # FastAPI integration decorators
│   ├── exceptions.py            # Typed exceptions for error handling
│   ├── config.py                # Settings with environment variable support
│   └── utils.py                 # Utilities for heartbeat, queues, etc.
│
└── api/
    ├── websocket_endpoints.py   # Example WebSocket routes
    └── websocket_middleware.py  # ASGI middleware integration

tests/websocket/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── test_connection.py           # Connection lifecycle tests
├── test_manager.py              # Broadcasting and room tests
├── test_middleware.py           # Auth and logging middleware tests
├── test_heartbeat.py            # Heartbeat and idle timeout tests
├── test_backpressure.py         # Queue limits and error handling tests
└── test_integration.py          # End-to-end WebSocket scenarios

docs/modules/
└── websockets.md                # User-facing module documentation
```

**Structure Decision**: Single Python module (websocket/) following Riso's optional module pattern. Integrates with existing FastAPI project structure (api/ directory). Tests mirror source structure (tests/websocket/). Documentation follows standard module docs pattern. No separate project needed—this is an enhancement to FastAPI scaffold (006).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations to track** - All constitution principles satisfied. Module maintains sovereignty (optional), determinism (reproducible renders), minimal baseline impact (zero when disabled, ~15 files when enabled), quality integration (passes all checks), test-first discipline (TDD workflow), documentation standards (Jinja templates), and technology consistency (approved stack).

## Phase 1 Design Validation

**Post-Design Constitution Re-Check** | **Date**: 2025-11-01

After completing Phase 1 design artifacts (data-model.md, contracts/, quickstart.md), we verify continued alignment with constitution:

✅ **Module Sovereignty**: Design confirms optional activation via copier.yml. No forced dependencies on other modules. WebSocket endpoints coexist with REST APIs without conflicts.

✅ **Deterministic Generation**: All schemas use explicit types (no random defaults). Connection IDs derived from request context (deterministic). Message timestamps use ISO 8601 UTC (reproducible).

✅ **Minimal Baseline**: Design adds zero files to baseline (module disabled by default). When enabled, data model defines 5 core entities (Connection, Message, Room, Metadata, Middleware) with minimal memory footprint (<10MB per 1,000 connections).

✅ **Quality Integration**: Pydantic models provide type safety and validation. All contracts include JSON Schema Draft-07 validation. Models compatible with mypy strict mode. Test fixtures support pytest-asyncio.

✅ **Test-First Development**: Quickstart includes testing examples. Data model defines testable invariants (state transitions, validation rules). Contracts specify error scenarios for TDD.

✅ **Documentation Standards**: Quickstart.md provides step-by-step guide with working examples. Data-model.md documents all entities with Pydantic models. Contracts/ includes JSON schemas with examples. All docs reference constitution principles.

✅ **Technology Consistency**: Design uses FastAPI (approved), Pydantic v2 (approved), pytest-asyncio (approved). No new dependencies beyond websockets library (minimal, standard). Configuration via Pydantic Settings (approved pattern).

### Design Compliance Summary

**Status**: ✅ PASS  
**Violations**: None  
**Justifications Required**: None  
**Blockers**: None

Phase 1 design artifacts maintain full constitution compliance. Ready to proceed to Phase 2 (task breakdown via `/speckit.tasks`).
