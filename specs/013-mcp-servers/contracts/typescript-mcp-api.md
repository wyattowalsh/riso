# TypeScript MCP API Contract

**Feature**: 013-mcp-servers | **Language**: TypeScript | **Date**: 2025-11-02

## Overview

This document defines the API contract for TypeScript MCP servers using the official `@modelcontextprotocol/sdk`. It specifies the expected interfaces, method signatures, and behavior for all MCP protocol operations.

## Server Initialization

### Server Class

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

// Create server instance
const server = new Server(
  {
    name: string,           // Server identifier (required)
    version: string,        // Semantic version (required)
    description?: string    // Server description (optional)
  },
  {
    capabilities: {
      tools: {},            // Enable tool capability
      resources: {},        // Enable resource capability
      prompts: {}           // Enable prompt capability
    }
  }
);
```

**Contract**:

- Server name must match `^[a-z0-9-]+$`
- Version must follow semver format `^\d+\.\d+\.\d+$`
- Capabilities declared at initialization
- Server instance is singleton per process

---

## Tool Registration

### Tool Handler

```typescript
import { z } from "zod";

// Define input schema with Zod
const EchoInputSchema = z.object({
  message: z.string().describe("Message to echo back"),
  uppercase: z.boolean().optional().describe("Convert to uppercase")
});

// List tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "echo",
      description: "Echo the input message back to the caller",
      inputSchema: zodToJsonSchema(EchoInputSchema)
    }
  ]
}));

// Call tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === "echo") {
    // Validate input
    const parsed = EchoInputSchema.parse(args);
    
    // Execute tool logic
    const result = parsed.uppercase 
      ? parsed.message.toUpperCase()
      : parsed.message;
    
    return {
      content: [
        {
          type: "text",
          text: result
        }
      ]
    };
  }
  
  throw new Error(`Unknown tool: ${name}`);
});
```

**Contract**:

- Tools listed via `ListToolsRequestSchema` handler
- Tool invocation via `CallToolRequestSchema` handler
- Input validation with Zod schemas (converted to JSON Schema)
- Tool name must match `^[a-z][a-z0-9_]*$`
- Response format: `{ content: Array<{ type: string, text?: string, ... }> }`
- Throw `Error` for business logic failures (converted to MCP error)
- Async handlers required

### Complex Tool Example

```typescript
const FetchUrlInputSchema = z.object({
  url: z.string().url().describe("URL to fetch"),
  timeout: z.number().int().min(1000).max(30000).optional().default(5000).describe("Timeout in milliseconds"),
  headers: z.record(z.string()).optional().describe("HTTP headers")
});

type FetchUrlInput = z.infer<typeof FetchUrlInputSchema>;

async function fetchUrl(input: FetchUrlInput): Promise<string> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), input.timeout);
  
  try {
    const response = await fetch(input.url, {
      headers: input.headers,
      signal: controller.signal
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.text();
  } finally {
    clearTimeout(timeoutId);
  }
}

// Register in CallToolRequestSchema handler
if (name === "fetch_url") {
  const parsed = FetchUrlInputSchema.parse(args);
  const content = await fetchUrl(parsed);
  
  return {
    content: [
      { type: "text", text: content }
    ]
  };
}
```

**Contract**:

- Zod schemas provide type safety and validation
- Use `z.infer<typeof Schema>` for TypeScript types
- Handle timeouts with `AbortController`
- Return structured content (text, image, resource reference)
- Log errors server-side, return sanitized messages

---

## Resource Registration

### Resource Handler

```typescript
import { ListResourcesRequestSchema, ReadResourceRequestSchema } from "@modelcontextprotocol/sdk/types.js";

// List resources handler
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "resource://about",
      name: "Server Information",
      description: "Details about this MCP server",
      mimeType: "application/json"
    }
  ]
}));

