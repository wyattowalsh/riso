````markdown
# Implementation Plan: MCP Server Scaffolds

**Branch**: `013-mcp-servers` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-mcp-servers/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Feature 013 delivers production-ready Copier template scaffolds for building Model Context Protocol (MCP) servers in both Python and TypeScript. Developers can bootstrap complete MCP servers with a single command, getting example implementations of tools, resources, and prompts, along with STDIO/HTTP transports, configuration management, structured logging, comprehensive tests, and full documentation. Both language implementations will be developed in parallel to ensure feature parity and serve both Python AI/ML and TypeScript/Node.js developer communities simultaneously.

## Technical Context

**Language/Version**: Python 3.11+ (uv-managed), TypeScript 5.x with Node.js 20 LTS  
**Primary Dependencies**: 
- Python: FastMCP, Loguru, tomli/tomllib, pytest
- TypeScript: @modelcontextprotocol/sdk, vitest, tsup/esbuild
**Storage**: File-based (TOML for Python, JSON/YAML for TypeScript)  
**Testing**: pytest (Python), vitest (TypeScript), integration tests via MCP Inspector  
**Target Platform**: Cross-platform (Linux, macOS, Windows) - STDIO primary, HTTP/SSE optional  
**Project Type**: Template (Copier) - generates dual-language scaffold projects  
**Performance Goals**: 
- Bootstrap time < 5 minutes (SC-001, SC-002)
- Handle 100 concurrent requests without errors (SC-007)
- Tool timeout 30s, Resource 10s, Prompt 5s (FR-053)
- Response size limit 100MB (Edge Case clarification)
**Constraints**: 
- >80% test coverage required (FR-046)
- Quality checks pass without modification (SC-003)
- CI validation < 3 minutes (SC-010)
- Transport-agnostic tool implementations (FR-045)
**Scale/Scope**: 
- 2 language implementations (Python, TypeScript)
- 3 MCP capabilities (tools, resources, prompts)
- 2 transports (STDIO default, HTTP/SSE optional)
- Rate limit: 100 req/min with burst of 20 (FR-054)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS (Constitution template not yet ratified for this project)

Since the constitution file is currently a template placeholder, we apply riso project best practices:

✅ **Modularity**: MCP scaffolds are self-contained modules within `template/files/mcp/`  
✅ **Testability**: Both Python and TypeScript scaffolds include comprehensive test suites (FR-046, FR-047, FR-048)  
✅ **Documentation**: Complete README, quickstart, examples required (FR-033, FR-034)  
✅ **Quality Integration**: Inherits riso quality suite (FR-050, FR-051)  
✅ **Simplicity**: STDIO transport primary, HTTP optional; no over-engineering  
✅ **Observability**: Structured logging required (FR-010, Loguru for Python)

## Project Structure

### Documentation (this feature)

```text
specs/013-mcp-servers/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── python-mcp-api.md       # Python MCP protocol contracts
│   └── typescript-mcp-api.md   # TypeScript MCP protocol contracts
├── spec.md              # Feature specification (already exists)
└── checklists/          # Quality checklists (already exists)
    └── requirements.md
```

### Source Code (repository root - Template Structure)

```text
template/files/
├── mcp/                         # NEW: MCP server scaffolds
│   ├── python/                  # Python MCP scaffold
│   │   ├── src/
│   │   │   └── mcp_server/
│   │   │       ├── __init__.py
│   │   │       ├── server.py
│   │   │       ├── tools.py
│   │   │       ├── resources.py
│   │   │       ├── prompts.py
│   │   │       └── config.py
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── conftest.py
│   │   ├── pyproject.toml.jinja
│   │   ├── config.toml.jinja
│   │   ├── .env.example.jinja
│   │   ├── README.md.jinja
│   │   └── Makefile.jinja
│   │
│   └── typescript/              # TypeScript MCP scaffold
│       ├── src/
│       │   ├── index.ts
│       │   ├── server.ts
│       │   ├── tools/
│       │   ├── resources/
│       │   ├── prompts/
│       │   └── config.ts
│       ├── tests/
│       │   ├── unit/
│       │   └── integration/
│       ├── package.json.jinja
│       ├── tsconfig.json.jinja
│       ├── vitest.config.ts.jinja
│       ├── config.json.jinja
│       ├── .env.example.jinja
│       └── README.md.jinja
│
├── shared/                      # EXISTING: Shared template resources
│   ├── quality/                 # Quality suite integration (feature 003)
│   └── .github/                 # CI workflows (feature 004)
│
scripts/ci/
├── validate_mcp_scaffolds.py   # NEW: MCP scaffold validation
└── render_mcp_samples.py       # NEW: Sample rendering with MCP modules

samples/
└── mcp-servers/                 # NEW: Rendered MCP server samples
    ├── python-stdio/
    ├── python-http/
    ├── typescript-stdio/
    └── typescript-http/
```

