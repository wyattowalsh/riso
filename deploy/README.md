# Riso MCP Server

The Riso MCP server can be accessed three ways:

## Option 1: HTTP URL (Easiest)

Add to your MCP client config (Cursor, VS Code Copilot, etc.):

```json
{
  "mcpServers": {
    "riso": {
      "url": "https://riso.dev/mcp"
    }
  }
}
```

## Option 2: uvx (Local, no install)

```json
{
  "mcpServers": {
    "riso": {
      "command": "uvx",
      "args": ["--from", "riso", "riso-mcp"]
    }
  }
}
```

## Option 3: uv (From cloned repo)

```json
{
  "mcpServers": {
    "riso": {
      "command": "uv",
      "args": ["run", "--group", "mcp", "riso-mcp"]
    }
  }
}
```

## Self-Hosting

### Docker

```bash
docker build -t riso-mcp -f deploy/Dockerfile .
docker run -p 8080:8080 riso-mcp
```

### Fly.io

```bash
cd deploy
fly launch --name my-riso-mcp
fly deploy
```

### Direct

```bash
uv run --group mcp riso-mcp --transport http --port 8080
```
