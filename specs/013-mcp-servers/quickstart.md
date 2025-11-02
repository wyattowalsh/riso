# MCP Server Quickstart

**Feature**: 013-mcp-servers | **Last Updated**: 2025-11-02

## Overview

This guide walks you through creating your first MCP (Model Context Protocol) server using the riso template. You'll scaffold a server in either Python or TypeScript, implement a simple tool, and integrate it with Claude Desktop.

**What you'll build**: An MCP server with a custom tool that Claude can invoke to extend its capabilities.

**Time estimate**: 15-20 minutes

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** with `uv` installed (`uv --version`)
- **Node.js 20 LTS** with `pnpm` installed (`node --version`, `pnpm --version`)
- **Copier** CLI installed (`copier --version`)
- **Claude Desktop** application ([download here](https://claude.ai/download))

---

## Step 1: Generate Your MCP Server

### Python Server

```bash
# Create a new project directory
mkdir my-mcp-server && cd my-mcp-server

# Run Copier to scaffold Python MCP server
copier copy gh:your-org/riso . \
  --vcs-ref main \
  --data mcp_module=enabled \
  --data mcp_language=python

# Initialize the project
uv sync
```

### TypeScript Server

```bash
# Create a new project directory
mkdir my-mcp-server && cd my-mcp-server

# Run Copier to scaffold TypeScript MCP server
copier copy gh:your-org/riso . \
  --vcs-ref main \
  --data mcp_module=enabled \
  --data mcp_language=typescript

# Initialize the project
pnpm install
```

**What just happened?**

- Created a complete MCP server project structure
- Generated configuration files for your chosen language
- Set up testing and quality tools
- Provided example tools, resources, and prompts

---

## Step 2: Explore the Project Structure

### Python Structure

```text
my-mcp-server/
├── src/my_mcp_server/
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py          # Main server instance
│   │   ├── tools.py            # Tool implementations
│   │   ├── resources.py        # Resource handlers
│   │   └── prompts.py          # Prompt templates
│   └── config.toml             # Server configuration
├── tests/
│   └── test_mcp.py             # Unit tests
└── pyproject.toml              # Project metadata
```

### TypeScript Structure

```text
my-mcp-server/
├── src/mcp/
│   ├── server.ts               # Main server instance
│   ├── tools.ts                # Tool implementations
│   ├── resources.ts            # Resource handlers
│   └── prompts.ts              # Prompt templates
├── config.json                 # Server configuration
├── tests/
│   └── mcp.test.ts             # Unit tests
└── package.json                # Project metadata
```

---

## Step 3: Implement Your First Tool

Let's create a tool that fetches the current weather (simulated for this example).

### Python Implementation

Edit `src/my_mcp_server/mcp/tools.py`:

```python
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from loguru import logger

class WeatherInput(BaseModel):
    """Input for weather tool."""
    city: str = Field(..., description="City name to fetch weather for")
    units: str = Field("celsius", description="Temperature units: celsius or fahrenheit")

@mcp.tool()
async def get_weather(input: WeatherInput) -> dict:
    """
    Get current weather for a city.
    
    This is a simulated tool for demonstration purposes.
    """
    logger.info(f"Fetching weather for {input.city}")
    
    # Simulated weather data
    weather_data = {
        "city": input.city,
        "temperature": 22 if input.units == "celsius" else 72,
        "units": input.units,
        "condition": "sunny",
        "humidity": 65
    }
    
    return weather_data
```

### TypeScript Implementation

Edit `src/mcp/tools.ts`:

```typescript
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { server } from "./server.js";

const WeatherInputSchema = z.object({
  city: z.string().describe("City name to fetch weather for"),
  units: z.enum(["celsius", "fahrenheit"]).default("celsius").describe("Temperature units")
});

// Update tools list
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "get_weather",
      description: "Get current weather for a city",
      inputSchema: zodToJsonSchema(WeatherInputSchema)
    }
  ]
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === "get_weather") {
    const { city, units } = WeatherInputSchema.parse(args);
    
    logger.info(`Fetching weather for ${city}`);
    
    // Simulated weather data
    const weatherData = {
      city,
      temperature: units === "celsius" ? 22 : 72,
      units,
      condition: "sunny",
      humidity: 65
    };
    
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(weatherData, null, 2)
        }
      ]
    };
  }
  
  throw new Error(`Unknown tool: ${name}`);
});
```

---

## Step 4: Test Your Tool Locally

### Python Testing

```bash
# Run unit tests
uv run pytest tests/test_mcp.py -v

# Test tool directly
uv run python -c "
from my_mcp_server.mcp.tools import get_weather, WeatherInput
import asyncio

result = asyncio.run(get_weather(WeatherInput(city='San Francisco')))
print(result)
"
```

### TypeScript Testing

```bash
# Run unit tests
pnpm test

# Test tool directly (create a test script)
node --loader ts-node/esm -e "
import { WeatherInputSchema } from './src/mcp/tools.js';
const result = WeatherInputSchema.parse({ city: 'San Francisco' });
console.log(result);
"
```

---

## Step 5: Run Your MCP Server

### Python Server

```bash
# Start server with STDIO transport
uv run python -m my_mcp_server.mcp.server

# Server is now listening on stdin/stdout
# Press Ctrl+C to stop
```

### TypeScript Server

```bash
# Start server with STDIO transport
pnpm start

# Server is now listening on stdin/stdout
# Press Ctrl+C to stop
```

---

## Step 6: Integrate with Claude Desktop

### Configure Claude Desktop

Edit Claude Desktop's configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

### Python Configuration

```json
{
  "mcpServers": {
    "my-weather-server": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "my_mcp_server.mcp.server"
      ],
      "cwd": "/absolute/path/to/my-mcp-server"
    }
  }
}
```

### TypeScript Configuration

```json
{
  "mcpServers": {
    "my-weather-server": {
      "command": "node",
      "args": [
        "dist/mcp/server.js"
      ],
      "cwd": "/absolute/path/to/my-mcp-server"
    }
  }
}
```

**Important**: Replace `/absolute/path/to/my-mcp-server` with your actual project path.

---

## Step 7: Test in Claude Desktop

1. **Restart Claude Desktop** to load the new MCP server configuration

2. **Verify server is connected**:
   - Open Claude Desktop
   - Look for the 🔌 (plug) icon in the bottom-left
   - Click it to see connected MCP servers
   - You should see "my-weather-server" listed

3. **Test your tool**:
   - Start a new conversation
   - Type: "What's the weather in San Francisco?"
   - Claude will invoke your `get_weather` tool
   - You should see the simulated weather response

---

## Step 8: Add More Capabilities

### Add a Resource

Resources provide data that Claude can read.

**Python** (`src/my_mcp_server/mcp/resources.py`):

```python
@mcp.resource("resource://weather/cities")
async def available_cities() -> dict:
    """List of cities with weather data available."""
    return {
        "cities": ["San Francisco", "New York", "London", "Tokyo"]
    }
```

**TypeScript** (`src/mcp/resources.ts`):

```typescript
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "resource://weather/cities",
      name: "Available Cities",
      description: "List of cities with weather data",
      mimeType: "application/json"
    }
  ]
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  if (request.params.uri === "resource://weather/cities") {
    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: "application/json",
          text: JSON.stringify({
            cities: ["San Francisco", "New York", "London", "Tokyo"]
          })
        }
      ]
    };
  }
  throw new Error("Unknown resource");
});
```

### Add a Prompt

Prompts provide templates for common LLM interactions.

**Python** (`src/my_mcp_server/mcp/prompts.py`):

```python
from fastmcp import Message

@mcp.prompt()
async def weather_report(city: str) -> list[Message]:
    """Generate a detailed weather report for a city."""
    return [
        Message(role="system", content="You are a meteorologist providing detailed weather reports."),
        Message(role="user", content=f"Provide a detailed weather report for {city}, including temperature, conditions, and forecast.")
    ]
```

**TypeScript** (`src/mcp/prompts.ts`):

```typescript
server.setRequestHandler(ListPromptsRequestSchema, async () => ({
  prompts: [
    {
      name: "weather_report",
      description: "Generate a detailed weather report",
      arguments: [
        {
          name: "city",
          description: "City name",
          required: true
        }
      ]
    }
  ]
}));

server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  if (request.params.name === "weather_report") {
    const city = request.params.arguments?.city || "a city";
    
    return {
      messages: [
        {
          role: "system",
          content: {
            type: "text",
            text: "You are a meteorologist providing detailed weather reports."
          }
        },
        {
          role: "user",
          content: {
            type: "text",
            text: `Provide a detailed weather report for ${city}, including temperature, conditions, and forecast.`
          }
        }
      ]
    };
  }
  throw new Error("Unknown prompt");
});
```

---

## Step 9: Production Configuration

Edit your configuration file for production settings:

### Python (`config.toml`)

```toml
[server]
name = "my-weather-server"
version = "1.0.0"
log_level = "INFO"

[transport]
type = "stdio"

[timeouts]
tool = 30
resource = 10
prompt = 5

[limits]
max_response_size_mb = 100
```

### TypeScript (`config.json`)

```json
{
  "server": {
    "name": "my-weather-server",
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
    "maxResponseSizeMb": 100
  }
}
```

---

## Troubleshooting

### Server Not Connecting

**Check logs**:
- Python: Logs written to stderr (check terminal output)
- TypeScript: Logs written to stderr (check terminal output)

**Verify configuration**:
- Ensure absolute paths in `claude_desktop_config.json`
- Confirm server starts manually before testing in Claude

### Tool Not Appearing

**Verify tool registration**:
- Python: Check `@mcp.tool()` decorator is present
- TypeScript: Ensure tool listed in `ListToolsRequestSchema` handler

**Check input schema**:
- Python: Pydantic model must have `Field` descriptions
- TypeScript: Zod schema must have `.describe()` calls

### Performance Issues

**Increase timeouts** if operations are slow:
- Edit `config.toml` (Python) or `config.json` (TypeScript)
- Increase `tool`, `resource`, or `prompt` timeout values

**Add caching** for expensive operations:
- Python: Use `functools.lru_cache` or Redis
- TypeScript: Use Map/WeakMap or Redis

---

## Next Steps

Congratulations! You've built and deployed your first MCP server. Here are some ideas to extend it:

1. **Connect to real APIs**: Replace simulated weather with a real weather API (OpenWeatherMap, WeatherAPI, etc.)

2. **Add authentication**: Implement API key validation for HTTP transport

3. **Build complex tools**: Chain multiple tool calls, use LLM agents, integrate databases

4. **Deploy to production**: Use HTTP/SSE transport for cloud deployment, add rate limiting and monitoring

5. **Contribute examples**: Share your MCP server with the community

---

## Resources

- **MCP Specification**: [modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification/2025-11-05/)
- **FastMCP Documentation**: [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **TypeScript SDK**: [github.com/modelcontextprotocol/typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk)
- **MCP Inspector**: Tool for testing MCP servers locally
- **Claude Desktop**: [claude.ai/download](https://claude.ai/download)

---

## Support

For questions or issues:

- Check the [riso template documentation](https://github.com/your-org/riso/tree/main/docs)
- Review the [MCP specification](https://modelcontextprotocol.io)
- Open an issue on the [riso repository](https://github.com/your-org/riso/issues)

Happy building! 🚀
