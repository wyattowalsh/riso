# Data Model: MCP Server Scaffolds

**Feature**: 013-mcp-servers | **Phase**: 1 (Design) | **Date**: 2025-11-02

## Overview

This document defines the key entities, their attributes, relationships, and validation rules for MCP server scaffolds. These entities are implementation-agnostic and apply to both Python and TypeScript scaffolds.

## Core Entities

### MCPServer

**Description**: The main server instance managing protocol implementation, transport layer, capability registration, and request routing.

**Attributes**:
- `name: string` - Server identifier (alphanumeric + hyphens, max 64 chars)
- `version: string` - Semantic version (MAJOR.MINOR.PATCH format)
- `configuration: MCPConfiguration` - Server settings
- `transport: MCPTransport` - Communication mechanism (STDIO or HTTP)
- `tools: Map<string, MCPTool>` - Registered callable functions
- `resources: Map<string, MCPResource>` - Registered data sources
- `prompts: Map<string, MCPPrompt>` - Registered prompt templates
- `state: ServerState` - Current lifecycle state (initializing, ready, shutting_down, stopped)

**Relationships**:
- HAS-ONE `MCPConfiguration`
- HAS-ONE `MCPTransport`
- HAS-MANY `MCPTool` (registered via decorators/methods)
- HAS-MANY `MCPResource` (registered via decorators/methods)
- HAS-MANY `MCPPrompt` (registered via decorators/methods)

**Validation Rules**:
- `name` must match pattern `^[a-z0-9-]+$`
- `version` must follow semver: `^\d+\.\d+\.\d+$`
- At least one capability (tool, resource, or prompt) must be registered before server can start
- State transitions: initializing → ready → shutting_down → stopped (no skipping states)

**State Diagram**:
```
initializing → ready ⟷ shutting_down → stopped
                ↑________________________↓
              (restart)
```

---

### MCPTool

**Description**: A callable function exposed via MCP protocol with JSON Schema validation and typed responses.

**Attributes**:
- `name: string` - Unique tool identifier (alphanumeric + underscores, max 64 chars)
- `description: string` - Human-readable purpose (max 500 chars)
- `input_schema: JSONSchema` - Parameter validation schema
- `handler: AsyncFunction` - Implementation function (async/await)
- `timeout: number` - Maximum execution time in seconds (default: 30)
- `retry_config: RetryConfig | null` - Optional retry policy for transient failures

**Relationships**:
- BELONGS-TO `MCPServer`
- USES `JSONSchema` for input validation
- RETURNS `ToolResult` (success) or `MCPError` (failure)

**Validation Rules**:
- `name` must match pattern `^[a-z][a-z0-9_]*$` (lowercase, starts with letter)
- `description` required, non-empty
- `input_schema` must be valid JSON Schema Draft 7 or later
- `handler` must be async function (returns Promise)
- `timeout` must be positive integer ≤ 300 (5 minutes)
- Tool names must be unique within server

**Example**:
```
Tool: fetch_url
Description: "Fetch content from a URL with timeout and retry logic"
Input Schema: { url: string (uri format), timeout_seconds: integer (1-60) }
Handler: async (url, timeout) => { /* fetch logic */ }
Timeout: 30 seconds
```

---

### MCPResource

**Description**: A URI-addressable piece of data or content with MIME type specification.

**Attributes**:
- `uri_pattern: string` - URI template with optional parameters (e.g., `file:///{path}`)
- `name: string` - Unique resource identifier
- `description: string` - Human-readable purpose
- `mime_type: string` - Content type (e.g., `application/json`, `text/plain`)
- `fetch_handler: AsyncFunction` - Function to retrieve content
- `is_static: boolean` - Whether content is fixed (true) or computed (false)

**Relationships**:
- BELONGS-TO `MCPServer`
- RETURNS `ResourceContent` (success) or `MCPError` (failure)

