# Search Module

The `search` module provides full-text search indexing for log entries.

## Table of Contents

- [Overview](#overview)
- [LogSearchIndex Class](#logsearchindex-class)
- [Methods](#methods)
- [Usage Examples](#usage-examples)

## Overview

The search module provides:

- **LogSearchIndex** - In-memory full-text search index
- **Tokenization** - Word-based indexing with stop word removal
- **Field indexing** - Index by level and source
- **Regex search** - Pattern-based search
- **Suggestions** - Auto-complete functionality

## LogSearchIndex Class

### Constructor

```python
LogSearchIndex()
```

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `STOP_WORDS` | `Set[str]` | Common stop words to exclude from indexing |

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_index` | `Dict[str, Set[int]]` | Word to entry index mapping |
| `_entries` | `List[LogEntry]` | All indexed entries |
| `_field_index` | `Dict[str, Dict[str, Set[int]]]` | Field-specific indexes |

## Methods

### add

```python
add(entry: LogEntry) -> None
```

Add an entry to the index.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entry` | `LogEntry` | Entry to index |

**Example:**

```python
index = LogSearchIndex()
index.add(entry)
```

### add_batch

```python
add_batch(entries: List[LogEntry]) -> None
```

Add multiple entries to the index.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `List[LogEntry]` | List of entries to index |

**Example:**

```python
index.add_batch(entries)
```

### search

```python
search(query: str, limit: int = 100) -> List[LogEntry]
```

Full-text search across indexed entries.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | required | Search query |
| `limit` | `int` | `100` | Maximum results |

**Returns:** `List[LogEntry]` - Matching entries

**Example:**

```python
results = index.search("database timeout")
print(f"Found {len(results)} results")

# With limit
results = index.search("error", limit=50)
```

### search_field

```python
search_field(field: str, value: str) -> List[LogEntry]
```

Search by specific field value.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `field` | `str` | Field name ("level" or "source") |
| `value` | `str` | Field value to match |

**Returns:** `List[LogEntry]` - Matching entries

**Example:**

```python
# Search by level
errors = index.search_field("level", "ERROR")

# Search by source
db_entries = index.search_field("source", "database")
```

### search_regex

```python
search_regex(pattern: str, limit: int = 100, case_sensitive: bool = False) -> List[LogEntry]
```

Search using regex pattern.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pattern` | `str` | required | Regex pattern |
| `limit` | `int` | `100` | Maximum results |
| `case_sensitive` | `bool` | `False` | Case sensitivity |

**Returns:** `List[LogEntry]` - Matching entries

**Raises:** `ValueError` - If pattern is invalid

**Example:**

```python
# Simple pattern
results = index.search_regex(r"timeout.*\d+s")

# Case-sensitive
results = index.search_regex(r"Timeout", case_sensitive=True)

# Complex pattern
results = index.search_regex(r"error|fail|exception")
```

### suggest

```python
suggest(prefix: str, limit: int = 10) -> List[str]
```

Suggest completions for a search prefix.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix` | `str` | required | Prefix to complete |
| `limit` | `int` | `10` | Maximum suggestions |

**Returns:** `List[str]` - Suggested words

**Example:**

```python
suggestions = index.suggest("conn")
print(suggestions)  # ['connection', 'connect', 'connector', ...]
```

### search_count

```python
search_count(query: str) -> int
```

Count matching entries without returning them.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search query |

**Returns:** `int` - Number of matching entries

**Example:**

```python
count = index.search_count("database")
print(f"Found {count} matching entries")
```

### entry_exists

```python
entry_exists(entry: LogEntry) -> bool
```

Check if an entry is already indexed.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entry` | `LogEntry` | Entry to check |

**Returns:** `bool` - True if entry is indexed

**Example:**

```python
if index.entry_exists(entry):
    print("Entry already indexed")
```

### Properties

#### stats

```python
@property
stats -> Dict[str, int]
```

Get index statistics.

**Returns:** `Dict[str, int]` - Statistics including:
- `entries` - Total indexed entries
- `unique_words` - Number of unique words
- `total_word_occurrences` - Total word occurrences

**Example:**

```python
stats = index.stats
print(f"Indexed entries: {stats['entries']}")
print(f"Unique words: {stats['unique_words']}")
```

## Usage Examples

### Basic Search

```python
from src.search import LogSearchIndex

# Create index
index = LogSearchIndex()
index.add_batch(entries)

# Search
results = index.search("database timeout")
print(f"Found {len(results)} results")
```

### Field Search

```python
# Search by level
errors = index.search_field("level", "ERROR")
warnings = index.search_field("level", "WARN")

# Search by source
db_entries = index.search_field("source", "database")
api_entries = index.search_field("source", "api")
```

### Regex Search

```python
# Pattern matching
ip_entries = index.search_regex(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
duration_entries = index.search_regex(r"\d+ms|\d+s")

# Complex patterns
error_patterns = index.search_regex(r"error|fail|exception")
```

### Suggestions

```python
# Get suggestions
suggestions = index.suggest("conn")
print(f"Suggestions: {suggestions}")

# Use for auto-complete
prefix = "data"
completions = index.suggest(prefix, limit=5)
print(f"Completions for '{prefix}': {completions}")
```

### Count Results

```python
# Count without retrieving
db_count = index.search_count("database")
error_count = index.search_count("error")

print(f"Database entries: {db_count}")
print(f"Error entries: {error_count}")
```

### Index Statistics

```python
# Get statistics
stats = index.stats
print(f"Indexed entries: {stats['entries']}")
print(f"Unique words: {stats['unique_words']}")
print(f"Total occurrences: {stats['total_word_occurrences']}")
```

### Check Existence

```python
# Check if entry exists
if index.entry_exists(entry):
    print("Entry already indexed")
else:
    index.add(entry)
```

### Performance Optimization

```python
# Index once, search many times
index = LogSearchIndex()
index.add_batch(all_entries)

# Multiple searches
results1 = index.search("timeout")
results2 = index.search("database")
results3 = index.search_regex(r"error.*\d+")

# Get counts
count1 = index.search_count("timeout")
count2 = index.search_count("database")
```

## See Also

- [Models](models.md) - LogEntry structure
- [Filter](filter.md) - Alternative filtering approach
- [Aggregator](aggregator.md) - Analyze search results
