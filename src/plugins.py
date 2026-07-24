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

    def __repr__(self) -> str:
        enabled = sum(1 for v in self._enabled.values() if v)
        return f"PluginManager(plugins={len(self._plugins)}, enabled={enabled})"

    def __len__(self) -> int:
        """Get number of registered plugins."""
        return len(self._plugins)

    def __contains__(self, name: str) -> bool:
        """Check if a plugin is registered."""
        return name in self._plugins

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

    def enable_all(self) -> int:
        """Enable all registered plugins.

        Returns:
            Number of plugins enabled.
        """
        count = 0
        for name in self._enabled:
            if not self._enabled[name]:
                self._enabled[name] = True
                count += 1
        return count

    def disable_all(self) -> int:
        """Disable all registered plugins.

        Returns:
            Number of plugins disabled.
        """
        count = 0
        for name in self._enabled:
            if self._enabled[name]:
                self._enabled[name] = False
                count += 1
        return count

    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugin names.

        Returns:
            List of enabled plugin names.
        """
        return [name for name, enabled in self._enabled.items() if enabled]

    def get_disabled_plugins(self) -> List[str]:
        """Get list of disabled plugin names.

        Returns:
            List of disabled plugin names.
        """
        return [name for name, enabled in self._enabled.items() if not enabled]

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
        """Run all enabled plugins on entries.

        Args:
            entries: List of log entries to process.

        Returns:
            Processed list of log entries.
        """
        if not entries:
            return []
        result = entries
        for name, plugin in self._plugins.items():
            if self._enabled.get(name, False):
                try:
                    result = plugin.process(result)
                except Exception:
                    continue
        return result

    def process_with_plugin(self, name: str, entries: List[LogEntry]) -> List[LogEntry]:
        """Run a specific plugin on entries.

        Args:
            name: Plugin name to run.
            entries: List of log entries to process.

        Returns:
            Processed list of log entries, or original if plugin not found.
        """
        if not entries:
            return []
        plugin = self._plugins.get(name)
        if not plugin or not self._enabled.get(name, False):
            return entries
        try:
            return plugin.process(entries)
        except Exception:
            return entries

    def is_enabled(self, name: str) -> bool:
        """Check if a plugin is enabled.

        Args:
            name: Plugin name.

        Returns:
            True if plugin exists and is enabled.
        """
        return self._enabled.get(name, False)

    def get_plugin_version(self, name: str) -> Optional[str]:
        """Get version of a specific plugin.

        Args:
            name: Plugin name.

        Returns:
            Version string if found, None otherwise.
        """
        plugin = self._plugins.get(name)
        return plugin.version if plugin else None

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

    def get_plugin_names(self) -> List[str]:
        """Get list of all registered plugin names.

        Returns:
            List of plugin names.
        """
        return list(self._plugins.keys())

    def has_plugin(self, name: str) -> bool:
        """Check if a plugin is registered.

        Args:
            name: Plugin name to check.

        Returns:
            True if plugin exists.
        """
        return name in self._plugins

    def has_plugins(self) -> bool:
        """Check if any plugins are registered.

        Returns:
            True if plugins exist.
        """
        return len(self._plugins) > 0

    def has_enabled_plugins(self) -> bool:
        """Check if any plugins are enabled.

        Returns:
            True if enabled plugins exist.
        """
        return any(self._enabled.values())

    def get_enabled_count(self) -> int:
        """Get number of enabled plugins.

        Returns:
            Count of enabled plugins.
        """
        return sum(1 for v in self._enabled.values() if v)

    def get_disabled_count(self) -> int:
        """Get number of disabled plugins.

        Returns:
            Count of disabled plugins.
        """
        return sum(1 for v in self._enabled.values() if not v)

    def get_plugins_dict(self) -> List[Dict[str, Any]]:
        """Get all plugins as dictionaries.

        Returns:
            List of plugin dictionaries.
        """
        return [
            {
                "name": name,
                "version": plugin.version,
                "enabled": self._enabled.get(name, False),
            }
            for name, plugin in self._plugins.items()
        ]

    def get_enabled_plugins_dict(self) -> List[Dict[str, Any]]:
        """Get enabled plugins as dictionaries.

        Returns:
            List of enabled plugin dictionaries.
        """
        return [
            {
                "name": name,
                "version": plugin.version,
            }
            for name, plugin in self._plugins.items()
            if self._enabled.get(name, False)
        ]

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get plugin manager statistics as dictionary.

        Returns:
            Dictionary with plugin stats.
        """
        return {
            "total": len(self._plugins),
            "enabled": self.get_enabled_count(),
            "disabled": self.get_disabled_count(),
        }

    def get_enabled_rate(self) -> float:
        """Get enabled plugin rate as percentage.

        Returns:
            Enabled rate percentage.
        """
        if not self._plugins:
            return 0.0
        return round(self.get_enabled_count() / len(self._plugins) * 100, 2)

    def get_disabled_rate(self) -> float:
        """Get disabled plugin rate as percentage.

        Returns:
            Disabled rate percentage.
        """
        if not self._plugins:
            return 0.0
        return round(self.get_disabled_count() / len(self._plugins) * 100, 2)

    def get_enabled_rate_formatted(self) -> str:
        """Get formatted enabled rate string.

        Returns:
            Formatted enabled rate string.
        """
        return f"{self.get_enabled_rate():.1f}%"

    def get_plugin_versions(self) -> Dict[str, str]:
        """Get plugin versions as dictionary.

        Returns:
            Dictionary mapping plugin names to versions.
        """
        return {name: plugin.version for name, plugin in self._plugins.items()}

    def has_disabled_plugins(self) -> bool:
        """Check if any plugins are disabled.

        Returns:
            True if disabled plugins exist.
        """
        return self.get_disabled_count() > 0

    def get_disabled_rate_formatted(self) -> str:
        """Get formatted disabled rate string.

        Returns:
            Formatted disabled rate string.
        """
        return f"{self.get_disabled_rate():.1f}%"

    def get_total_count_formatted(self) -> str:
        """Get formatted total count string.

        Returns:
            Formatted total count string.
        """
        return f"{len(self._plugins)} plugins"

    def get_enabled_count_formatted(self) -> str:
        """Get formatted enabled count string.

        Returns:
            Formatted enabled count string.
        """
        return f"{self.get_enabled_count()} enabled"

    def get_disabled_count_formatted(self) -> str:
        """Get formatted disabled count string.

        Returns:
            Formatted disabled count string.
        """
        return f"{self.get_disabled_count()} disabled"

    def get_plugin_versions_formatted(self) -> str:
        """Get formatted plugin versions string.

        Returns:
            Formatted plugin versions string.
        """
        versions = self.get_plugin_versions()
        if not versions:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in versions.items())

    def get_plugin_names_formatted(self) -> str:
        """Get formatted plugin names string.

        Returns:
            Formatted plugin names string.
        """
        names = self.get_plugin_names()
        if not names:
            return "none"
        return ", ".join(names)

    def get_enabled_rate_formatted(self) -> str:
        """Get formatted enabled rate string.

        Returns:
            Formatted enabled rate string.
        """
        return f"{self.get_enabled_rate():.1f}%"

    def get_stats_formatted(self) -> str:
        """Get formatted stats string.

        Returns:
            Formatted stats string.
        """
        return f"Total: {len(self._plugins)}, Enabled: {self.get_enabled_count()}, Disabled: {self.get_disabled_count()}"

    def get_enabled_plugins_formatted(self) -> str:
        """Get formatted enabled plugins string.

        Returns:
            Formatted enabled plugins string.
        """
        names = [name for name, enabled in self._enabled.items() if enabled]
        if not names:
            return "none"
        return ", ".join(names)

    def get_disabled_plugins_formatted(self) -> str:
        """Get formatted disabled plugins string.

        Returns:
            Formatted disabled plugins string.
        """
        names = [name for name, enabled in self._enabled.items() if not enabled]
        if not names:
            return "none"
        return ", ".join(names)

    def get_plugin_versions_formatted(self) -> str:
        """Get formatted plugin versions string.

        Returns:
            Formatted plugin versions string.
        """
        versions = self.get_plugin_versions()
        if not versions:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in versions.items())

    def get_enabled_rate_percent(self) -> float:
        """Get enabled rate as percentage.

        Returns:
            Enabled rate percentage.
        """
        if not self._plugins:
            return 0.0
        return round(self.get_enabled_count() / len(self._plugins) * 100, 2)

    def get_disabled_rate_percent(self) -> float:
        """Get disabled rate as percentage.

        Returns:
            Disabled rate percentage.
        """
        if not self._plugins:
            return 0.0
        return round(self.get_disabled_count() / len(self._plugins) * 100, 2)

    def get_disabled_rate_formatted(self) -> str:
        """Get formatted disabled rate string.

        Returns:
            Formatted disabled rate string.
        """
        return f"{self.get_disabled_rate_percent():.1f}%"

    def get_total_count_formatted(self) -> str:
        """Get formatted total count string.

        Returns:
            Formatted total count string.
        """
        return f"{len(self._plugins)} plugins"

    def get_enabled_count_formatted(self) -> str:
        """Get formatted enabled count string.

        Returns:
            Formatted enabled count string.
        """
        return f"{self.get_enabled_count()} enabled"

    def get_disabled_count_formatted(self) -> str:
        """Get formatted disabled count string.

        Returns:
            Formatted disabled count string.
        """
        return f"{self.get_disabled_count()} disabled"

    def get_plugin_names_list(self) -> List[str]:
        """Get plugin names as list.

        Returns:
            List of plugin names.
        """
        return self.get_plugin_names()

    def get_enabled_plugins_list(self) -> List[str]:
        """Get enabled plugins as list.

        Returns:
            List of enabled plugin names.
        """
        return [name for name, enabled in self._enabled.items() if enabled]

    def get_disabled_plugins_list(self) -> List[str]:
        """Get disabled plugins as list.

        Returns:
            List of disabled plugin names.
        """
        return [name for name, enabled in self._enabled.items() if not enabled]

    def get_summary_string(self) -> str:
        """Get summary string.

        Returns:
            Summary string.
        """
        return self.get_stats_formatted()

    def get_plugin_diversity(self) -> float:
        """Get plugin diversity (unique versions / total plugins).

        Returns:
            Plugin diversity percentage.
        """
        if not self._plugins:
            return 0.0
        versions = set(plugin.version for plugin in self._plugins.values())
        return round(len(versions) / len(self._plugins) * 100, 2)

    def get_plugin_diversity_formatted(self) -> str:
        """Get formatted plugin diversity string.

        Returns:
            Formatted plugin diversity string.
        """
        return f"{self.get_plugin_diversity():.1f}%"

    def get_enabled_to_disabled_ratio(self) -> float:
        """Get enabled to disabled ratio.

        Returns:
            Enabled to disabled ratio.
        """
        disabled = self.get_disabled_count()
        if disabled == 0:
            return float('inf') if self.get_enabled_count() > 0 else 0.0
        return round(self.get_enabled_count() / disabled, 2)

    def get_enabled_to_disabled_ratio_formatted(self) -> str:
        """Get formatted enabled to disabled ratio string.

        Returns:
            Formatted enabled to disabled ratio string.
        """
        ratio = self.get_enabled_to_disabled_ratio()
        if ratio == float('inf'):
            return "inf"
        return f"{ratio:.2f}"

    def get_plugin_health(self) -> float:
        """Get plugin health (enabled rate).

        Returns:
            Plugin health percentage.
        """
        return self.get_enabled_rate_percent()

    def get_plugin_health_formatted(self) -> str:
        """Get formatted plugin health string.

        Returns:
            Formatted plugin health string.
        """
        return f"{self.get_plugin_health():.1f}%"

    def get_total_count_formatted(self) -> str:
        """Get formatted total count string.

        Returns:
            Formatted total count string.
        """
        return f"{len(self._plugins)} plugins"

    def get_enabled_count_formatted(self) -> str:
        """Get formatted enabled count string.

        Returns:
            Formatted enabled count string.
        """
        return f"{self.get_enabled_count()} enabled"

    def get_disabled_count_formatted(self) -> str:
        """Get formatted disabled count string.

        Returns:
            Formatted disabled count string.
        """
        return f"{self.get_disabled_count()} disabled"

    def get_enabled_rate_formatted(self) -> str:
        """Get formatted enabled rate string.

        Returns:
            Formatted enabled rate string.
        """
        return f"{self.get_enabled_rate_percent():.1f}%"

    def get_disabled_rate_formatted(self) -> str:
        """Get formatted disabled rate string.

        Returns:
            Formatted disabled rate string.
        """
        return f"{self.get_disabled_rate_percent():.1f}%"
