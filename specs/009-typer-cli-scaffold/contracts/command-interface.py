"""Command Interface Contract — Typer-first CLI model.

Rendered projects use Typer callbacks decorated with ``@command()`` from
``cli.core.base``. Class-based ``CommandProtocol`` remains available for
advanced or legacy patterns but is not required for scaffolded commands.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol, TypedDict


class CommandMetadata(TypedDict, total=False):
    """Metadata attached by the ``@command()`` decorator."""

    name: str
    help: str
    aliases: list[str]
    hidden: bool


class TyperCommandProtocol(Protocol):
    """Protocol for Typer command callables with CLI metadata."""

    _cli_command: bool
    _cli_name: str
    _cli_help: str
    _cli_aliases: list[str]
    _cli_hidden: bool

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


class CommandGroupProtocol(Protocol):
    """Protocol for Typer sub-apps mounted via ``app.add_typer()``."""

    name: str
    help: str


def is_typer_command(func: Any) -> bool:
    """Return True when ``func`` carries ``@command()`` metadata."""
    return getattr(func, "_cli_command", False) is True


def get_command_metadata(func: Callable[..., Any]) -> CommandMetadata:
    """Extract CLI metadata from a decorated command function."""
    if not is_typer_command(func):
        return {}
    return {
        "name": getattr(func, "_cli_name", func.__name__),
        "help": getattr(func, "_cli_help", ""),
        "aliases": list(getattr(func, "_cli_aliases", [])),
        "hidden": bool(getattr(func, "_cli_hidden", False)),
    }
