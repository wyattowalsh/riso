# Feature Specification: MCP Server Scaffolds

**Feature Branch**: `013-mcp-servers`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: Robust, advanced, and flexible MCP (Model Context Protocol) server scaffolds for both TypeScript and Python, enabling developers to quickly bootstrap production-ready MCP servers with best practices built-in.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bootstrap Python MCP Server (Priority: P1)

As a Python developer, I want to scaffold a complete MCP server with a single command so that I can immediately start implementing custom tools, resources, and prompts without worrying about protocol implementation details.

**Why this priority**: This is the core MVP - developers need a working Python MCP server scaffold before any other features matter. Python is the primary language for many AI/ML practitioners.

**Independent Test**: Can be fully tested by running the scaffold command, implementing one simple tool (e.g., "echo"), starting the server via STDIO transport, connecting with MCP Inspector, and successfully calling the tool. Delivers immediate value as a working MCP server.

**Acceptance Scenarios**:

1. **Given** I have Python 3.11+ and uv installed, **When** I run `copier copy template/ my-mcp-server` with `mcp_module=enabled` and `mcp_language=python`, **Then** I get a project with `src/mcp_server/`, `pyproject.toml`, example tool/resource/prompt implementations, and complete documentation
2. **Given** a scaffolded Python MCP server, **When** I run `uv sync && uv run python -m mcp_server`, **Then** the server starts successfully, registers all example capabilities, and responds to MCP protocol messages via STDIO
3. **Given** a running Python MCP server, **When** I connect with MCP Inspector or Claude Desktop, **Then** I can discover and invoke all registered tools, fetch resources, and execute prompts with proper error handling

---

### User Story 2 - Bootstrap TypeScript MCP Server (Priority: P1)

As a TypeScript/Node.js developer, I want to scaffold a complete MCP server with TypeScript support so that I can leverage strong typing, modern ESM syntax, and the Node.js ecosystem to build MCP servers.

**Why this priority**: TypeScript is the reference implementation language for MCP and critical for developers preferring static typing and JavaScript ecosystem tooling. Equal priority to Python scaffold.

**Independent Test**: Can be fully tested by running the scaffold command, implementing one simple tool, starting the server, and connecting with MCP Inspector. Delivers immediate value as a working TypeScript MCP server with full type safety.

**Acceptance Scenarios**:

1. **Given** I have Node.js 20 LTS and pnpm installed, **When** I run `copier copy template/ my-mcp-server` with `mcp_module=enabled` and `mcp_language=typescript`, **Then** I get a project with `src/`, `package.json`, TypeScript configs, example implementations, and complete documentation
2. **Given** a scaffolded TypeScript MCP server, **When** I run `pnpm install && pnpm run build && pnpm start`, **Then** the server compiles without errors, starts successfully, and responds to MCP protocol messages via STDIO
3. **Given** a running TypeScript MCP server, **When** I connect with MCP Inspector, **Then** I can discover all capabilities with full type information and invoke them with IDE autocomplete support

---

### User Story 3 - Production-Ready Configuration (Priority: P2)

As a developer deploying MCP servers to production, I want built-in configuration management, structured logging, and error handling so that my servers are observable and maintainable at scale.

**Why this priority**: After basic scaffolding works, production concerns become critical. This story adds the reliability and observability needed for real deployments.

**Independent Test**: Can be fully tested by configuring logging levels via config file, triggering various error conditions, and verifying structured logs are emitted with proper context. Demonstrates production-readiness independently of other features.

**Acceptance Scenarios**:

1. **Given** a scaffolded MCP server, **When** I provide a config file (TOML for Python, JSON for TypeScript) with custom settings, **Then** the server loads and applies all configurations including log levels, timeouts, and resource limits
2. **Given** a running MCP server with structured logging enabled, **When** any operation occurs (tool call, resource fetch, error), **Then** structured logs are emitted with correlation IDs, timestamps, and full context for debugging
3. **Given** an MCP tool that throws an error, **When** invoked by a client, **Then** the server catches the error, logs it with stack trace, and returns a properly formatted MCP error response without crashing

