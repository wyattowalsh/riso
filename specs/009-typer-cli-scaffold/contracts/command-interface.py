"""Command Interface Contract

This module defines the interface that all CLI commands must implement.
"""

from typing import Protocol, Any, Dict, List, Optional
from pathlib import Path


class CommandProtocol(Protocol):
    """Protocol defining the interface for CLI commands."""
    
    name: str
    """Command name as invoked in the CLI"""
    
    help_text: str
    """Help text displayed in --help output"""
    
    def execute(self, **kwargs: Any) -> int:
        """Execute the command with provided parameters.
        
        Args:
            **kwargs: Command parameters as key-value pairs
            
        Returns:
            Exit code (0 for success, non-zero for failure)
            
        Raises:
            CLIError: For application-level errors
            ValueError: For invalid parameter values
        """
        ...
    
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        """Validate command parameters before execution.
        
        Args:
            params: Parameter dict to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        ...


class AsyncCommandProtocol(Protocol):
    """Protocol for async CLI commands."""
    
    name: str
    help_text: str
    
    async def execute(self, **kwargs: Any) -> int:
        """Async execution of the command."""
        ...
    
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        """Validate command parameters."""
        ...


class CommandGroupProtocol(Protocol):
    """Protocol for command groups (e.g., 'config' with subcommands)."""
    
    name: str
    """Group name"""
    
    help_text: str
    """Group description"""
    
    commands: Dict[str, CommandProtocol]
    """Mapping of command name to command instance"""
    
    def add_command(self, command: CommandProtocol) -> None:
        """Register a command in this group."""
        ...
    
    def get_command(self, name: str) -> Optional[CommandProtocol]:
        """Retrieve command by name."""
        ...


# Example implementation
class BaseCommand:
    """Base class implementing CommandProtocol."""
    
    def __init__(self, name: str, help_text: str):
        self.name = name
        self.help_text = help_text
    
    def execute(self, **kwargs: Any) -> int:
        """Default implementation - subclasses override."""
        raise NotImplementedError(
            f"Command {self.name} must implement execute()"
        )
    
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        """Default validation - subclasses can override."""
        return []


# Contract validation
def validate_command(command: Any) -> bool:
    """Validate that an object implements CommandProtocol.
    
    Args:
        command: Object to validate
        
    Returns:
        True if valid command, False otherwise
    """
    required_attrs = ["name", "help_text", "execute", "validate_params"]
    return all(hasattr(command, attr) for attr in required_attrs)