// Read resource handler
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;
  
  if (uri === "resource://about") {
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify({
            name: "example-server",
            version: "1.0.0",
            capabilities: ["tools", "resources", "prompts"]
          }, null, 2)
        }
      ]
    };
  }
  
  throw new Error(`Unknown resource: ${uri}`);
});
```

**Contract**:

- Resources listed via `ListResourcesRequestSchema` handler
- Resource content via `ReadResourceRequestSchema` handler
- URI must be valid (e.g., `resource://name`, `file:///{path}`)
- Response: `{ contents: Array<{ uri, mimeType, text?, blob? }> }`
- MimeType: `application/json`, `text/plain`, `image/png`, etc.
- Text content: UTF-8 string
- Binary content: base64 in `blob` field

### Dynamic Resource with Parameters

```typescript
// List resources with URI template
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "file:///{path}",
      name: "File Browser",
      description: "Browse files at the specified path",
      mimeType: "application/json"
    }
  ]
}));

// Read resource with parameter extraction
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;
  
  const fileMatch = uri.match(/^file:\/\/\/(.+)$/);
  if (fileMatch) {
    const path = fileMatch[1];
    
    // Validate path (security critical!)
    if (!isPathAllowed(path)) {
      throw new Error("Access denied");
    }
    
    const files = await fs.readdir(path);
    
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify({ path, files }, null, 2)
        }
      ]
    };
  }
  
  throw new Error(`Unknown resource: ${uri}`);
});
```

**Contract**:

