# Research: MCP Server Scaffolds

**Feature**: 013-mcp-servers | **Phase**: 0 (Research) | **Date**: 2025-11-02

## Overview

This research phase resolves technical unknowns, evaluates SDK choices, and establishes implementation patterns for Python and TypeScript MCP server scaffolds.

## Research Tasks Completed

### 1. MCP Protocol Implementation

**Decision**: Use MCP protocol version 2025-11-05 specification

**Rationale**:
- Official specification from Anthropic (protocol authors)
- JSON-RPC 2.0 foundation provides standard message format
- Well-documented capability negotiation, initialization, and error handling
- Active community and reference implementations

**Alternatives Considered**:
- Custom protocol: Rejected due to lack of ecosystem compatibility
- Earlier protocol versions: Rejected as outdated

**Key Findings**:
- Protocol methods: `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`, `prompts/get`
- Capability negotiation occurs during initialization handshake
- Error responses use JSON-RPC 2.0 error codes with MCP-specific extensions
- Transport-agnostic design allows STDIO and HTTP/SSE implementations

**References**:
- https://modelcontextprotocol.io/specification
- https://github.com/modelcontextprotocol/specification

---

### 2. Python SDK Selection

**Decision**: FastMCP library

**Rationale**:
- Pythonic decorator-based API simplifies capability registration
- Active maintenance and community support
- Simpler learning curve for Python developers
- Better alignment with Python idioms (decorators, type hints)
- Clarification session confirmed this choice

**Alternatives Considered**:
- Official MCP Python SDK: Less mature at time of decision, less Pythonic API
- Direct protocol implementation: Higher maintenance burden, reinventing wheel

**Key Findings**:
- FastMCP provides `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()` decorators
- Automatic JSON Schema generation from type hints
- Built-in STDIO transport with optional HTTP/SSE support
- Integration with standard Python async/await patterns

**References**:
- https://github.com/jlowin/fastmcp
- FastMCP documentation and examples

---

### 3. TypeScript SDK Selection

**Decision**: Official @modelcontextprotocol/sdk

**Rationale**:
- Reference implementation maintained by Anthropic
- Full TypeScript type safety for all MCP entities
- Direct alignment with protocol specification
- Long-term support guaranteed by protocol authors
- Extensive documentation and examples

**Alternatives Considered**:
- Third-party wrappers: Unnecessary abstraction over official SDK
- Direct protocol implementation: Reinventing reference implementation

**Key Findings**:
- SDK provides `Server` class with method handlers for all MCP operations
- Full type definitions for `Tool`, `Resource`, `Prompt`, `McpError`
- Built-in support for STDIO and HTTP/SSE transports
- Type-safe request/response handling

**References**:
- https://github.com/modelcontextprotocol/typescript-sdk
- https://modelcontextprotocol.io/docs/typescript-sdk

---

### 4. Configuration Management

**Decision**: TOML for Python, JSON for TypeScript

**Rationale**:
- Python: TOML aligns with PEP 621 and feature 009 (Typer CLI) patterns
- TypeScript: JSON aligns with package.json conventions
- Both support environment variable overrides
- Clear separation of config (committed) vs secrets (environment)

**Alternatives Considered**:
- Unified JSON for both: Rejected to maintain language ecosystem consistency
- YAML for both: Rejected due to parsing complexity and security concerns

**Key Findings**:
- Python: Use `tomli` (Python <3.11) or `tomllib` (Python 3.11+)
- TypeScript: Native JSON parsing with Zod/TypeBox for validation
- Environment variable naming: `MCP_SERVER_*` prefix for clarity
- Profile support: `MCP_PROFILE=development|production` environment variable

**Configuration Schema**:
```toml
# Python config.toml
[server]
name = "my-mcp-server"
version = "0.1.0"
log_level = "INFO"

[transport]
type = "stdio"  # or "http"
host = "0.0.0.0"  # HTTP only
port = 8000      # HTTP only

[timeouts]
tool = 30
resource = 10
prompt = 5

[limits]
max_response_size_mb = 100
rate_limit_per_minute = 100
rate_limit_burst = 20
```

**References**:
- Feature 009 (Typer CLI) TOML patterns
- https://toml.io/en/
- https://github.com/colinhacks/zod

---

### 5. Structured Logging

**Decision**: Loguru for Python, custom structured logger for TypeScript

**Rationale**:
- Python: Loguru provides zero-config structured logging (feature 009 pattern)
- TypeScript: Lightweight wrapper around console with structured JSON output
- Both support correlation IDs, log levels, and contextual information
- Production-ready observability without heavy dependencies

**Alternatives Considered**:
- Python stdlib logging: More verbose, less ergonomic
- Winston/Pino (TypeScript): Overkill for scaffold, adds dependency weight