---

### User Story 4 - Comprehensive Documentation (Priority: P2)

As a developer new to MCP, I want complete documentation with examples and best practices so that I can understand how to implement tools, resources, and prompts correctly without reading the MCP spec repeatedly.

**Why this priority**: Good documentation multiplies the value of the scaffolds by reducing onboarding time and preventing common mistakes. Critical for adoption but secondary to working code.

**Independent Test**: Can be fully tested by following the quickstart guide from zero to deployed MCP server, implementing each example (tool, resource, prompt), and verifying all code samples work as documented.

**Acceptance Scenarios**:

1. **Given** I've scaffolded an MCP server, **When** I read the generated `README.md`, **Then** I find quickstart instructions, architecture overview, example implementations, testing guide, and deployment instructions
2. **Given** I want to implement a new MCP tool, **When** I consult the documentation, **Then** I find complete examples showing input validation, error handling, async operations, and response formatting
3. **Given** I'm deploying to production, **When** I read the deployment guide, **Then** I find instructions for STDIO and HTTP transports, Claude Desktop integration, security hardening, and monitoring setup

---

### User Story 5 - Advanced MCP Features (Priority: P3)

As an advanced MCP developer, I want examples of sophisticated features like pagination, streaming responses, and multi-step tool chains so that I can build complex, high-performance MCP servers.

**Why this priority**: These features are important for advanced use cases but not required for basic functionality. Can be added incrementally after core scaffolds are solid.

**Independent Test**: Can be fully tested by implementing a paginated resource, a streaming tool, and a multi-step workflow, then verifying they work correctly via MCP Inspector.

**Acceptance Scenarios**:

1. **Given** I need to return large datasets, **When** I implement a paginated resource following the scaffold examples, **Then** clients can request pages sequentially and the server efficiently streams results
2. **Given** I have a long-running operation, **When** I implement a streaming tool, **Then** the server sends progress updates to the client and properly handles cancellation
3. **Given** I need complex workflows, **When** I implement a multi-step tool chain where Tool B uses results from Tool A, **Then** the server coordinates execution and maintains state correctly

---

### User Story 6 - Multiple Transport Support (Priority: P3)

As a developer building cloud-based MCP services, I want support for HTTP/SSE transport in addition to STDIO so that I can deploy MCP servers as web services accessible to remote clients.

**Why this priority**: STDIO is sufficient for local/Claude Desktop use cases. HTTP transport enables broader deployment scenarios but is not required for MVP.

**Independent Test**: Can be fully tested by starting the server in HTTP mode, making REST/SSE requests from a client, and verifying all MCP protocol operations work identically to STDIO mode.

**Acceptance Scenarios**:

1. **Given** a scaffolded MCP server, **When** I configure it for HTTP transport and start it, **Then** it exposes RESTful endpoints for all MCP operations and an SSE endpoint for server-initiated messages
2. **Given** an MCP server running in HTTP mode, **When** I send authenticated requests from a remote client, **Then** all tool calls, resource fetches, and prompt executions work identically to STDIO mode
3. **Given** I need to switch transports, **When** I change the config from STDIO to HTTP, **Then** the server adapts without code changes to the tool/resource/prompt implementations

---

### Edge Cases

- **Transport Disconnection**: What happens when STDIO pipe breaks or HTTP connection drops mid-operation? Server MUST handle gracefully, log the event, clean up resources, and NOT crash.
- **Malformed Requests**: How does the server handle invalid JSON-RPC messages, missing required fields, or schema violations? MUST return proper MCP error responses with clear error codes.
- **Resource Exhaustion**: What happens when a tool tries to return a response larger than memory limits (100MB default)? MUST detect early, return error to client with size information, and NOT allow OOM crashes. Memory limit configurable via MAX_RESPONSE_SIZE_MB environment variable.
- **Concurrent Requests**: How does the server handle multiple simultaneous tool calls? MUST execute concurrently (when safe), maintain proper isolation, and NOT corrupt shared state.
- **Configuration Errors**: What happens when config file is missing or malformed? MUST fail fast at startup with clear error message indicating which config value is problematic.
- **Type Mismatches**: (TypeScript) What happens when runtime data doesn't match declared types? MUST validate at boundaries, log warnings, and return typed errors.
- **Async Cancellation**: What happens when a client cancels a long-running tool call? Server MUST detect cancellation signal, stop work, clean up resources, and NOT leak background tasks.
- **Version Compatibility**: How does the server handle clients using different MCP protocol versions? MUST negotiate version at connection time and clearly document supported versions.

