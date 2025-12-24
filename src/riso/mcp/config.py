"""MCP Server configuration with Pydantic models.

Supports environment variables, config files, and defaults.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TimeoutConfig(BaseModel):
    """Operation timeout settings in seconds."""

    tool: int = Field(default=30, ge=1, le=300, description="Tool operation timeout")
    resource: int = Field(default=10, ge=1, le=60, description="Resource fetch timeout")
    prompt: int = Field(default=5, ge=1, le=30, description="Prompt render timeout")
    copier_copy: int = Field(
        default=120, ge=30, le=600, description="Copier copy timeout"
    )


class WizardConfig(BaseModel):
    """Interactive wizard settings."""

    session_ttl_minutes: int = Field(
        default=60, ge=5, le=1440, description="Session TTL in minutes"
    )
    max_sessions: int = Field(
        default=100, ge=1, le=1000, description="Max concurrent sessions"
    )
    auto_cleanup_interval: int = Field(
        default=300, ge=60, le=3600, description="Cleanup interval in seconds"
    )


class ServerConfig(BaseSettings):
    """Main server configuration.

    Load order: defaults < config file < environment variables
    """

    model_config = SettingsConfigDict(
        env_prefix="RISO_MCP_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Server identity
    name: str = Field(default="riso-mcp", description="Server name")
    version: str = Field(default="1.0.0", description="Server version")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # Paths
    template_path: Path = Field(
        default=Path(__file__).parent.parent.parent.parent / "template",
        description="Path to Copier template",
    )
    samples_path: Path = Field(
        default=Path(__file__).parent.parent.parent.parent / "samples",
        description="Path to sample projects",
    )

    # Transport
    transport: Literal["stdio", "http", "sse"] = Field(default="stdio")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=3000, ge=1024, le=65535)

    # Limits
    max_response_size_mb: int = Field(default=100, ge=1, le=500)

    # Sub-configs
    timeouts: TimeoutConfig = Field(default_factory=TimeoutConfig)
    wizard: WizardConfig = Field(default_factory=WizardConfig)

    @field_validator("template_path", "samples_path", mode="before")
    @classmethod
    def resolve_path(cls, v: str | Path) -> Path:
        """Resolve and validate paths."""
        path = Path(v).expanduser().resolve()
        return path

    @property
    def is_remote(self) -> bool:
        """Check if using remote transport."""
        return self.transport != "stdio"


@lru_cache
def get_config() -> ServerConfig:
    """Get cached server configuration."""
    return ServerConfig()


def load_config(config_path: Path | None = None) -> ServerConfig:
    """Load server configuration from file and environment.

    Parameters
    ----------
    config_path
        Optional path to TOML config file

    Returns
    -------
    ServerConfig
        Validated configuration
    """
    if config_path is None:
        # Check standard locations
        candidates = [
            Path.cwd() / "riso-mcp.toml",
            Path.cwd() / ".riso" / "mcp.toml",
            Path.home() / ".config" / "riso" / "mcp.toml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = candidate
                break

    config_data: dict = {}
    if config_path and config_path.exists():
        try:
            import tomli

            with open(config_path, "rb") as f:
                config_data = tomli.load(f)
        except ImportError:
            pass  # tomli not available, use defaults

    return ServerConfig(**config_data)
