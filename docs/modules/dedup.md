# Dedup Module

The `dedup` module provides deduplication capabilities for log entries.

## Table of Contents

- [Overview](#overview)
- [LogDeduplicator Class](#logdeduplicator-class)
- [Methods](#methods)
- [Usage Examples](#usage-examples)

## Overview

The dedup module provides:

- **LogDeduplicator** - Hash-based duplicate detection
- **Content hashing** - Generate hashes based on entry content
- **Duplicate tracking** - Track and count duplicates
- **Summary statistics** - Get deduplication statistics

## LogDeduplicator Class

### Constructor

```python
LogDeduplicator(ignore_timestamp: bool = True)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ignore_timestamp` | `bool` | `True` | Whether to ignore timestamps when hashing |

### Special Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |

## Methods

### deduplicate

```python
deduplicate(entries: List[LogEntry]) -> Tuple[List[LogEntry], Dict[str, int]]
```

Remove duplicates, return unique entries and counts.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `List[LogEntry]` | Entries to deduplicate |

**Returns:** `Tuple[List[LogEntry], Dict[str, int]]` - Unique entries and hash counts

**Raises:** `TypeError` - If entries is not a list

**Example:**

```python
deduplicator = LogDeduplicator()
unique_entries, counts = deduplicator.deduplicate(entries)

print(f"Original: {len(entries)}")
print(f"Unique: {len(unique_entries)}")
```

### get_duplicate_summary

```python
get_duplicate_summary() -> List[Tuple[str, int]]
```

Get summary of duplicated entries.

**Returns:** `List[Tuple[str, int]]` - List of (hash, count) for duplicates

**Example:**

```python
duplicates = deduplicator.get_duplicate_summary()
for hash_val, count in duplicates:
    print(f"Hash {hash_val}: {count} occurrences")
```

### total_duplicates_removed

```python
total_duplicates_removed() -> int
```

Count total duplicates found.

**Returns:** `int` - Number of duplicates removed

**Example:**

```python
removed = deduplicator.total_duplicates_removed()
print(f"Removed {removed} duplicates")
```

### reset

```python
reset() -> None
```

Clear deduplication state.

**Example:**

```python
deduplicator.reset()
```

### get_summary

```python
get_summary() -> Dict[str, int]
```

Get a summary of deduplication statistics.

**Returns:** `Dict[str, int]` - Statistics including:
- `total_processed` - Total entries processed
- `unique_entries` - Number of unique entries
- `duplicates_found` - Number of duplicates
- `dedup_rate` - Deduplication rate percentage

**Example:**

```python
summary = deduplicator.get_summary()
print(f"Total processed: {summary['total_processed']}")
print(f"Unique entries: {summary['unique_entries']}")
print(f"Duplicates found: {summary['duplicates_found']}")
print(f"Dedup rate: {summary['dedup_rate']}%")
```

## Usage Examples

### Basic Deduplication

```python
from src.dedup import LogDeduplicator

# Create deduplicator
deduplicator = LogDeduplicator()

# Deduplicate entries
unique_entries, counts = deduplicator.deduplicate(entries)

print(f"Original: {len(entries)}")
print(f"Unique: {len(unique_entries)}")
print(f"Duplicates: {len(entries) - len(unique_entries)}")
```

### With Timestamps

```python
# Include timestamps in hash
deduplicator = LogDeduplicator(ignore_timestamp=False)
unique_entries, counts = deduplicator.deduplicate(entries)
```

### Get Statistics

```python
# Get summary
summary = deduplicator.get_summary()
print(f"Total processed: {summary['total_processed']}")
print(f"Unique entries: {summary['unique_entries']}")
print(f"Duplicates found: {summary['duplicates_found']}")
print(f"Dedup rate: {summary['dedup_rate']}%")
```

### Find Duplicates

```python
# Get duplicate details
duplicates = deduplicator.get_duplicate_summary()

print(f"Found {len(duplicates)} duplicate patterns:")
for hash_val, count in duplicates:
    print(f"  Hash {hash_val}: {count} occurrences")
```

### Reset State

```python
# Process first batch
deduplicator = LogDeduplicator()
unique1, _ = deduplicator.deduplicate(batch1)

# Reset for second batch
deduplicator.reset()
unique2, _ = deduplicator.deduplicate(batch2)
```

### Combined with Filtering

```python
from src.dedup import LogDeduplicator
from src.filter import LogFilter
from src.models import LogLevel

# Deduplicate first
deduplicator = LogDeduplicator()
unique_entries, _ = deduplicator.deduplicate(entries)

# Then filter
errors = LogFilter(unique_entries).by_level(LogLevel.ERROR).apply()

print(f"Unique errors: {len(errors)}")
```

### Export Duplicate Analysis

```python
import json
from src.dedup import LogDeduplicator

deduplicator = LogDeduplicator()
unique_entries, counts = deduplicator.deduplicate(entries)

# Export analysis
analysis = {
    "summary": deduplicator.get_summary(),
    "duplicates": [
        {"hash": h, "count": c}
        for h, c in deduplicator.get_duplicate_summary()
    ]
}

with open("dedup_analysis.json", "w") as f:
    json.dump(analysis, f, indent=2)
```

## See Also

- [Models](models.md) - LogEntry structure
- [Filter](filter.md) - Filter after deduplication
- [Aggregator](aggregator.md) - Analyze deduplicated entries