## Requirements *(mandatory)*

### Functional Requirements - Protocol Implementation

- **FR-001**: System MUST implement MCP protocol version 2025-11-05 specification completely, supporting JSON-RPC 2.0 message format with all required MCP methods
- **FR-002**: System MUST provide STDIO transport as the default, using stdin for requests and stdout for responses with proper message framing
- **FR-003**: System MUST support HTTP/SSE transport as an optional mode, exposing RESTful endpoints for all MCP operations
- **FR-004**: System MUST handle protocol initialization including capability negotiation, protocol version exchange, and client information sharing
- **FR-005**: System MUST implement proper error handling per MCP spec, returning structured error responses with appropriate error codes and messages

### Functional Requirements - Python Implementation

- **FR-006**: Python scaffold MUST use Python 3.11+ as baseline, managed via uv package manager consistent with riso template standards
- **FR-007**: Python scaffold MUST use FastMCP library for protocol implementation, providing a Pythonic developer experience with decorator-based capability registration
- **FR-008**: Python scaffold MUST provide a clear project structure: `src/mcp_server/__init__.py`, `src/mcp_server/tools.py`, `src/mcp_server/resources.py`, `src/mcp_server/prompts.py`
- **FR-009**: Python scaffold MUST use TOML for configuration files (following feature 009 patterns), supporting `config.toml` or `.mcp-server.toml` in project directory
- **FR-010**: Python scaffold MUST use Loguru for structured logging with configurable log levels and output formats
- **FR-011**: Python scaffold MUST include pytest-based test suite with examples covering tool invocation, resource fetching, and prompt execution
- **FR-012**: Python scaffold MUST provide example implementations for at least one tool, one resource, and one prompt with complete type hints

### Functional Requirements - TypeScript Implementation

- **FR-013**: TypeScript scaffold MUST use Node.js 20 LTS as baseline with ESM module format
- **FR-014**: TypeScript scaffold MUST use official `@modelcontextprotocol/sdk` package for protocol implementation
- **FR-015**: TypeScript scaffold MUST provide a clear project structure: `src/index.ts`, `src/tools/`, `src/resources/`, `src/prompts/`, `src/config.ts`
- **FR-016**: TypeScript scaffold MUST use JSON or YAML for configuration files with full TypeScript type definitions via interfaces
- **FR-017**: TypeScript scaffold MUST provide comprehensive TypeScript types for all MCP entities (tools, resources, prompts, errors)
- **FR-018**: TypeScript scaffold MUST include vitest-based test suite with examples covering all MCP capabilities
- **FR-019**: TypeScript scaffold MUST provide example implementations for at least one tool, one resource, and one prompt with full type safety
- **FR-020**: TypeScript scaffold MUST include proper ESM build configuration using tsup or esbuild with source maps

### Functional Requirements - MCP Capabilities

- **FR-021**: Scaffolds MUST demonstrate tool implementation with JSON Schema input validation, error handling, and typed responses
- **FR-022**: Tool examples MUST show both simple synchronous tools and complex async tools with proper Promise/async-await patterns
- **FR-023**: Scaffolds MUST demonstrate resource implementation with URI-based addressing, MIME type specification, and content encoding
- **FR-024**: Resource examples MUST show both static resources (fixed content) and dynamic resources (computed/fetched content)
- **FR-025**: Scaffolds MUST demonstrate prompt implementation with parameter substitution, template rendering, and usage examples
- **FR-026**: Prompt examples MUST show both simple text prompts and complex multi-turn conversation templates
- **FR-027**: All capability examples MUST include complete JSDoc/docstrings explaining purpose, parameters, return values, and error conditions