**Key Findings**:
- Log format: JSON in production, human-readable in development
- Required fields: timestamp, level, message, correlation_id, context
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Automatic stack traces for errors

**Logging Pattern**:
```python
# Python with Loguru
from loguru import logger

logger.info("Tool invoked", extra={"tool": "echo", "correlation_id": "abc-123"})
```

```typescript
// TypeScript structured logger
logger.info("Tool invoked", { tool: "echo", correlationId: "abc-123" });
```

**References**:
- Feature 009 Loguru integration
- https://github.com/Delgan/loguru

---

### 6. Testing Strategy

**Decision**: pytest (Python), vitest (TypeScript) with MCP Inspector integration

**Rationale**:
- Both frameworks align with riso baseline (feature 003 quality suite)
- MCP Inspector provides protocol-level validation
- Unit tests for individual capabilities, integration tests for full flows
- Coverage target >80% (FR-046)

**Alternatives Considered**:
- Jest for TypeScript: Slower, more configuration required
- unittest (Python): Less ergonomic than pytest

**Key Findings**:
- Unit tests mock MCP transport layer, test tool/resource/prompt logic in isolation
- Integration tests use real STDIO pipes or HTTP endpoints
- Contract tests verify JSON-RPC message format compliance
- MCP Inspector can be scripted for automated protocol validation

**Test Structure**:
```
tests/
├── unit/
│   ├── test_tools.py|ts
│   ├── test_resources.py|ts
│   └── test_prompts.py|ts
├── integration/
│   ├── test_stdio_transport.py|ts
│   ├── test_http_transport.py|ts
│   └── test_full_protocol.py|ts
└── contract/
    └── test_mcp_compliance.py|ts
```

**References**:
- Feature 003 (Code Quality) test patterns
- https://github.com/modelcontextprotocol/inspector

---

### 7. Transport Layer Abstraction

**Decision**: Abstract base class pattern with STDIO and HTTP implementations

**Rationale**:
- Tool/resource/prompt implementations remain transport-agnostic (FR-045)
- Switching transports requires only configuration change (SC-008)
- Clean separation of concerns (protocol vs transport)
- Extensible for future transport types

**Alternatives Considered**:
- No abstraction: Would couple tool logic to transport, violating FR-045
- Middleware pattern: More complex than needed for two transport types

**Key Findings**:
- Transport interface: `send_request(message) -> response`, `receive_message() -> message`
- STDIO uses stdin/stdout with newline-delimited JSON
- HTTP uses POST endpoints + SSE for server-initiated messages
- Both transports handle connection lifecycle, framing, error propagation

**Transport Interface**:
```python
# Python
class MCPTransport(ABC):
    @abstractmethod
    async def send_message(self, message: dict) -> None: ...
    
    @abstractmethod
    async def receive_message(self) -> dict: ...
    
    @abstractmethod
    async def close(self) -> None: ...
```

```typescript
// TypeScript
interface MCPTransport {
  sendMessage(message: object): Promise<void>;
  receiveMessage(): Promise<object>;
  close(): Promise<void>;
}
```

**References**:
- MCP specification transport requirements
- Feature 006 (FastAPI) HTTP patterns for HTTP transport

---

### 8. Example Implementations

**Decision**: One simple + one complex example per capability type

**Rationale**:
- Simple examples (echo tool, static resource, greeting prompt) show basic patterns
- Complex examples (async API call tool, dynamic resource with pagination, multi-turn prompt) demonstrate advanced features
- Both satisfy FR-022, FR-024, FR-026 requirements
- Provides clear learning path for developers

**Alternatives Considered**:
- Only simple examples: Insufficient for production use cases
- Many examples: Clutters scaffold, reduces clarity

**Key Findings**:

**Tool Examples**:
1. Simple: `echo` - synchronous, string in/out, no external dependencies
2. Complex: `fetch_url` - async, error handling, timeout, retry logic

**Resource Examples**:
1. Simple: `about` - static JSON content, fixed MIME type
2. Complex: `file_browser` - dynamic directory listing, URI parameters, pagination

**Prompt Examples**:
1. Simple: `greeting` - single-turn, string template, basic parameters
2. Complex: `code_review` - multi-turn conversation, context injection, examples

**Example Tool Template**:
```python
# Python with FastMCP
from fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("my-server")

class EchoInput(BaseModel):
    message: str

@mcp.tool()
async def echo(input: EchoInput) -> str:
    """Echo the input message back to the caller."""
    return input.message
```

```typescript
// TypeScript with official SDK
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { z } from "zod";

const server = new Server({
  name: "my-server",
  version: "1.0.0"
});

server.tool(
  "echo",
  "Echo the input message back to the caller",
  {
    message: z.string().describe("The message to echo")
  },
  async ({ message }) => ({ content: [{ type: "text", text: message }] })
);
```