- Extract parameters from URI via regex matching
- Validate all parameters (security critical for file paths)
- Return appropriate mime type for content
- Handle errors gracefully (don't leak system paths)

---

## Prompt Registration

### Prompt Handler

```typescript
import { ListPromptsRequestSchema, GetPromptRequestSchema } from "@modelcontextprotocol/sdk/types.js";

// List prompts handler
server.setRequestHandler(ListPromptsRequestSchema, async () => ({
  prompts: [
    {
      name: "greeting",
      description: "Generate a friendly greeting",
      arguments: [
        {
          name: "name",
          description: "Name of the person to greet",
          required: false
        }
      ]
    }
  ]
}));

// Get prompt handler
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === "greeting") {
    const personName = args?.name || "friend";
    
    return {
      messages: [
        {
          role: "system",
          content: {
            type: "text",
            text: "You are a friendly assistant."
          }
        },
        {
          role: "user",
          content: {
            type: "text",
            text: `Greet ${personName} warmly.`
          }
        }
      ]
    };
  }
  
  throw new Error(`Unknown prompt: ${name}`);
});
```

**Contract**:

- Prompts listed via `ListPromptsRequestSchema` handler
- Prompt content via `GetPromptRequestSchema` handler
- Arguments: name, description, required boolean
- Response: `{ messages: Array<{ role, content }> }`
- Roles: `"system"`, `"user"`, `"assistant"`
- Content: structured object with type and text/data fields

---

## Error Handling

### MCP Error Response

```typescript
import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === "risky_operation") {
    // Validate input
    if (!args.param) {
      throw new McpError(
        ErrorCode.InvalidParams,
        "Parameter 'param' is required",
        { param: "param" }
      );
    }
    
    try {
      const result = await performOperation(args.param);
      return { content: [{ type: "text", text: result }] };
    } catch (error) {
      // Log full error server-side
      logger.error("Operation failed", { error, tool: name });
      
      // Return sanitized error to client
      throw new McpError(
        ErrorCode.InternalError,
        "Operation failed",
        { hint: "Check server logs" }
      );
    }
  }
  
  throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
});
```

**Contract**:

- Use `McpError` for expected/business logic errors
- Error codes (from SDK):
  - `ErrorCode.ParseError` (-32700)
  - `ErrorCode.InvalidRequest` (-32600)
  - `ErrorCode.MethodNotFound` (-32601)
  - `ErrorCode.InvalidParams` (-32602)
  - `ErrorCode.InternalError` (-32603)
- Uncaught errors converted to InternalError automatically
- Production: Never send stack traces to client (log only)

---

## Configuration

### Loading Configuration

```typescript
import fs from "fs/promises";
import path from "path";

interface ServerConfig {
  server: {
    name: string;
    version: string;
    logLevel: "debug" | "info" | "warn" | "error";
  };
  transport: {
    type: "stdio" | "http";
    host?: string;
    port?: number;
  };
  timeouts: {
    tool: number;
    resource: number;
    prompt: number;
  };
  limits: {
    maxResponseSizeMb: number;
    rateLimitPerMinute?: number;
    rateLimitBurst?: number;
  };
}

async function loadConfig(configPath: string = "config.json"): Promise<ServerConfig> {
  const content = await fs.readFile(configPath, "utf-8");
  const config = JSON.parse(content) as ServerConfig;
  
  // Override with environment variables
  if (process.env.MCP_LOG_LEVEL) {
    config.server.logLevel = process.env.MCP_LOG_LEVEL as any;
  }
  
  return config;
}
```

**Contract**:

- Configuration file: `config.json` (JSON format)
- Environment variables override file settings
- Prefix: `MCP_SERVER_*` or `MCP_*`
- Validation: Zod schema recommended for type safety

### Configuration Schema

```json
{
  "server": {
    "name": "my-mcp-server",
    "version": "1.0.0",
    "logLevel": "info"
  },
  "transport": {
    "type": "stdio"
  },
  "timeouts": {
    "tool": 30,
    "resource": 10,
    "prompt": 5
  },
  "limits": {
    "maxResponseSizeMb": 100,
    "rateLimitPerMinute": 100,
    "rateLimitBurst": 20
  }
}
```

**Contract**:

- All sections optional (defaults provided)
- JSON syntax: valid JSON file required
- Validation: Server fails fast on startup if invalid

---

## Transport

### STDIO Transport (Default)

```typescript
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

// Create transport
const transport = new StdioServerTransport();

// Connect server
await server.connect(transport);

// Server now reads from stdin, writes to stdout
```

**Contract**:

- Stdin: newline-delimited JSON-RPC messages
- Stdout: newline-delimited JSON-RPC responses
- Stderr: Logs (not part of protocol)
- EOF on stdin triggers graceful shutdown

### HTTP/SSE Transport

```typescript
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import express from "express";

const app = express();

app.post("/mcp/tools/call", async (req, res) => {
  const transport = new SSEServerTransport("/mcp/sse", res);
  await server.connect(transport);
  
  // Handle request
  // ...
});

app.listen(8000, "0.0.0.0", () => {
  console.log("MCP server listening on http://0.0.0.0:8000");
});
```

**Contract**:

- HTTP endpoints:
  - `POST /mcp/tools/call` - Invoke tool
  - `POST /mcp/resources/read` - Fetch resource
  - `POST /mcp/prompts/get` - Get prompt
  - `GET /mcp/sse` - Server-Sent Events stream
- Request body: JSON-RPC 2.0 message
- Response: JSON-RPC 2.0 response
- CORS: Configure via Express middleware
- Auth: Middleware for Bearer tokens/API keys

---

## Logging

### Structured Logging

```typescript
interface Logger {
  debug(message: string, context?: Record<string, any>): void;
  info(message: string, context?: Record<string, any>): void;
  warn(message: string, context?: Record<string, any>): void;
  error(message: string, context?: Record<string, any>): void;
}

class ConsoleLogger implements Logger {
  constructor(private level: string = "info") {}
  
  private log(level: string, message: string, context?: Record<string, any>) {
    if (this.shouldLog(level)) {
      const timestamp = new Date().toISOString();
      const data = context ? ` ${JSON.stringify(context)}` : "";
      console.error(`${timestamp} | ${level.toUpperCase()} | ${message}${data}`);
    }
  }
  
  private shouldLog(level: string): boolean {
    const levels = ["debug", "info", "warn", "error"];
    return levels.indexOf(level) >= levels.indexOf(this.level);
  }
  
  debug(message: string, context?: Record<string, any>) { this.log("debug", message, context); }
  info(message: string, context?: Record<string, any>) { this.log("info", message, context); }
  warn(message: string, context?: Record<string, any>) { this.log("warn", message, context); }
  error(message: string, context?: Record<string, any>) { this.log("error", message, context); }
}

const logger = new ConsoleLogger(process.env.MCP_LOG_LEVEL || "info");

// Usage in handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  logger.info("Tool invoked", { tool: name, args });
  
  // ...
  
  logger.info("Tool completed", { tool: name, result });
  return result;
});
```

**Contract**:

- Log to stderr (stdout reserved for MCP protocol)
- Log levels: debug, info, warn, error
- Structured logs: Include context object
- Production: info level, JSON format
- Development: debug level, human-readable format
- Required fields: timestamp, level, message, correlation_id (if applicable)

---

## Testing

### Unit Test Example

```typescript
import { describe, it, expect, beforeEach } from "vitest";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";

describe("MCP Server", () => {
  let server: Server;
  
  beforeEach(() => {
    server = new Server(
      { name: "test-server", version: "1.0.0" },
      { capabilities: { tools: {} } }
    );
    
    // Register test tool
    server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name === "echo") {
        return {
          content: [
            { type: "text", text: request.params.arguments.message }
          ]
        };
      }
      throw new Error("Unknown tool");
    });
  });
  
  it("should echo message", async () => {
    const handler = server.getRequestHandler(CallToolRequestSchema);
    const result = await handler({
      method: "tools/call",
      params: {
        name: "echo",
        arguments: { message: "hello" }
      }
    });
    
    expect(result.content[0].text).toBe("hello");
  });
});
```

**Contract**:

- Use vitest for testing
- Mock external dependencies (fetch, file system)
- Test handler logic in isolation (no transport layer)
- Integration tests use real STDIO pipes or HTTP requests

---

## Lifecycle Hooks

### Server Lifecycle

```typescript
// Startup hook
server.onclose = async () => {
  logger.info("Server shutting down");
  // Close connections, save state, etc.
  await cleanup();
};

// Error hook
server.onerror = (error) => {
  logger.error("Server error", { error });
};

// Start server
async function start() {
  logger.info("Server starting");
  // Initialize connections, load resources, etc.
  await initialize();
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

start().catch((error) => {
  logger.error("Failed to start server", { error });
  process.exit(1);
});
```

**Contract**:

- `onclose`: Called during graceful shutdown
- `onerror`: Called for unhandled errors
- Both hooks optional
- Exceptions in hooks are logged but don't prevent shutdown

---

## Performance Requirements

From specification and clarifications:

**Timeouts**:

- Tool operations: 30 seconds default (configurable)
- Resource fetches: 10 seconds default
- Prompt rendering: 5 seconds default

**Size Limits**:

- Response size: 100MB maximum (configurable via `maxResponseSizeMb`)
- Memory: <100MB per in-flight request

**Concurrency**:

- Handle 100 concurrent requests without errors (SC-007)
- Rate limiting (HTTP only): 100 requests/minute, burst of 20

**Startup**:

- Server ready within 5 seconds of launch

---

## Example Complete Server

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

// Create server
const server = new Server(
  { name: "example-server", version: "1.0.0" },
  { capabilities: { tools: {}, resources: {} } }
);

// Tool
const EchoSchema = z.object({
  message: z.string().describe("Message to echo")
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "echo",
      description: "Echo the input message",
      inputSchema: zodToJsonSchema(EchoSchema)
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "echo") {
    const { message } = EchoSchema.parse(request.params.arguments);
    return { content: [{ type: "text", text: message }] };
  }
  throw new Error("Unknown tool");
});

// Resource
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "resource://about",
      name: "About",
      mimeType: "application/json"
    }
  ]
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  if (request.params.uri === "resource://about") {
    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: "application/json",
          text: JSON.stringify({ name: "example-server" })
        }
      ]
    };
  }
  throw new Error("Unknown resource");
});

// Start
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP server running");
}

main().catch(console.error);
```

This contract defines all required interfaces for TypeScript MCP servers and ensures consistency across implementations.
