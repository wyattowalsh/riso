"""
Configuration hot-reload with watchdog (FR-044, Phase 10).

This module provides automatic configuration reloading when the YAML
file changes, useful for development and dynamic configuration updates.
"""

import logging
from pathlib import Path
from typing import Callable, Optional

try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    FileSystemEvent = None

from api_versioning.core.registry import VersionRegistry


logger = logging.getLogger("api_versioning.reliability")


class ConfigReloadHandler:
    """
    File system event handler for configuration hot-reload.
    
    Watches the version configuration file and automatically reloads
    the VersionRegistry when changes are detected.
    
    Example:
        >>> from pathlib import Path
        >>> handler = ConfigReloadHandler(Path("config/api_versions.yaml"))
        >>> handler.on_modified(event)  # Called by watchdog
    """
    
    def __init__(
        self,
        config_path: Path,
        on_reload: Optional[Callable[[], None]] = None
    ):
        """
        Initialize config reload handler.
        
        Args:
            config_path: Path to configuration file
            on_reload: Optional callback after successful reload
        """
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError(
                "watchdog library not installed. "
                "Install with: pip install api-versioning[hotreload]"
            )
        
        self.config_path = config_path.resolve()
        self.on_reload = on_reload
    
    def on_modified(self, event: "FileSystemEvent") -> None:
        """
        Handle file modification event.
        
        Args:
            event: File system event from watchdog
        """
        # Check if the modified file is our config
        event_path = Path(event.src_path).resolve()
        if event_path == self.config_path:
            logger.info(f"Configuration file modified: {self.config_path}")
            self._reload_config()
    
    def _reload_config(self) -> None:
        """Reload configuration with error handling."""
        try:
            # Attempt to reload
            registry = VersionRegistry()
            registry.reload()
            
            logger.info("Configuration reloaded successfully")
            
            # Call callback if provided
            if self.on_reload:
                self.on_reload()
        
        except Exception as e:
            # Log error but continue with previous configuration (FR-044)
            logger.error(
                f"Configuration reload failed: {e}. "
                f"Continuing with previous configuration."
            )


def start_config_watcher(
    config_path: Path,
    on_reload: Optional[Callable[[], None]] = None
) -> Optional["Observer"]:
    """
    Start watching configuration file for changes.
    
    This function starts a background thread that monitors the configuration
    file and automatically reloads it when changes are detected.
    
    Args:
        config_path: Path to configuration file
        on_reload: Optional callback after successful reload
    
    Returns:
        Observer instance if watchdog available, None otherwise
    
    Example:
        >>> from pathlib import Path
        >>> from api_versioning.reliability import start_config_watcher
        >>> 
        >>> config_path = Path("config/api_versions.yaml")
        >>> observer = start_config_watcher(config_path)
        >>> # Configuration will auto-reload on file changes
        >>> # ...
        >>> # Later: stop watching
        >>> if observer:
        ...     observer.stop()
        ...     observer.join()
    """
    if not WATCHDOG_AVAILABLE:
        logger.warning(
            "watchdog library not installed. Hot-reload disabled. "
            "Install with: pip install api-versioning[hotreload]"
        )
        return None
    
    # Create handler
    handler = ConfigReloadHandler(config_path, on_reload)
    
    # Wrap in FileSystemEventHandler for watchdog
    class WatchdogHandler(FileSystemEventHandler):
        def on_modified(self, event):
            handler.on_modified(event)
    
    # Start observer
    observer = Observer()
    observer.schedule(
        WatchdogHandler(),
        str(config_path.parent),
        recursive=False
    )
    observer.start()
    
    logger.info(f"Started configuration hot-reload watcher for {config_path}")
    
    return observer


def stop_config_watcher(observer: Optional["Observer"]) -> None:
    """
    Stop configuration file watcher.
    
    Args:
        observer: Observer instance from start_config_watcher
    
    Example:
        >>> observer = start_config_watcher(config_path)
        >>> # Later...
        >>> stop_config_watcher(observer)
    """
    if observer:
        observer.stop()
        observer.join()
        logger.info("Stopped configuration hot-reload watcher")