**References**:
- FastMCP examples: https://github.com/jlowin/fastmcp/tree/main/examples
- TypeScript SDK examples: https://github.com/modelcontextprotocol/typescript-sdk/tree/main/examples

---

### 9. Claude Desktop Integration

**Decision**: Provide ready-to-use Claude Desktop configuration files

**Rationale**:
- Claude Desktop is primary MCP client (assumption #3)
- Simple configuration enables immediate testing
- Reduces onboarding friction

**Alternatives Considered**:
- Generic client documentation: Less actionable for users
- Multiple client configs: Scope creep (Claude Desktop is reference)

**Key Findings**:
- Configuration location: `~/Library/Application Support/Claude/` (macOS), `%APPDATA%\Claude\` (Windows), `~/.config/claude/` (Linux)
- Configuration format: JSON with server command and environment
- STDIO servers: Simple command execution
- HTTP servers: URL + optional authentication

**Claude Desktop Config Template**:
```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_server"],
      "env": {
        "MCP_PROFILE": "production"
      }
    }
  }
}
```

**References**:
- https://docs.anthropic.com/claude/docs/mcp-client-setup
- Claude Desktop MCP integration documentation

---

### 10. Security Best Practices

**Decision**: Implement input validation, rate limiting, error sanitization, graceful shutdown

**Rationale**:
- Production deployments need security hardening
- HTTP transport exposes server to network threats
- FR-052 through FR-057 mandate these features

**Alternatives Considered**:
- Basic validation only: Insufficient for production (violates FR-052-057)
- Complex WAF integration: Out of scope, adds deployment complexity

**Key Findings**:

**Input Validation** (FR-052):
- JSON Schema validation before tool execution
- Reject invalid inputs with clear error messages
- Type coercion where safe, strict validation where not

**Rate Limiting** (FR-054):
- Token bucket algorithm: 100 requests/minute, burst 20
- Per-client tracking via IP or API key
- HTTP 429 response with Retry-After header

**Error Sanitization** (FR-055):
- Production mode: Generic error messages, no stack traces
- Development mode: Full error details for debugging
- Log full errors server-side regardless of mode

**Graceful Shutdown** (FR-057):
- SIGTERM/SIGINT signal handlers
- Complete in-flight requests (with timeout)
- Close transport connections cleanly
- Release resources (files, sockets, etc.)

**Security Implementation Pattern**:
```python
# Python rate limiting with token bucket
from aiolimiter import AsyncLimiter

rate_limiter = AsyncLimiter(max_rate=100, time_period=60)

async def handle_request(request):
    async with rate_limiter:
        return await process_request(request)
```

```typescript
// TypeScript graceful shutdown
process.on("SIGTERM", async () => {
  logger.info("SIGTERM received, starting graceful shutdown");
  await server.close();
  process.exit(0);
});
```

**References**:
- OWASP API Security Top 10
- Feature 011 (API Rate Limit/Throttle) patterns

---

## Summary of Decisions

| Topic | Decision | Primary Rationale |
|-------|----------|-------------------|
| Protocol | MCP 2025-11-05 | Official spec, JSON-RPC foundation, active ecosystem |
| Python SDK | FastMCP | Pythonic decorators, clarification session confirmed |
| TypeScript SDK | @modelcontextprotocol/sdk | Reference implementation, official support |
| Python Config | TOML | PEP 621 compliance, feature 009 consistency |
| TypeScript Config | JSON | package.json alignment, native parsing |
| Python Logging | Loguru | Feature 009 pattern, zero-config structured logging |
| TypeScript Logging | Custom structured | Lightweight, no heavy dependencies |
| Testing | pytest + vitest | Riso baseline alignment, >80% coverage |
| Transport | Abstract base class | Transport-agnostic tools (FR-045, SC-008) |
| Examples | 1 simple + 1 complex | Learning path, production patterns |
| Claude Desktop | Config templates | Primary client, immediate testing |
| Security | Validation + rate limit + sanitization | Production readiness (FR-052-057) |

## Open Questions Resolved

All open questions from specification have been resolved through this research phase. The remaining open question (TOML-only vs dual TOML/JSON for Python) is deferred to implementation based on actual developer feedback.

## Next Steps

- **Phase 1**: Create data-model.md defining entities (MCPServer, MCPTool, MCPResource, MCPPrompt, MCPConfiguration, MCPTransport)
- **Phase 1**: Generate API contracts in contracts/ (Python and TypeScript MCP protocol contracts)
- **Phase 1**: Create quickstart.md for developers using the scaffolds
- **Phase 1**: Update agent context with new technologies and patterns
