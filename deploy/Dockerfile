FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --group mcp --frozen

# Expose port
ENV PORT=8080
EXPOSE 8080

# Run MCP server with HTTP transport
CMD ["uv", "run", "--group", "mcp", "riso-mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "8080"]
