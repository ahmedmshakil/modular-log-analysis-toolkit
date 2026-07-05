# Models Module

The `models` module defines the core data structures used throughout the Modular Log Analysis Toolkit.

## Table of Contents

- [Overview](#overview)
- [LogLevel](#loglevel)
- [LogEntry](#logentry)
- [AnalysisResult](#analysisresult)
- [Usage Examples](#usage-examples)

## Overview

The models module provides:

- **LogLevel** - Enumeration of log severity levels
- **LogEntry** - Data class representing a single log entry
- **AnalysisResult** - Data class for aggregated analysis results

## LogLevel

An enumeration of supported log severity levels.

### Values

| Value | Description |
|-------|-------------|
| `DEBUG` | Debug messages |
| `INFO` | Informational messages |
| `WARN` | Warning messages |
| `ERROR` | Error messages |
| `CRITICAL` | Critical errors |
| `TRACE` | Trace messages |

### Usage

```python
from src.models import LogLevel

# Access values
print(LogLevel.DEBUG)        # LogLevel.DEBUG
print(LogLevel.DEBUG.value)  # "DEBUG"

# Compare levels
if LogLevel.ERROR == LogLevel.ERROR:
    print("Same level")

# Check membership
if level in (LogLevel.ERROR, LogLevel.CRITICAL):
    print("Error level")
```

## LogEntry

Represents a single parsed log entry.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `timestamp` | `datetime` | required | When the log entry occurred |
| `level` | `LogLevel` | required | Log severity level |
| `message` | `str` | required | Log message content |
| `source` | `Optional[str]` | `None` | Source of the log entry |
| `line_number` | `int` | `0` | Line number in the log file |
| `raw` | `str` | `""` | Original raw log line |
| `tags` | `Dict[str, str]` | `{}` | Custom tags |
| `metadata` | `Dict[str, Any]` | `{}` | Additional metadata |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_error` | `bool` | True if level is ERROR or CRITICAL |

### Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `__eq__(other)` | `bool` | Compare two entries |
| `__repr__()` | `str` | String representation for debugging |
| `__str__()` | `str` | Human-readable string |
| `to_dict()` | `Dict[str, Any]` | Convert to dictionary |
| `from_dict(data)` | `LogEntry` | Create from dictionary (classmethod) |

### Usage

```python
from src.models import LogEntry, LogLevel
from datetime import datetime

# Create entry
entry = LogEntry(
    timestamp=datetime.now(),
    level=LogLevel.ERROR,
    message="Database connection timeout",
    source="database",
    line_number=42,
    raw="2024-01-15 10:30:45 [ERROR] Database connection timeout",
    tags={"env": "production"},
    metadata={"retry_count": 3}
)

# Check if error
if entry.is_error:
    print("This is an error entry")

# Convert to dictionary
entry_dict = entry.to_dict()
print(entry_dict)
# {
#     'timestamp': '2024-01-15T10:30:45',
#     'level': 'ERROR',
#     'message': 'Database connection timeout',
#     'source': 'database',
#     'line_number': 42,
#     'tags': {'env': 'production'}
# }

# Create from dictionary
entry = LogEntry.from_dict({
    "timestamp": "2024-01-15T10:30:45",
    "level": "ERROR",
    "message": "Database connection timeout",
    "source": "database"
})
```

## AnalysisResult

Aggregated result from log analysis.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `total_entries` | `int` | `0` | Total number of entries |
| `level_counts` | `Dict[str, int]` | `{}` | Count per log level |
| `time_range` | `Optional[tuple]` | `None` | (min_timestamp, max_timestamp) |
| `top_errors` | `List[str]` | `[]` | Top error messages |
| `sources` | `List[str]` | `[]` | Unique sources |
| `duration_seconds` | `float` | `0.0` | Analysis duration |

### Methods

| Method | Return Type | Description |
|--------|-------------|-------------|
| `__str__()` | `str` | Human-readable string |
| `__repr__()` | `str` | String representation for debugging |
| `to_dict()` | `Dict[str, Any]` | Convert to dictionary |

### Usage

```python
from src.models import AnalysisResult

# Create result
result = AnalysisResult(
    total_entries=1000,
    level_counts={"INFO": 800, "ERROR": 150, "WARN": 50},
    time_range=(datetime(2024, 1, 1), datetime(2024, 1, 31)),
    top_errors=["Connection timeout", "Database error"],
    sources=["app", "database", "auth"],
    duration_seconds=1.5
)

# Access fields
print(f"Total entries: {result.total_entries}")
print(f"Error count: {result.level_counts.get('ERROR', 0)}")
print(f"Time range: {result.time_range}")

# Convert to dictionary
result_dict = result.to_dict()
```

## Usage Examples

### Complete Workflow

```python
from src.models import LogEntry, LogLevel, AnalysisResult
from src.parser import LogParser
from src.reader import read_log_lines
from src.aggregator import LogAggregator

# Parse log file
parser = LogParser()
lines = list(read_log_lines("app.log"))
entries = parser.parse_lines(lines)

# Analyze
aggregator = LogAggregator(entries)
result = aggregator.summary()

# Access results
print(f"Total entries: {result.total_entries}")
print(f"Level counts: {result.level_counts}")
print(f"Top errors: {result.top_errors}")
print(f"Sources: {result.sources}")
print(f"Time range: {result.time_range}")
```

### Working with LogEntry

```python
from src.models import LogEntry, LogLevel
from datetime import datetime

# Create multiple entries
entries = [
    LogEntry(
        timestamp=datetime.now(),
        level=LogLevel.INFO,
        message="Application started",
        source="app"
    ),
    LogEntry(
        timestamp=datetime.now(),
        level=LogLevel.ERROR,
        message="Database connection failed",
        source="database"
    )
]

# Filter errors
errors = [e for e in entries if e.is_error]

# Get unique sources
sources = set(e.source for e in entries if e.source)

# Convert to dictionaries
entry_dicts = [e.to_dict() for e in entries]
```

### Serialization

```python
import json
from src.models import LogEntry

# Entry to JSON
entry = LogEntry(
    timestamp=datetime.now(),
    level=LogLevel.INFO,
    message="Test message",
    source="test"
)

# Convert to dict and serialize
entry_dict = entry.to_dict()
json_str = json.dumps(entry_dict, default=str)

# Deserialize
data = json.loads(json_str)
entry = LogEntry.from_dict(data)
```

## See Also

- [Parser](parser.md) - Parse log lines into LogEntry objects
- [Aggregator](aggregator.md) - Generate AnalysisResult from entries
- [Exporter](exporter.md) - Export entries and results