### Functional Requirements - Configuration Management

- **FR-028**: Configuration MUST support environment variable overrides following standard precedence: env vars > config file > defaults
- **FR-029**: Configuration MUST include settings for: server name, version, log level, transport type, host/port (for HTTP), timeout values (default: tool operations 30s, resource fetches 10s, prompt rendering 5s)
- **FR-030**: Configuration schema MUST be validated at startup with clear error messages for invalid or missing required values
- **FR-031**: Configuration MUST support different profiles (development, production) loaded based on environment variable
- **FR-032**: Sensitive configuration values (API keys, credentials) MUST be loaded from environment variables, never committed to config files

### Functional Requirements - Development Experience

- **FR-033**: Scaffolds MUST include comprehensive README with: quickstart (< 5 minutes), architecture overview, API documentation, deployment guide
- **FR-034**: Scaffolds MUST provide clear examples showing how to: add new tools, add new resources, add new prompts, modify configuration, run tests
- **FR-035**: Scaffolds MUST include development tooling: linters (ruff/eslint), formatters (black/prettier), type checkers (mypy/tsc)
- **FR-036**: Scaffolds MUST provide `make` targets or npm scripts for common tasks: dev, build, test, lint, format, run
- **FR-037**: Scaffolds MUST include `.gitignore` appropriate for the language with common exclusions (node_modules, __pycache__, .env, etc.)
- **FR-038**: Scaffolds MUST include example `.env.example` file documenting all environment variables with descriptions and example values

### Functional Requirements - Transport Layer

- **FR-039**: STDIO transport MUST read JSON-RPC messages from stdin and write responses to stdout with proper newline framing
- **FR-040**: STDIO transport MUST handle EOF gracefully, cleaning up resources and shutting down without errors
- **FR-041**: HTTP transport MUST expose POST endpoints for all MCP methods following RESTful conventions
- **FR-042**: HTTP transport MUST implement Server-Sent Events (SSE) endpoint for server-initiated notifications and streaming responses
- **FR-043**: HTTP transport MUST include proper CORS configuration for cross-origin requests when enabled
- **FR-044**: HTTP transport MUST support authentication via configurable middleware (Bearer tokens, API keys, or custom schemes)
- **FR-045**: Transport layer MUST be abstracted so tool/resource/prompt implementations are transport-agnostic

### Functional Requirements - Testing & Quality

- **FR-046**: Test suites MUST achieve >80% code coverage for scaffold-generated code
- **FR-047**: Test suites MUST include unit tests for individual tools, resources, and prompts in isolation
- **FR-048**: Test suites MUST include integration tests verifying full MCP protocol flows from request to response
- **FR-049**: Test suites MUST include examples of mocking external dependencies (APIs, databases, file systems)
- **FR-050**: Scaffolds MUST integrate with riso's quality suite (feature 003), inheriting ruff/mypy/pylint for Python or eslint/tsc for TypeScript
- **FR-051**: CI workflows (feature 004) MUST validate MCP servers build successfully, all tests pass, and quality checks pass

### Functional Requirements - Security & Reliability

- **FR-052**: Server MUST validate all tool inputs against declared JSON Schema before execution, rejecting invalid inputs with clear errors
- **FR-053**: Server MUST implement request timeouts to prevent hung operations, with configurable timeout values per operation type (defaults: tool operations 30 seconds, resource fetches 10 seconds, prompt rendering 5 seconds)
- **FR-054**: Server MUST implement rate limiting when in HTTP mode to prevent abuse, with configurable limits per client (default: 100 requests per minute with burst allowance of 20 requests for temporary spikes)
- **FR-055**: Server MUST sanitize all error messages sent to clients, never exposing sensitive internal details or stack traces in production mode
- **FR-056**: Server MUST log all security-relevant events (auth failures, rate limit hits, suspicious requests) at appropriate log levels
- **FR-057**: Server MUST implement graceful shutdown, completing in-flight requests and cleaning up resources when receiving SIGTERM/SIGINT

