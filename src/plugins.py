"""Plugin system for custom log parsers and processors."""

import importlib
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Type

from .models import LogEntry


class LogPlugin(ABC):
    """Base class for log analyzer plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @abstractmethod
    def process(self, entries: List[LogEntry]) -> List[LogEntry]:
        """Process log entries."""
        pass

    def on_startup(self):
        """Called when plugin is loaded."""
        pass

    def on_shutdown(self):
        """Called when plugin is unloaded."""
        pass


class PluginManager:
    """Manage log analyzer plugins."""

    def __init__(self):
        self._plugins: Dict[str, LogPlugin] = {}
        self._enabled: Dict[str, bool] = {}

    def register(self, plugin: LogPlugin):
        """Register a plugin.

        Args:
            plugin: The plugin instance to register.

        Raises:
            TypeError: If plugin is not a LogPlugin instance.
        """
        if not isinstance(plugin, LogPlugin):
            raise TypeError("plugin must be an instance of LogPlugin")
        if not plugin.name:
            raise ValueError("plugin must have a name")
        self._plugins[plugin.name] = plugin
        self._enabled[plugin.name] = True
        plugin.on_startup()

    def unregister(self, name: str):
        """Unregister a plugin."""
        if name in self._plugins:
            self._plugins[name].on_shutdown()
            del self._plugins[name]
            del self._enabled[name]

    def remove_batch(self, names: List[str]) -> int:
        """Remove multiple plugins at once. Returns count of removed plugins."""
        removed = 0
        for name in names:
            if name in self._plugins:
                self.unregister(name)
                removed += 1
        return removed

    def enable(self, name: str):
        """Enable a plugin."""
        if name in self._enabled:
            self._enabled[name] = True

    def disable(self, name: str):
        """Disable a plugin."""
        if name in self._enabled:
            self._enabled[name] = False

    def get_plugin(self, name: str) -> Optional[LogPlugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def has_plugin(self, name: str) -> bool:
        """Check if a plugin is registered."""
        return name in self._plugins

    def get_version(self, name: str) -> Optional[str]:
        """Get version string for a registered plugin."""
        plugin = self._plugins.get(name)
        return plugin.version if plugin else None

    def list_plugins(self) -> List[Dict[str, str]]:
        """List all registered plugins."""
        return [
            {"name": p.name, "version": p.version, "enabled": self._enabled.get(p.name, False)}
            for p in self._plugins.values()
        ]

    def get_plugin_names(self) -> List[str]:
        """Get list of all registered plugin names."""
        return list(self._plugins.keys())

    def process_all(self, entries: List[LogEntry]) -> List[LogEntry]:
        """Run all enabled plugins on entries."""
        result = entries
        for name, plugin in self._plugins.items():
            if self._enabled.get(name, False):
                result = plugin.process(result)
        return result

    @property
    def stats(self) -> Dict[str, int]:
        """Get plugin manager statistics."""
        enabled_count = sum(1 for v in self._enabled.values() if v)
        return {
            "total": len(self._plugins),
            "enabled": enabled_count,
            "disabled": len(self._plugins) - enabled_count,
        }

    def load_from_directory(self, directory: str):
        """Load plugins from a directory."""
        plugin_dir = Path(directory)
        if not plugin_dir.exists():
            return
        for file in plugin_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            module_name = file.stem
            spec = importlib.util.spec_from_file_location(module_name, str(file))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and issubclass(attr, LogPlugin)
                            and attr is not LogPlugin):
                        self.register(attr())
