# Aggregator Module

The `aggregator` module provides statistics and aggregation capabilities for log entries.

## Table of Contents

- [Overview](#overview)
- [LogAggregator Class](#logaggregator-class)
- [Methods](#methods)
- [Usage Examples](#usage-examples)

## Overview

The aggregator module provides:

- **LogAggregator** - Main class for log analysis and statistics
- **Summary generation** - Overall statistics for log entries
- **Time analysis** - Time-window based grouping
- **Error analysis** - Error rate and top errors
- **Source analysis** - Top sources and busiest hours

## LogAggregator Class

### Constructor

```python
LogAggregator(entries: List[LogEntry])
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `List[LogEntry]` | List of log entries to analyze |

### Class Methods

#### from_entries

```python
@classmethod
from_entries(cls, *entry_lists: List[LogEntry]) -> LogAggregator
```

Create an aggregator from multiple entry lists.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `*entry_lists` | `List[LogEntry]` | Multiple lists of entries |

**Returns:** `LogAggregator` - New aggregator with merged entries

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `entries` | `List[LogEntry]` | List of entries |

### Special Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |

## Methods

### summary

```python
summary() -> AnalysisResult
```

Generate summary statistics for all entries.

**Returns:** `AnalysisResult` - Summary including:
- `total_entries` - Total number of entries
- `level_counts` - Count per log level
- `time_range` - (min_timestamp, max_timestamp)
- `top_errors` - Top 10 error messages
- `sources` - Unique sources
- `duration_seconds` - Analysis duration

**Example:**

```python
aggregator = LogAggregator(entries)
result = aggregator.summary()

print(f"Total entries: {result.total_entries}")
print(f"Level counts: {result.level_counts}")
print(f"Time range: {result.time_range}")
print(f"Top errors: {result.top_errors}")
print(f"Sources: {result.sources}")
```

### by_time_window

```python
by_time_window(window_minutes: int = 60) -> Dict[str, List[LogEntry]]
```

Group entries by time windows.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `window_minutes` | `int` | `60` | Window size in minutes |

**Returns:** `Dict[str, List[LogEntry]]` - Dictionary mapping ISO timestamp to entries

**Raises:** `ValueError` - If window_minutes < 1

**Example:**

```python
# Group by hour
windows = aggregator.by_time_window(window_minutes=60)
for time_window, entries in windows.items():
    print(f"{time_window}: {len(entries)} entries")

# Group by 15 minutes
windows = aggregator.by_time_window(window_minutes=15)

# Group by day (1440 minutes)
windows = aggregator.by_time_window(window_minutes=1440)
```

### error_rate

```python
error_rate() -> float
```

Calculate error rate as percentage.

**Returns:** `float` - Error rate (0.0 to 100.0)

**Example:**

```python
rate = aggregator.error_rate()
print(f"Error rate: {rate:.2f}%")
```

### top_sources

```python
top_sources(limit: int = 10) -> List[Tuple[str, int]]
```

Get top log sources by count.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `10` | Maximum number of sources |

**Returns:** `List[Tuple[str, int]]` - List of (source, count) tuples

**Example:**

```python
top = aggregator.top_sources(limit=5)
for source, count in top:
    print(f"{source}: {count} entries")
```

### busiest_hours

```python
busiest_hours(limit: int = 5) -> List[Tuple[int, int]]
```

Find busiest hours of the day.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `5` | Maximum number of hours |

**Returns:** `List[Tuple[int, int]]` - List of (hour, count) tuples

**Example:**

```python
busiest = aggregator.busiest_hours(limit=3)
for hour, count in busiest:
    print(f"Hour {hour}: {count} entries")
```

### count_entries

```python
count_entries(level: Optional[LogLevel] = None) -> int
```

Count entries, optionally filtered by level.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `Optional[LogLevel]` | `None` | Level to count (None for all) |

**Returns:** `int` - Number of entries

**Example:**

python
# Count all entries
total = aggregator.count_entries()

# Count by level
errors = aggregator.count_entries(LogLevel.ERROR)
infos = aggregator.count_entries(LogLevel.INFO)
```

### clear

```python
clear() -> None
```

Clear all entries from the aggregator.

**Example:**

```python
aggregator.clear()
print(aggregator.count_entries())  # 0
```

### has_entries

```python
has_entries() -> bool
```

Check if aggregator has any entries.

**Returns:** `bool` - True if entries exist

**Example:**

```python
if aggregator.has_entries():
    print("Has entries to analyze")
else:
    print("No entries")
```

## Usage Examples

### Basic Analysis

```python
from src.aggregator import LogAggregator
from src.models import LogEntry, LogLevel

# Create aggregator
aggregator = LogAggregator(entries)

# Get summary
summary = aggregator.summary()
print(f"Total entries: {summary.total_entries}")
print(f"Level counts: {summary.level_counts}")
print(f"Error rate: {aggregator.error_rate():.2f}%")
```

### Time Window Analysis

```python
# Group by hour
windows = aggregator.by_time_window(window_minutes=60)

for time_window, window_entries in sorted(windows.items()):
    window_agg = LogAggregator(window_entries)
    print(f"{time_window}:")
    print(f"  Entries: {len(window_entries)}")
    print(f"  Error rate: {window_agg.error_rate():.2f}%")
```

### Source Analysis

```python
# Get top sources
top_sources = aggregator.top_sources(limit=10)

print("Top sources:")
for source, count in top_sources:
    print(f"  {source}: {count} entries")

# Get busiest hours
busiest = aggregator.busiest_hours(limit=5)

print("Busiest hours:")
for hour, count in busiest:
    print(f"  Hour {hour}: {count} entries")
```

### Error Analysis

```python
# Count errors
error_count = aggregator.count_entries(LogLevel.ERROR)
critical_count = aggregator.count_entries(LogLevel.CRITICAL)

print(f"Errors: {error_count}")
print(f"Critical: {critical_count}")
print(f"Total issues: {error_count + critical_count}")

# Get top errors
summary = aggregator.summary()
print("Top errors:")
for error in summary.top_errors:
    print(f"  - {error}")
```

### Multiple Sources

```python
from src.aggregator import LogAggregator

# Create from multiple sources
agg = LogAggregator.from_entries(
    app_entries,
    db_entries,
    auth_entries
)

# Analyze combined
summary = agg.summary()
print(f"Combined entries: {summary.total_entries}")
print(f"All sources: {summary.sources}")
```

### Comparative Analysis

```python
# Compare different time periods
from datetime import datetime, timedelta

now = datetime.now()
last_hour = now - timedelta(hours=1)
prev_hour = last_hour - timedelta(hours=1)

# Current hour
current_agg = LogAggregator([
    e for e in entries
    if last_hour <= e.timestamp <= now
])

# Previous hour
previous_agg = LogAggregator([
    e for e in entries
    if prev_hour <= e.timestamp <= last_hour
])

# Compare
current_rate = current_agg.error_rate()
previous_rate = previous_agg.error_rate()

print(f"Current error rate: {current_rate:.2f}%")
print(f"Previous error rate: {previous_rate:.2f}%")
print(f"Change: {current_rate - previous_rate:+.2f}%")
```

### Filtering and Aggregating

```python
from src.filter import LogFilter
from src.aggregator import LogAggregator
from src.models import LogLevel

# Filter first, then aggregate
errors = LogFilter(entries).by_level(LogLevel.ERROR).apply()
error_agg = LogAggregator(errors)

print(f"Total errors: {error_agg.count_entries()}")
print(f"Error sources: {error_agg.top_sources()}")
print(f"Busiest error hours: {error_agg.busiest_hours()}")
```

### Exporting Results

```python
from src.exporter import LogExporter

# Generate summary
aggregator = LogAggregator(entries)
summary = aggregator.summary()

# Export to JSON
exporter = LogExporter()
exporter.result_to_json(summary, "analysis.json")

# Export full analysis
analysis = {
    "summary": summary.to_dict(),
    "error_rate": aggregator.error_rate(),
    "top_sources": aggregator.top_sources(),
    "busiest_hours": aggregator.busiest_hours(),
    "time_windows": {
        k: len(v)
        for k, v in aggregator.by_time_window().items()
    }
}

import json
with open("full_analysis.json", "w") as f:
    json.dump(analysis, f, indent=2, default=str)
```

## See Also

- [Models](models.md) - AnalysisResult data structure
- [Filter](filter.md) - Filter entries before aggregation
- [Exporter](exporter.md) - Export analysis results
