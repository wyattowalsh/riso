"""Entry point for running riso.mcp as a module.

Usage:
    python -m riso.mcp [options]
    uv run python -m riso.mcp [options]
"""

from __future__ import annotations

from .server import main

if __name__ == "__main__":
    main()