### Key Entities

- **MCPServer**: The main server instance managing protocol implementation, transport layer, capability registration, and request routing. Contains configuration, registered tools/resources/prompts, and maintains connection state.

- **MCPTool**: A callable function exposed via MCP protocol. Has name, description, JSON Schema for input parameters, and implementation function. Can be sync or async, returns structured results or errors.

- **MCPResource**: A URI-addressable piece of data or content. Has URI pattern, MIME type, description, and fetch function. Can be static (fixed content) or dynamic (computed on request).

- **MCPPrompt**: A reusable template for LLM interactions. Has name, description, parameters, and template rendering logic. Can include system messages, user messages, and examples.

- **MCPConfiguration**: Server settings loaded from config file and environment. Includes server metadata (name, version), transport settings (type, host, port), operational settings (timeouts, log level, rate limits), and feature flags.

- **MCPTransport**: Abstraction over communication mechanism (STDIO or HTTP). Handles message framing, request/response correlation, error propagation, and connection lifecycle.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can bootstrap a working Python MCP server in under 5 minutes from `copier copy` to responding to MCP Inspector requests
- **SC-002**: Developers can bootstrap a working TypeScript MCP server in under 5 minutes from `copier copy` to responding to MCP Inspector requests
- **SC-003**: Generated scaffolds pass all quality checks (ruff/mypy/pylint for Python, eslint/tsc for TypeScript) without modification
- **SC-004**: Generated test suites achieve >80% code coverage and all tests pass on first run
- **SC-005**: Generated scaffolds successfully connect to Claude Desktop and execute at least one tool, fetch one resource, and execute one prompt
- **SC-006**: Documentation enables a developer unfamiliar with MCP to implement a custom tool in under 15 minutes
- **SC-007**: Scaffolds handle 100 concurrent requests without errors or crashes when tested with MCP load testing tool
- **SC-008**: Switching between STDIO and HTTP transports requires changing only configuration, no code changes to tool implementations
- **SC-009**: Generated servers gracefully handle all edge cases (disconnection, malformed requests, resource exhaustion) without crashing
- **SC-010**: CI workflows (feature 004) validate MCP scaffolds in under 3 minutes, providing fast feedback on PRs
- **SC-011**: Generated projects integrate seamlessly with existing riso features (quality suite, workflows, docs) requiring no special-casing
- **SC-012**: Post-generation surveys show >90% of developers successfully deploy their MCP server without requiring external support

## Assumptions *(mandatory)*

1. **MCP Protocol Stability**: Assumes MCP protocol version 2025-11-05 is stable and won't have breaking changes requiring immediate scaffold updates. If breaking changes occur, scaffolds will need rapid updates.

2. **SDK Availability**: Assumes FastMCP (Python) and @modelcontextprotocol/sdk (TypeScript) remain actively maintained and compatible with latest MCP spec. Python implementation uses FastMCP for its Pythonic decorator-based API. Fallback: implement protocol layer directly if SDKs become unmaintained.

3. **Claude Desktop Integration**: Assumes Claude Desktop remains the primary MCP client and its configuration format stays consistent. Other clients (VS Code extensions, web apps) may emerge but Claude Desktop is reference.

4. **Developer Environment**: Assumes developers have Python 3.11+/uv or Node.js 20/pnpm already installed per riso baseline requirements. Pre-gen hooks validate these prerequisites.

5. **Use Case Focus**: Assumes most developers want local/Claude Desktop deployment initially (STDIO transport), with HTTP transport as growth path. STDIO examples are more prominent than HTTP.

6. **Configuration Preference**: Assumes Python developers prefer TOML (consistent with feature 009 and PEP 621) and TypeScript developers prefer JSON (consistent with package.json conventions).

7. **Testing Priority**: Assumes developers value working examples over exhaustive tests initially. Scaffolds provide high-value test examples but not 100% coverage of every edge case.

