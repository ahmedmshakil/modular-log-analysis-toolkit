# Filter Module

The `filter` module provides powerful filtering capabilities for log entries.

## Table of Contents

- [Overview](#overview)
- [LogFilter Class](#logfilter-class)
- [Filter Methods](#filter-methods)
- [Chaining Filters](#chaining-filters)
- [Usage Examples](#usage-examples)

## Overview

The filter module provides:

- **LogFilter** - Chainable filter engine for log entries
- **Multiple filter types** - Level, time, source, keyword, regex
- **Filter composition** - Combine multiple filters
- **Filter merging** - Merge results from different filters

## LogFilter Class

### Constructor

```python
LogFilter(entries: List[LogEntry])
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `List[LogEntry]` | List of log entries to filter |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_empty` | `bool` | True if no entries to filter |
| `entry_count` | `int` | Total number of entries |

### Special Methods

| Method | Description |
|--------|-------------|
| `__len__()` | Return number of entries |
| `__contains__(entry)` | Check if entry exists |
| `__repr__()` | String representation |

## Filter Methods

### by_level

```python
by_level(*levels: LogLevel) -> LogFilter
```

Filter entries by log level.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `*levels` | `LogLevel` | One or more log levels to include |

**Returns:** `LogFilter` - Self for chaining

**Example:**

```python
# Single level
filtered = log_filter.by_level(LogLevel.ERROR).apply()

# Multiple levels
filtered = log_filter.by_level(LogLevel.ERROR, LogLevel.CRITICAL).apply()
```

### by_time_range

```python
by_time_range(start: datetime, end: datetime) -> LogFilter
```

Filter entries by time range.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | Start of time range |
| `end` | `datetime` | End of time range |

**Returns:** `LogFilter` - Self for chaining

**Example:**

```python
from datetime import datetime

start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)

filtered = log_filter.by_time_range(start, end).apply()
```

### by_source

```python
by_source(source: str) -> LogFilter
```

Filter entries by source (case-insensitive substring match).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `source` | `str` | Source string to match |

**Returns:** `LogFilter` - Self for chaining

**Raises:** `ValueError` - If source is empty

**Example:**

```python
filtered = log_filter.by_source("database").apply()
```

### by_keyword

```python
by_keyword(keyword: str, case_sensitive: bool = False) -> LogFilter
```

Filter entries by keyword in message.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | `str` | required | Keyword to search for |
| `case_sensitive` | `bool` | `False` | Whether to match case |

**Returns:** `LogFilter` - Self for chaining

**Example:**

```python
# Case-insensitive (default)
filtered = log_filter.by_keyword("timeout").apply()

# Case-sensitive
filtered = log_filter.by_keyword("Timeout", case_sensitive=True).apply()
```

### by_regex

```python
by_regex(pattern: str) -> LogFilter
```

Filter entries by regex pattern match on message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pattern` | `str` | Regex pattern string |

**Returns:** `LogFilter` - Self for chaining

**Raises:** `ValueError` - If pattern is empty or invalid regex

**Example:**

```python
# Simple pattern
filtered = log_filter.by_regex(r"timeout.*\d+s").apply()

# Complex pattern
filtered = log_filter.by_regex(r"error|fail|exception").apply()
```

### clear_filters

```python
clear_filters() -> LogFilter
```

Remove all pending filters.

**Returns:** `LogFilter` - Self for chaining

**Example:**

```python
log_filter.clear_filters()
```

### apply

```python
apply() -> List[LogEntry]
```

Apply all filters and return matching entries.

**Returns:** `List[LogEntry]` - Filtered entries

**Example:**

```python
filtered = log_filter.apply()
print(f"Found {len(filtered)} matching entries")
```

### count_by_level

```python
count_by_level() -> dict
```

Count entries grouped by level.

**Returns:** `dict` - Dictionary of level counts

**Example:**

```python
counts = log_filter.count_by_level()
print(counts)  # {'INFO': 100, 'ERROR': 20, 'WARN': 10}
```

### merge

```python
merge(other: LogFilter) -> LogFilter
```

Merge entries from another LogFilter, removing duplicates.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `other` | `LogFilter` | Another LogFilter to merge with |

**Returns:** `LogFilter` - New LogFilter with merged entries

**Example:**

```python
filter1 = LogFilter(entries1).by_level(LogLevel.ERROR)
filter2 = LogFilter(entries2).by_level(LogLevel.CRITICAL)

merged = filter1.merge(filter2)
all_errors = merged.apply()
```

## Chaining Filters

Filters can be chained together for complex queries:

```python
from src.filter import LogFilter
from src.models import LogLevel
from datetime import datetime

# Chain multiple filters
filtered = (LogFilter(entries)
    .by_level(LogLevel.ERROR, LogLevel.CRITICAL)
    .by_time_range(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 12, 31)
    )
    .by_source("database")
    .by_keyword("timeout")
    .by_regex(r"\d+ms")
    .apply())

print(f"Found {len(filtered)} matching entries")
```

### Filter Order

Filters are applied in the order they are chained. Each filter operates on the results of the previous filter:

```python
# This is more efficient
filtered = (LogFilter(entries)
    .by_level(LogLevel.ERROR)  # First: reduce to errors only
    .by_keyword("timeout")     # Then: filter by keyword
    .apply())

# This is less efficient
filtered = (LogFilter(entries)
    .by_keyword("timeout")     # First: search all entries
    .by_level(LogLevel.ERROR)  # Then: filter by level
    .apply())
```

## Usage Examples

### Basic Filtering

```python
from src.filter import LogFilter
from src.models import LogLevel

# Create filter
log_filter = LogFilter(entries)

# Filter by level
errors = log_filter.by_level(LogLevel.ERROR).apply()
warnings = log_filter.by_level(LogLevel.WARN).apply()

# Multiple levels
critical_and_errors = log_filter.by_level(
    LogLevel.CRITICAL,
    LogLevel.ERROR
).apply()
```

### Time-based Filtering

```python
from datetime import datetime, timedelta

# Last 24 hours
now = datetime.now()
yesterday = now - timedelta(days=1)
recent = log_filter.by_time_range(yesterday, now).apply()

# Specific date
start = datetime(2024, 1, 15, 0, 0, 0)
end = datetime(2024, 1, 15, 23, 59, 59)
today = log_filter.by_time_range(start, end).apply()
```

### Source-based Filtering

```python
# Filter by source
db_entries = log_filter.by_source("database").apply()
auth_entries = log_filter.by_source("auth").apply()

# Case-insensitive
app_entries = log_filter.by_source("APP").apply()  # Matches "app", "App", etc.
```

### Keyword Filtering

```python
# Simple keyword
timeout_entries = log_filter.by_keyword("timeout").apply()

# Case-sensitive
capital_errors = log_filter.by_keyword("Error", case_sensitive=True).apply()

# Multiple keywords (chained)
db_timeouts = (log_filter
    .by_keyword("database")
    .by_keyword("timeout")
    .apply())
```

### Regex Filtering

```python
import re

# Match patterns
ip_entries = log_filter.by_regex(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}").apply()
duration_entries = log_filter.by_regex(r"\d+ms|\d+s").apply()

# Complex patterns
error_patterns = log_filter.by_regex(r"error|fail|exception|critical").apply()
```

### Combining Filters

```python
from datetime import datetime

# Complex query: Errors from database in the last hour with timeout
one_hour_ago = datetime.now() - timedelta(hours=1)
now = datetime.now()

filtered = (log_filter
    .by_level(LogLevel.ERROR, LogLevel.CRITICAL)
    .by_time_range(one_hour_ago, now)
    .by_source("database")
    .by_keyword("timeout")
    .apply())

print(f"Database timeout errors in last hour: {len(filtered)}")
```

### Merging Filters

```python
# Create separate filters
error_filter = LogFilter(entries).by_level(LogLevel.ERROR)
warn_filter = LogFilter(entries).by_level(LogLevel.WARN)

# Merge results
merged = error_filter.merge(warn_filter)
all_issues = merged.apply()

# Merge with different criteria
db_filter = LogFilter(entries).by_source("database")
api_filter = LogFilter(entries).by_source("api")

combined = db_filter.merge(api_filter)
service_entries = combined.apply()
```

### Getting Statistics

```python
# Count by level
counts = log_filter.count_by_level()
for level, count in counts.items():
    print(f"{level}: {count}")

# Check if empty
if log_filter.is_empty:
    print("No entries to filter")

# Get entry count
print(f"Total entries: {log_filter.entry_count}")
```

### Dynamic Filtering

```python
def dynamic_filter(entries, filters_config):
    """Apply filters based on configuration."""
    log_filter = LogFilter(entries)

    if "level" in filters_config:
        levels = [LogLevel[l] for l in filters_config["level"]]
        log_filter.by_level(*levels)

    if "source" in filters_config:
        log_filter.by_source(filters_config["source"])

    if "keyword" in filters_config:
        log_filter.by_keyword(filters_config["keyword"])

    if "since" in filters_config:
        start = datetime.fromisoformat(filters_config["since"])
        log_filter.by_time_range(start, datetime.now())

    return log_filter.apply()

# Usage
config = {
    "level": ["ERROR", "CRITICAL"],
    "source": "database",
    "keyword": "timeout",
    "since": "2024-01-01T00:00:00"
}

filtered = dynamic_filter(entries, config)
```

## See Also

- [Models](models.md) - LogEntry and LogLevel definitions
- [Parser](parser.md) - Parse log lines into entries
- [Aggregator](aggregator.md) - Analyze filtered entries

## New Methods (v1.2.0)

### by_multiple_keywords

```python
by_multiple_keywords(keywords: List[str], match_all: bool = False) -> LogFilter
```

Filter by multiple keywords.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keywords` | `List[str]` | required | List of keywords |
| `match_all` | `bool` | `False` | If True, all must match; if False, any matches |

### by_source_list

```python
by_source_list(sources: List[str]) -> LogFilter
```

Filter by multiple sources.

### by_min_severity

```python
by_min_severity(min_level: LogLevel) -> LogFilter
```

Filter by minimum severity level.

### first, last, sample

```python
first(n: int = 1) -> List[LogEntry]
last(n: int = 1) -> List[LogEntry]
sample(n: int = 10) -> List[LogEntry]
```

Get first N, last N, or sampled entries.

### apply_count

```python
apply_count() -> int
```

Count matching entries without building the full list.

### unique_sources

```python
@property
unique_sources() -> List[str]
```

Get unique sources from entries.