**Validation Rules**:
- `uri_pattern` must be valid URI template (RFC 6570)
- `name` must match pattern `^[a-z][a-z0-9_]*$`
- `description` required, non-empty
- `mime_type` must be valid IANA media type
- `fetch_handler` must be async function
- Static resources should cache content (don't recompute on every fetch)
- Resource names must be unique within server

**Example**:
```
Static Resource: about
URI: resource://about
MIME Type: application/json
Content: { "name": "My MCP Server", "version": "1.0.0" }

Dynamic Resource: file_browser
URI: file:///{path}
MIME Type: application/json
Content: Directory listing computed from {path} parameter
```

---

### MCPPrompt

**Description**: A reusable template for LLM interactions with parameter substitution.

**Attributes**:
- `name: string` - Unique prompt identifier
- `description: string` - Human-readable purpose
- `parameters: Map<string, ParameterSpec>` - Template variables with types
- `template: PromptTemplate` - Messages with substitution placeholders
- `examples: List<PromptExample>` - Sample inputs/outputs for documentation

**Relationships**:
- BELONGS-TO `MCPServer`
- USES `ParameterSpec` for type validation
- RETURNS `PromptMessages` (list of system/user/assistant messages)

**Validation Rules**:
- `name` must match pattern `^[a-z][a-z0-9_]*$`
- `description` required, non-empty
- All parameters referenced in template must be defined in `parameters` map
- Parameter types: string, number, boolean, array, object
- Template must contain at least one message (system, user, or assistant)
- Prompt names must be unique within server

**Example**:
```
Prompt: code_review
Description: "Generate a code review with specific focus areas"
Parameters: 
  - code: string (required)
  - language: string (default: "python")
  - focus: array<string> (default: ["security", "performance"])
Template:
  - System: "You are an expert code reviewer..."
  - User: "Review this {language} code focusing on {focus}: {code}"
```

---

### MCPConfiguration

**Description**: Server settings loaded from config file and environment variables.

**Attributes**:
- `server_name: string` - Server identifier
- `server_version: string` - Semantic version
- `log_level: LogLevel` - Logging verbosity (DEBUG|INFO|WARNING|ERROR|CRITICAL)
- `transport_type: TransportType` - Communication mechanism (STDIO|HTTP)
- `http_host: string | null` - HTTP bind address (if transport=HTTP)
- `http_port: number | null` - HTTP port (if transport=HTTP, range 1024-65535)
- `tool_timeout: number` - Default tool timeout in seconds (default: 30)
- `resource_timeout: number` - Default resource timeout in seconds (default: 10)
- `prompt_timeout: number` - Default prompt timeout in seconds (default: 5)
- `max_response_size_mb: number` - Response size limit (default: 100)
- `rate_limit_per_minute: number` - HTTP rate limit (default: 100)
- `rate_limit_burst: number` - HTTP burst allowance (default: 20)
- `profile: string` - Environment profile (development|production)

**Relationships**:
- BELONGS-TO `MCPServer`
- LOADED-FROM config file (TOML/JSON) and environment variables

**Validation Rules**:
- `server_name` and `server_version` required
- `log_level` must be valid enum value
- `transport_type` must be STDIO or HTTP
- If `transport_type=HTTP`: `http_host` and `http_port` required
- `http_port` must be in range 1024-65535 (avoid privileged ports)
- All timeout values must be positive integers
- `max_response_size_mb` must be positive integer
- Rate limit values must be positive integers
- Environment variables override config file (precedence: env > file > defaults)

**Loading Precedence**:
1. Environment variables (`MCP_SERVER_NAME`, `MCP_LOG_LEVEL`, etc.)
2. Config file (`config.toml` or `config.json`)
3. Built-in defaults

---

### MCPTransport

**Description**: Abstraction over communication mechanism (STDIO or HTTP).

**Attributes**:
- `type: TransportType` - STDIO or HTTP
- `state: TransportState` - Current connection state (connecting, connected, disconnected)
- `message_queue: Queue<Message>` - Pending outbound messages
- `correlation_map: Map<string, Promise>` - Request/response correlation

**Relationships**:
- BELONGS-TO `MCPServer`
- SENDS `Message` (JSON-RPC 2.0 format)
- RECEIVES `Message` (JSON-RPC 2.0 format)

**Validation Rules**:
- STDIO transport: Must use stdin for input, stdout for output, stderr for errors
- HTTP transport: Must expose POST endpoints for all MCP methods
- HTTP transport: Must implement SSE endpoint for server-initiated messages
- Messages must be valid JSON-RPC 2.0 format
- Message framing: newline-delimited for STDIO, HTTP chunks for HTTP
- Correlation IDs must be unique per request

**Methods** (Abstract Interface):
- `send_message(message: Message) -> void` - Send JSON-RPC message
- `receive_message() -> Message` - Receive JSON-RPC message (async/blocking)
- `close() -> void` - Gracefully close connection

**STDIO Implementation**:
- Read from stdin line by line (newline-delimited JSON)
- Write to stdout with trailing newline
- Handle EOF gracefully (client disconnection)

**HTTP Implementation**:
- POST `/mcp/{method}` - Method invocation
- GET `/mcp/sse` - Server-Sent Events stream
- CORS headers if configured
- Authentication middleware (Bearer token, API key)

---

## Supporting Types

### ToolResult

**Attributes**:
- `content: List<Content>` - Response content (text, images, etc.)
- `is_error: boolean` - Whether result represents an error

### ResourceContent

**Attributes**:
- `uri: string` - Resource URI
- `mime_type: string` - Content type
- `content: string | bytes` - Actual content
- `size: number` - Content size in bytes

### PromptMessages

**Attributes**:
- `messages: List<Message>` - System/user/assistant messages
- `message: { role: string, content: string }` - Single message structure

### MCPError

**Attributes**:
- `code: number` - JSON-RPC error code
- `message: string` - Error description
- `data: object | null` - Additional error context

**Error Codes**:
- `-32700`: Parse error (invalid JSON)
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000 to -32099`: MCP-specific errors

---

## Entity Lifecycle

### Server Lifecycle
```
1. Load configuration (file + environment)
2. Validate configuration schema
3. Initialize transport layer
4. Register tools, resources, prompts
5. Perform capability negotiation (if client initiates)
6. Enter ready state
7. Process requests
8. On shutdown signal: complete in-flight requests
9. Close transport connections
10. Enter stopped state
```

### Tool Invocation Lifecycle
```
1. Client sends tools/call request
2. Server validates tool name exists
3. Server validates input against JSON Schema
4. Server invokes tool handler (async)
5. Tool executes with timeout
6. On success: return ToolResult
7. On error: catch exception, log, return MCPError
8. Server sends response to client
```

### Resource Fetch Lifecycle
```
1. Client sends resources/read request
2. Server validates URI matches registered pattern
3. Server extracts parameters from URI
4. Server invokes fetch handler with parameters
5. Fetch executes with timeout
6. On success: return ResourceContent
7. On error: catch exception, log, return MCPError
8. Server validates response size ≤ max_response_size_mb
9. Server sends response to client
```

---

## Validation Constraints

### Cross-Entity Constraints

1. **Unique Names**: Tool, resource, and prompt names must be unique across all capability types within a server
2. **Timeout Consistency**: Individual capability timeouts cannot exceed server max timeout (300 seconds)
3. **Transport Compatibility**: STDIO transport doesn't require authentication; HTTP transport must implement auth
4. **Resource Size**: All responses (tool results, resource content) must respect max_response_size_mb limit
5. **Concurrent Execution**: Tools marked as thread-safe can execute concurrently; otherwise, serialized execution

### Configuration Validation

1. **Required Fields**: server_name, server_version, transport_type always required
2. **HTTP Requirements**: If transport=HTTP, must specify http_host and http_port
3. **Rate Limiting**: Only applicable for HTTP transport (ignored for STDIO)
4. **Profile Values**: Must be "development" or "production" (case-sensitive)

### Runtime Constraints

1. **Memory Limits**: Total in-flight requests cannot exceed 100MB memory usage
2. **Concurrent Requests**: Maximum 100 concurrent requests per server instance
3. **Request Queue**: Maximum 1000 queued requests (reject with 503 if exceeded)
4. **Graceful Shutdown**: Maximum 30 seconds to complete in-flight requests before forced termination

---

## Persistence

MCP servers are **stateless** - no database or persistent storage required. Configuration is loaded from files at startup, and all runtime state (registered capabilities, active connections) is held in memory only.

**Exception**: Logs are written to configured output (stdout, file, external logging service) but not used for state recovery.

---

## Relationships Diagram

```
MCPServer (1)
    ├── has one MCPConfiguration
    ├── has one MCPTransport (STDIO or HTTP)
    ├── has many MCPTool (0..n)
    ├── has many MCPResource (0..n)
    └── has many MCPPrompt (0..n)

MCPTool (n)
    ├── belongs to MCPServer
    ├── uses JSONSchema for validation
    └── returns ToolResult or MCPError

MCPResource (n)
    ├── belongs to MCPServer
    └── returns ResourceContent or MCPError

MCPPrompt (n)
    ├── belongs to MCPServer
    ├── uses ParameterSpec for validation
    └── returns PromptMessages

MCPTransport (1)
    ├── belongs to MCPServer
    ├── sends/receives Message (JSON-RPC 2.0)
    └── implementation: STDIOTransport or HTTPTransport

MCPConfiguration (1)
    ├── belongs to MCPServer
    └── loaded from file (TOML/JSON) + environment
```

---

## Implementation Notes

### Python-Specific

- Use `@dataclass` for entity definitions with type hints
- Pydantic models for JSON Schema validation
- FastMCP decorators (`@mcp.tool()`, etc.) register capabilities automatically
- Async/await with `asyncio` for all I/O operations

### TypeScript-Specific

- Use interfaces or `type` for entity definitions
- Zod schemas for runtime validation
- Official SDK provides `Server` class handling capability registration
- Promises for all async operations

### Shared Patterns

- Builder pattern for server configuration
- Factory pattern for transport creation (STDIO vs HTTP)
- Observer pattern for lifecycle events (startup, shutdown)
- Decorator pattern for capability registration