8. **Documentation Format**: Assumes developers want documentation in Markdown within the scaffold project, not separate documentation sites. Links to external MCP spec/SDK docs for deep dives.

9. **Production Deployment**: Assumes most production deployments will use containerization (feature 005). MCP scaffolds should include Dockerfile examples and health check endpoints.

10. **Security Model**: Assumes MCP servers deployed locally/Claude Desktop don't require authentication, but HTTP-deployed servers do. Authentication middleware is optional and configurable.

## Open Questions *(if applicable)*

1. **Configuration Format**: Should we offer both TOML and JSON for Python to match TypeScript? Or enforce TOML for consistency with feature 009? Current plan: TOML only for Python, but may add JSON if user feedback demands it.

## Clarifications

### Session 2025-11-02

- Q: Should Python scaffold use FastMCP (simpler, more Pythonic) or official MCP Python SDK (more aligned with spec)? → A: FastMCP
- Q: Should Python or TypeScript scaffold be implemented first, or both in parallel? → A: Parallel development with shared patterns
- Q: What is the specific memory threshold for "resource exhaustion" edge case? → A: 100MB per response
- Q: What are the specific default timeout values for different operation types? → A: Tool:30s, Resource:10s, Prompt:5s
- Q: What are the specific rate limit defaults for HTTP transport? → A: 100 requests/minute per client

## Out of Scope *(mandatory)*

1. **Custom MCP Protocol Extensions**: Scaffolds implement MCP spec as-is. Custom protocol extensions, vendor-specific features, or experimental protocol changes are out of scope.

2. **MCP Client Implementation**: This feature provides server scaffolds only. MCP client libraries, MCP Inspector alternatives, or custom testing clients are separate concerns.

3. **Language Beyond Python/TypeScript**: No support for Go, Rust, Java, or other MCP SDK languages in this feature. Future features may add them if demand warrants.

4. **Complex Authentication Schemes**: HTTP transport will support Bearer tokens and API keys. OAuth2, SAML, mTLS, and other enterprise auth schemes are out of scope initially.

5. **Advanced Streaming**: Basic SSE streaming for HTTP transport is in scope. Advanced patterns like bidirectional streaming, backpressure, or custom streaming protocols are out of scope.

6. **Built-in Tool Libraries**: Scaffolds provide examples of tools. Pre-built libraries of common tools (web search, file operations, database queries) are separate feature opportunities.

7. **GUI/Admin Interface**: MCP servers are headless. Web UIs for server administration, monitoring dashboards, or graphical configuration editors are out of scope.

8. **Multi-Tenancy**: Scaffolds support single-tenant deployments. Multi-tenant architectures, tenant isolation, per-tenant configuration, and tenant billing are out of scope.

9. **Distributed MCP Servers**: Scaffolds are for single-process servers. Distributed architectures, server clustering, load balancing, or service mesh integration are out of scope.

10. **MCP Registry/Marketplace**: Publishing MCP servers to a registry, discovering public MCP servers, or marketplace features are separate ecosystem concerns.

## Dependencies *(include if this feature is blocked by or builds on others)*

### Required Dependencies

- **Feature 001 (Build Riso Template)**: Core Copier template infrastructure, Jinja rendering, uv/pnpm tooling baseline
- **Feature 003 (Code Quality Integrations)**: Quality suite (ruff, mypy, pylint, pytest) for validating generated MCP servers
- **Feature 004 (GitHub Actions Workflows)**: CI workflows to validate MCP scaffolds build and test successfully
- **Feature 009 (Typer CLI Scaffold)**: Patterns for TOML configuration, Loguru logging, and Python CLI structure

### Optional Dependencies

- **Feature 005 (Container Deployment)**: Dockerfiles and docker-compose for containerized MCP server deployment
- **Feature 006 (FastAPI API Scaffold)**: Patterns for HTTP endpoints, request validation, and error handling (applicable to HTTP transport)

### Parallel Development

