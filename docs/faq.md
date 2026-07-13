# FAQ

## Where do I start?

Start with [quickstart.md](quickstart.md) for a short end-to-end walkthrough.

## How do I use the web dashboard?

See [dashboard.md](dashboard.md) and the root [README](../README.md).

## How do I handle large log files?

Use the `LogStream` class for memory-efficient processing of large files. It reads line by line instead of loading the entire file into memory. See [streaming.md](modules/streaming.md) for details.

## How do I filter logs by multiple criteria?

Chain filter methods together:

```python
from src.filter import LogFilter
from src.models import LogLevel

filtered = (LogFilter(entries)
    .by_level(LogLevel.ERROR)
    .by_keyword("timeout")
    .by_source("database")
    .apply())
```

See [filter.md](modules/filter.md) for all available filters.

## How do I export results to different formats?

Use `LogExporter` to export to JSON, CSV, or text:

```python
from src.exporter import LogExporter

exporter = LogExporter()
exporter.to_json(entries, "output.json")
exporter.to_csv(entries, "output.csv")
exporter.to_text(entries, "output.txt")
```

See [exporter.md](modules/exporter.md) for details.

## How do I remove duplicate log entries?

Use `LogDeduplicator` to detect and remove duplicates:

```python
from src.dedup import LogDeduplicator

dedup = LogDeduplicator()
unique, counts = dedup.deduplicate(entries)
```

See [dedup.md](modules/dedup.md) for details.

## How do I set up alerts?

Use `AlertManager` to configure thresholds:

```python
from src.alerts import AlertManager, AlertSeverity

manager = AlertManager()
manager.set_threshold("error_rate", 5.0, AlertSeverity.HIGH)
```

See [alerts.md](modules/alerts.md) for the full alert system.

## How do I add custom log patterns?

Add patterns to `config/patterns.yaml` or use a custom regex:

```python
from src.parser import LogParser

parser = LogParser(custom_pattern=r"(?P<timestamp>\d{4}-\d{2}-\d{2}).*\[(?P<level>\w+)\] (?P<message>.*)")
```

See [parser.md](modules/parser.md) for pattern details.

## How do I use the caching system?

Use `LRUCache` for general caching or the `@cached` decorator:

```python
from src.cache import LRUCache, cached

cache = LRUCache(max_size=1000, ttl=300)
cache.put("key", "value")

@cached(ttl=600)
def my_function(arg):
    return expensive_computation(arg)
```

See [cache.md](modules/cache.md) for details.
