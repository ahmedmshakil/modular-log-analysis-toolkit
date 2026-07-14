# Plugin Development

Custom plugins implement the `LogPlugin` interface from `src.plugins`.

```python
from src.plugins import LogPlugin
```

## Basic Plugin Template

```python
from src.plugins import LogPlugin
from src.models import LogEntry
from typing import List

class MyPlugin(LogPlugin):
    @property
    def name(self) -> str:
        return "my_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def process(self, entries: List[LogEntry]) -> List[LogEntry]:
        # Custom processing logic
        return entries

    def on_startup(self):
        print(f"{self.name} started")

    def on_shutdown(self):
        print(f"{self.name} stopped")
```

## Registering Plugins

```python
from src.plugins import PluginManager

manager = PluginManager()
manager.register(MyPlugin())
```

## Loading from Directory

```python
manager.load_from_directory("./plugins")
```

Place plugin `.py` files in the directory and they will be auto-discovered.

Use the module reference in [modules/plugins.md](modules/plugins.md) for the current API surface.