- **Feature 013** Python and TypeScript scaffolds will be developed in parallel with shared test scenarios and patterns to ensure feature parity
- Both implementations target simultaneous MVP delivery to serve both Python AI/ML and TypeScript/Node.js developer communities
- MCP-specific code lives in `template/files/mcp/` and doesn't conflict with other modules
- Shares test infrastructure and quality tools but has independent test suites

## Risks & Mitigations *(include if feature has notable risks)*

1. **Risk**: MCP protocol evolves with breaking changes, requiring frequent scaffold updates.
   **Likelihood**: Medium - Protocol is young (2025-11-05) and may see revisions.
   **Impact**: High - Scaffolds could generate incompatible servers.
   **Mitigation**: Pin to specific MCP SDK versions, include protocol version in scaffold metadata, monitor MCP GitHub for changes, provide migration guides for breaking updates.

2. **Risk**: FastMCP or official Python SDK become unmaintained or diverge in implementation.
   **Likelihood**: Low - FastMCP is actively maintained; TypeScript SDK maintained by Anthropic.
   **Impact**: High - Would require rewriting Python scaffold protocol layer.
   **Mitigation**: Abstract protocol implementation behind interface, monitor FastMCP GitHub activity, have fallback plan to implement protocol directly using official spec or switch to official Python SDK if it becomes available and mature.

3. **Risk**: Developers expect features beyond basic scaffolding (pre-built tool libraries, admin UIs).
   **Likelihood**: Medium - Feature creep is common for developer tools.
   **Impact**: Medium - Could delay delivery or bloat scaffolds.
   **Mitigation**: Clearly document scope (in-spec, out-of-scope sections), provide extension points for custom features, link to community resources for advanced use cases.

4. **Risk**: HTTP transport adds complexity without proportional value for most users.
   **Likelihood**: Low - STDIO covers majority use case (Claude Desktop).
   **Impact**: Medium - Increases maintenance burden, test matrix, and documentation size.
   **Mitigation**: Make HTTP transport fully optional (can be disabled at scaffold time), provide separate documentation section, ensure STDIO works perfectly first.

5. **Risk**: TypeScript/Python scaffolds diverge in capabilities or quality, confusing users.
   **Likelihood**: Medium - Different languages, SDKs, and conventions.
   **Impact**: Medium - Users may perceive one language as "second-class."
   **Mitigation**: Share specification and test scenarios across both implementations, maintain feature parity, unified documentation explaining differences are language conventions not feature gaps.

6. **Risk**: Integration with Claude Desktop changes requiring scaffold updates.
   **Likelihood**: Medium - Claude Desktop MCP integration is relatively new.
   **Impact**: Medium - Generated servers might not work with new Claude Desktop versions.
   **Mitigation**: Document Claude Desktop version compatibility, include Claude Desktop config examples in scaffolds, test against both current and beta Claude Desktop versions.

7. **Risk**: Performance issues with STDIO transport for high-throughput use cases.
   **Likelihood**: Low - STDIO has minimal overhead for typical Claude Desktop usage.
   **Impact**: Low - Most MCP servers are low-volume interactive tools.
   **Mitigation**: Document performance characteristics, recommend HTTP transport for high-throughput scenarios, include benchmarking examples in scaffold.

## Related Features *(include if this depends on or relates to other features)*

- **Feature 009 (Typer CLI Scaffold)**: MCP servers follow similar patterns - TOML config, Loguru logging, structured project layout. Python MCP scaffold borrows heavily from Feature 009 patterns.
- **Feature 006 (FastAPI API Scaffold)**: HTTP transport for MCP shares patterns with FastAPI - request validation, error handling, CORS, health checks.
- **Feature 003 (Code Quality Integrations)**: MCP scaffolds integrate with quality suite, inheriting ruff/mypy/pylint for Python or eslint/tsc for TypeScript.
- **Feature 004 (GitHub Actions Workflows)**: CI workflows validate MCP scaffolds, running tests and quality checks automatically.
- **Feature 005 (Container Deployment)**: MCP servers can be containerized, following Feature 005 patterns for Dockerfiles and health endpoints.