**Structure Decision**: Template-based project structure. The MCP scaffolds live in `template/files/mcp/` with separate Python and TypeScript subdirectories. Each contains complete project structures that will be rendered via Copier with Jinja templating. This mirrors the pattern established in feature 009 (Typer CLI) and feature 006 (FastAPI). Shared resources (quality, workflows) are inherited from `template/files/shared/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. The feature follows riso template patterns:
- Modular scaffold structure (consistent with features 006, 009)
- Dual-language support justified by MCP ecosystem (Python AI/ML, TypeScript reference implementation)
- Shared quality/CI infrastructure (no duplication)
- Transport abstraction (FR-045) keeps tool implementations simple

---

## Phase 0: Research ✅ COMPLETE

*Deliverable: `research.md` with all technical unknowns resolved*

**Status**: Complete - see [research.md](./research.md)

**Key Research Topics**:
1. MCP Protocol version and JSON-RPC foundation
2. Python SDK selection (FastMCP vs alternatives)
3. TypeScript SDK selection (official @modelcontextprotocol/sdk)
4. Configuration management strategies (TOML vs JSON vs YAML)
5. Logging approaches (Loguru for Python, structured for TypeScript)
6. Testing strategies with MCP Inspector
7. Transport abstraction patterns (STDIO vs HTTP/SSE)
8. Example implementations (simple + complex per capability)
9. Claude Desktop integration requirements
10. Security best practices (validation, rate limiting, error sanitization)

All decisions documented with rationale, alternatives considered, and implementation guidance.

---

## Phase 1: Design & Contracts ✅ COMPLETE

*Deliverables: `data-model.md`, `contracts/*.md`, `quickstart.md`, updated agent context*

### Completed Deliverables

1. **Data Model** (`data-model.md`) ✅
   - 6 core entities: MCPServer, MCPTool, MCPResource, MCPPrompt, MCPConfiguration, MCPTransport
   - Complete attribute definitions with types, validation rules, defaults
   - Entity relationships and lifecycle diagrams
   - State machine for MCPServer (idle → running → stopping → stopped)
   - Implementation notes for Python/TypeScript differences

2. **API Contracts** ✅
   - `contracts/python-mcp-api.md`: FastMCP decorator-based API, Pydantic schemas, STDIO/HTTP transports, Loguru logging, pytest testing, TOML configuration
   - `contracts/typescript-mcp-api.md`: @modelcontextprotocol/sdk handler-based API, Zod schemas, STDIO/SSE transports, structured logging, vitest testing, JSON configuration
   - Both contracts include: tool/resource/prompt registration, error handling, configuration loading, lifecycle hooks, performance requirements

3. **Developer Guide** (`quickstart.md`) ✅
   - Complete 15-20 minute tutorial from scaffold to Claude Desktop integration
   - Step-by-step for both Python and TypeScript
   - Example weather tool implementation
   - Local testing instructions
   - Claude Desktop configuration
   - Advanced examples (resources, prompts)
   - Production configuration guidance
   - Troubleshooting section

4. **Agent Context Update** ⚠️ PENDING
   - Need to run `.specify/scripts/bash/update-agent-context.sh copilot`
   - Technologies to add: FastMCP, @modelcontextprotocol/sdk, MCP Inspector, STDIO/HTTP transports, Zod, Pydantic

### Design Decisions from Phase 1

**Dual Language Strategy**:
- Python: FastMCP library (decorator-based, Pythonic) + TOML config
- TypeScript: Official SDK (handler-based, explicit) + JSON config
- Justification: FastMCP preferred for Python (simpler DX), official SDK for TypeScript (reference implementation)

**Configuration Management**:
- Python: TOML files (aligns with PEP 621, existing pyproject.toml patterns)
- TypeScript: JSON files (aligns with package.json ecosystem)
- Both: Environment variable overrides for deployment flexibility

**Testing Strategy**:
- Unit tests: Isolated handler/tool logic (pytest, vitest)
- Integration tests: Full server with transport layer (optional)
- MCP Inspector: Manual testing during development

**Security Baseline**:
- Input validation: Pydantic (Python), Zod (TypeScript)
- Error sanitization: Never send stack traces to clients
- Rate limiting: Token bucket algorithm for HTTP transport
- Graceful degradation: Timeout enforcement at tool/resource/prompt level

### Phase 1 Summary

✅ **All deliverables complete** except agent context script execution

Phase 1 provides comprehensive architectural documentation:
- Data model defines all entities and relationships
- API contracts specify exact interfaces for both languages
- Quickstart guide enables rapid developer onboarding
- Design decisions documented with clear rationale

**Ready for Phase 2** (`/speckit.tasks` command) or direct implementation.

---

## Phase 2: Tasks

*Use `/speckit.tasks` command to generate task breakdown*

Phase 2 is not part of the `/speckit.plan` workflow. After completing Phase 1, run:

```bash
/speckit.tasks
```

This will generate a detailed task breakdown in `tasks.md` with:
- Implementation tasks decomposed from functional requirements
- Dependency graph between tasks
- Acceptance criteria per task
- Estimated complexity/effort

````
