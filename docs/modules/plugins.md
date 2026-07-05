# Plugins Module

The `plugins` module provides an extensible architecture for custom log processors.

## Table of Contents

- [Overview](#overview)
- [LogPlugin Class](#logplugin-class)
- [PluginManager Class](#pluginmanager-class)
- [Usage Examples](#usage-examples)

## Overview

The plugins module provides:

- **LogPlugin** - Abstract base class for plugins
- **PluginManager** - Manage plugin lifecycle
- **Dynamic loading** - Load plugins from directory
- **Enable/disable** - Control plugin execution

## LogPlugin Class

Abstract base class for log analyzer plugins.

### Abstract Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Plugin name |
| `version` | `str` | Plugin version |

### Abstract Methods

#### process

```python
@abstractmethod
process(entries: List[LogEntry]) -> List[LogEntry]
```

Process log entries.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `List[LogEntry]` | Entries to process |

**Returns:** `List[LogEntry]` - Processed entries

### Optional Methods

#### on_startup

```python
on_startup() -> None
```

Called when plugin is loaded.

#### on_shutdown

```python
on_shutdown() -> None
```

Called when plugin is unloaded.

## PluginManager Class

Manage log analyzer plugins.

### Constructor

```python
PluginManager()
```

### Methods

#### register

```python
register(plugin: LogPlugin) -> None
```

Register a plugin.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `plugin` | `LogPlugin` | Plugin to register |

**Example:**

```python
manager = PluginManager()
manager.register(MyPlugin())
```

#### unregister

```python
unregister(name: str) -> None
```

Unregister a plugin.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin name |

**Example:**

```python
manager.unregister("my_plugin")
```

#### remove_batch

```python
remove_batch(names: List[str]) -> int
```

Remove multiple plugins at once.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `names` | `List[str]` | Plugin names |

**Returns:** `int` - Number of plugins removed

**Example:**

```python
removed = manager.remove_batch(["plugin1", "plugin2"])
print(f"Removed {removed} plugins")
```

#### enable

```python
enable(name: str) -> None
```

Enable a plugin.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin name |

**Example:**

```python
manager.enable("my_plugin")
```

#### disable

```python
disable(name: str) -> None
```

Disable a plugin.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin name |

**Example:**

```python
manager.disable("my_plugin")
```

#### get_plugin

```python
get_plugin(name: str) -> Optional[LogPlugin]
```

Get a plugin by name.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin name |

**Returns:** `Optional[LogPlugin]` - Plugin or None

**Example:**

```python
plugin = manager.get_plugin("my_plugin")
if plugin:
    print(f"Found: {plugin.name}")
```

#### has_plugin

```python
has_plugin(name: str) -> bool
```

Check if a plugin is registered.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin name |

**Returns:** `bool` - True if registered

**Example:**

```python
if manager.has_plugin("my_plugin"):
    print("Plugin exists")
```

#### get_version

```python
get_version(name: str) -> Optional[str]
```

Get version string for a registered plugin.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Plugin name |

**Returns:** `Optional[str]` - Version string or None

**Example:**

```python
version = manager.get_version("my_plugin")
print(f"Version: {version}")
```

#### list_plugins

```python
list_plugins() -> List[Dict[str, str]]
```

List all registered plugins.

**Returns:** `List[Dict[str, str]]` - List of plugin info

**Example:**

```python
plugins = manager.list_plugins()
for p in plugins:
    print(f"{p['name']} v{p['version']} (enabled: {p['enabled']})")
```

#### get_plugin_names

```python
get_plugin_names() -> List[str]
```

Get list of all registered plugin names.

**Returns:** `List[str]` - Plugin names

**Example:**

```python
names = manager.get_plugin_names()
print(f"Plugins: {names}")
```

#### process_all

```python
process_all(entries: List[LogEntry]) -> List[LogEntry]
```

Run all enabled plugins on entries.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `List[LogEntry]` | Entries to process |

**Returns:** `List[LogEntry]` - Processed entries

**Example:**

```python
processed = manager.process_all(entries)
```

#### Properties

##### stats

```python
@property
stats -> Dict[str, int]
```

Get plugin manager statistics.

**Returns:** `Dict[str, int]` - Statistics including:
- `total` - Total plugins
- `enabled` - Enabled plugins
- `disabled` - Disabled plugins

**Example:**

```python
stats = manager.stats
print(f"Total: {stats['total']}")
print(f"Enabled: {stats['enabled']}")
print(f"Disabled: {stats['disabled']}")
```

#### load_from_directory

```python
load_from_directory(directory: str) -> None
```

Load plugins from a directory.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `directory` | `str` | Directory path |

**Example:**

```python
manager.load_from_directory("./plugins")
```

## Usage Examples

### Create Custom Plugin

```python
from src.plugins import LogPlugin
from src.models import LogEntry
from typing import List

class ErrorCounter(LogPlugin):
    @property
    def name(self) -> str:
        return "error_counter"

    @property
    def version(self) -> str:
        return "1.0.0"

    def __init__(self):
        self.error_count = 0

    def process(self, entries: List[LogEntry]) -> List[LogEntry]:
        for entry in entries:
            if entry.is_error:
                self.error_count += 1
        return entries

    def on_startup(self):
        print(f"{self.name} started")

    def on_shutdown(self):
        print(f"{self.name} stopped, counted {self.error_count} errors")
```

### Register and Use Plugin

```python
from src.plugins import PluginManager

manager = PluginManager()

# Register plugin
counter = ErrorCounter()
manager.register(counter)

# Process entries
processed = manager.process_all(entries)

# Check stats
print(f"Error count: {counter.error_count}")
```

### Manage Plugins

```python
# List plugins
plugins = manager.list_plugins()
for p in plugins:
    print(f"{p['name']} v{p['version']} (enabled: {p['enabled']})")

# Get plugin names
names = manager.get_plugin_names()

# Check if exists
if manager.has_plugin("error_counter"):
    print("Plugin exists")

# Get version
version = manager.get_version("error_counter")

# Enable/disable
manager.disable("error_counter")
manager.enable("error_counter")

# Unregister
manager.unregister("error_counter")
```

### Load from Directory

```python
# Create plugin file: plugins/my_plugin.py
# class MyPlugin(LogPlugin):
#     ...

# Load all plugins from directory
manager.load_from_directory("./plugins")

# List loaded plugins
print(manager.list_plugins())
```

### Batch Operations

```python
# Register multiple plugins
manager.register(ErrorCounter())
manager.register(AnotherPlugin())

# Remove batch
removed = manager.remove_batch(["error_counter", "another_plugin"])
print(f"Removed {removed} plugins")
```

### Plugin Statistics

```python
stats = manager.stats
print(f"Total: {stats['total']}")
print(f"Enabled: {stats['enabled']}")
print(f"Disabled: {stats['disabled']}")
```

## See Also

- [Models](models.md) - LogEntry structure
