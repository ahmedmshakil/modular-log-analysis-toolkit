# Python API Guide

Complete guide to using the Modular Log Analysis Toolkit Python API.

## Table of Contents

- [Getting Started](#getting-started)
- [Core Workflow](#core-workflow)
- [Parsing Logs](#parsing-logs)
- [Filtering](#filtering)
- [Aggregation](#aggregation)
- [Search](#search)
- [Export](#export)
- [Deduplication](#deduplication)
- [Streaming](#streaming)
- [Alerts](#alerts)
- [Webhooks](#webhooks)
- [Tags](#tags)
- [Plugins](#plugins)
- [Retention](#retention)
- [Geolocation](#geolocation)
- [Authentication](#authentication)
- [Caching](#caching)

## Getting Started

### Import Statement

```python
from src.parser import LogParser
from src.reader import read_log_lines, read_compressed_log
from src.filter import LogFilter
from src.aggregator import LogAggregator
from src.exporter import LogExporter
from src.models import LogEntry, LogLevel, AnalysisResult
from src.search import LogSearchIndex
from src.dedup import LogDeduplicator
from src.streaming import LogStream
from src.alerts import AlertManager, AlertSeverity, Alert
from src.webhooks import WebhookSender, WebhookRouter
from src.tags import TagManager, TagRule
from src.plugins import LogPlugin, PluginManager
from src.retention import RetentionPolicy, RetentionManager
from src.geolocation import GeoLookup, GeoLocation
from src.auth import AuthManager, User
from src.cache import LRUCache, QueryCache, cached
```

## Core Workflow

The typical workflow involves:

1. **Parse** - Read and parse log files
2. **Filter** - Apply filters to narrow down entries
3. **Analyze** - Generate statistics and insights
4. **Export** - Save results to files

```python
from src.parser import LogParser
from src.reader import read_log_lines
from src.filter import LogFilter
from src.aggregator import LogAggregator
from src.exporter import LogExporter
from src.models import LogLevel

# Step 1: Parse
parser = LogParser(pattern_name="standard")
lines = list(read_log_lines("app.log"))
entries = parser.parse_lines(lines)

# Step 2: Filter
log_filter = LogFilter(entries)
errors = log_filter.by_level(LogLevel.ERROR, LogLevel.CRITICAL).apply()

# Step 3: Analyze
aggregator = LogAggregator(entries)
summary = aggregator.summary()
error_rate = aggregator.error_rate()

# Step 4: Export
exporter = LogExporter()
exporter.to_json(errors, "errors.json")
```

## Parsing Logs

### Basic Parsing

```python
from src.parser import LogParser

# Use built-in pattern
parser = LogParser(pattern_name="standard")
entry = parser.parse_line("2024-01-15 10:30:45 [ERROR] Connection timeout")

if entry:
    print(f"Level: {entry.level}")
    print(f"Message: {entry.message}")
    print(f"Timestamp: {entry.timestamp}")
```

### Parse Multiple Lines

```python
from src.parser import LogParser
from src.reader import read_log_lines

parser = LogParser(pattern_name="standard")
lines = list(read_log_lines("app.log"))
entries = parser.parse_lines(lines)

print(f"Parsed {len(entries)} entries")
```

### Custom Patterns

```python
import re
from src.parser import LogParser

# Define custom pattern with named groups
custom_pattern = r"(?P<timestamp>\d{4}-\d{2}-\d{2}) (?P<level>\w+): (?P<message>.*)"
parser = LogParser(custom_pattern=custom_pattern)

entry = parser.parse_line("2024-01-15 ERROR: Database connection failed")
```

### Available Patterns

```python
from src.parser import PATTERNS

print(list(PATTERNS.keys()))
# ['syslog', 'apache', 'json_log', 'standard']
```

### Reading Files

```python
from src.reader import read_log_lines, read_compressed_log

# Read regular file
lines = list(read_log_lines("app.log"))

# Read compressed file
lines = list(read_compressed_log("app.log.gz"))

# With encoding
lines = list(read_log_lines("app.log", encoding="utf-8"))
```

## Filtering

### Basic Filtering

```python
from src.filter import LogFilter
from src.models import LogLevel

log_filter = LogFilter(entries)

# Filter by level
errors = log_filter.by_level(LogLevel.ERROR).apply()

# Multiple levels
errors_and_warnings = log_filter.by_level(
    LogLevel.ERROR,
    LogLevel.CRITICAL,
    LogLevel.WARN
).apply()
```

### Chaining Filters

```python
from datetime import datetime

filtered = (LogFilter(entries)
    .by_level(LogLevel.ERROR)
    .by_keyword("timeout")
    .by_source("database")
    .by_time_range(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 12, 31)
    )
    .apply())
```

### Regex Filtering

```python
# Filter by regex pattern
filtered = (LogFilter(entries)
    .by_regex(r"timeout.*\d+s")
    .apply())
```

### Filter Methods

| Method | Description |
|--------|-------------|
| `by_level(*levels)` | Filter by log level |
| `by_time_range(start, end)` | Filter by time range |
| `by_source(source)` | Filter by source |
| `by_keyword(keyword, case_sensitive=False)` | Filter by keyword |
| `by_regex(pattern)` | Filter by regex pattern |
| `clear_filters()` | Remove all filters |
| `apply()` | Apply filters and return results |
| `count_by_level()` | Count entries by level |
| `merge(other)` | Merge with another filter |

### Filter Properties

```python
log_filter = LogFilter(entries)

# Check if empty
if log_filter.is_empty:
    print("No entries to filter")

# Get entry count
print(f"Total entries: {log_filter.entry_count}")

# Get length
print(f"Length: {len(log_filter)}")
```

## Aggregation

### Basic Aggregation

```python
from src.aggregator import LogAggregator

aggregator = LogAggregator(entries)

# Get summary
summary = aggregator.summary()
print(f"Total entries: {summary.total_entries}")
print(f"Level counts: {summary.level_counts}")
print(f"Top errors: {summary.top_errors}")
print(f"Time range: {summary.time_range}")
```

### Error Rate

```python
error_rate = aggregator.error_rate()
print(f"Error rate: {error_rate:.2f}%")
```

### Time Window Analysis

```python
# Group by 60-minute windows
windows = aggregator.by_time_window(window_minutes=60)

for time_window, window_entries in windows.items():
    window_agg = LogAggregator(window_entries)
    print(f"{time_window}: {len(window_entries)} entries, "
          f"error rate: {window_agg.error_rate():.2f}%")
```

### Top Sources

```python
top_sources = aggregator.top_sources(limit=10)
for source, count in top_sources:
    print(f"{source}: {count} entries")
```

### Busiest Hours

```python
busiest = aggregator.busiest_hours(limit=5)
for hour, count in busiest:
    print(f"Hour {hour}: {count} entries")
```

### Count Entries

```python
# Total count
total = aggregator.count_entries()

# Count by level
error_count = aggregator.count_entries(LogLevel.ERROR)
info_count = aggregator.count_entries(LogLevel.INFO)
```

## Search

### Create Search Index

```python
from src.search import LogSearchIndex

index = LogSearchIndex()
index.add_batch(entries)
```

### Full-text Search

```python
# Search for terms
results = index.search("database timeout")
print(f"Found {len(results)} matching entries")

# With limit
results = index.search("error", limit=50)
```

### Field-specific Search

```python
# Search by level
errors = index.search_field("level", "ERROR")

# Search by source
db_entries = index.search_field("source", "database")
```

### Regex Search

```python
# Regex pattern search
results = index.search_regex(r"timeout.*\d+s")

# Case-sensitive search
results = index.search_regex(r"Timeout", case_sensitive=True)

# With limit
results = index.search_regex(r"error.*\d+", limit=100)
```

### Suggestions

```python
# Get word suggestions
suggestions = index.suggest("conn", limit=5)
print(suggestions)  # ['connection', 'connect', 'connector', ...]
```

### Count Results

```python
# Count without retrieving
count = index.search_count("database")
print(f"Found {count} matching entries")
```

### Index Statistics

```python
stats = index.stats
print(f"Indexed entries: {stats['entries']}")
print(f"Unique words: {stats['unique_words']}")
print(f"Total word occurrences: {stats['total_word_occurrences']}")
```

## Export

### Export to JSON

```python
from src.exporter import LogExporter

exporter = LogExporter()

# Basic export
exporter.to_json(entries, "output.json")

# With options
exporter.to_json(entries, "output.json", indent=4, encoding="utf-8")
```

### Export to CSV

```python
exporter.to_csv(entries, "output.csv")

# With encoding
exporter.to_csv(entries, "output.csv", encoding="utf-8-sig")
```

### Export to Text

```python
exporter.to_text(entries, "output.txt")
```

### Export Analysis Result

```python
summary = aggregator.summary()
exporter.result_to_json(summary, "analysis.json")
```

### Export All Formats

```python
# Export to all formats at once
paths = exporter.export_all(entries, "output_dir", prefix="logs")
print(paths)
# {'json': 'output_dir/logs.json', 'csv': 'output_dir/logs.csv', 'text': 'output_dir/logs.txt'}
```

## Deduplication

### Basic Deduplication

```python
from src.dedup import LogDeduplicator

deduplicator = LogDeduplicator()
unique_entries, counts = deduplicator.deduplicate(entries)

print(f"Original: {len(entries)}")
print(f"Unique: {len(unique_entries)}")
```

### Ignore Timestamps

```python
# Ignore timestamps (default)
deduplicator = LogDeduplicator(ignore_timestamp=True)

# Include timestamps
deduplicator = LogDeduplicator(ignore_timestamp=False)
```

### Get Summary

```python
summary = deduplicator.get_summary()
print(f"Total processed: {summary['total_processed']}")
print(f"Unique entries: {summary['unique_entries']}")
print(f"Duplicates found: {summary['duplicates_found']}")
print(f"Dedup rate: {summary['dedup_rate']}%")
```

### Duplicate Details

```python
duplicates = deduplicator.get_duplicate_summary()
for hash_val, count in duplicates:
    print(f"Hash {hash_val}: {count} occurrences")
```

## Streaming

### Basic Streaming

```python
from src.streaming import LogStream

stream = LogStream("large_file.log")

# Process entries one by one
def process_entry(entry):
    if entry.is_error:
        print(f"Error: {entry.message}")

stream.stream(process_entry)
```

### Batch Streaming

```python
def process_batch(batch):
    print(f"Processing {len(batch)} entries")

stream.stream_batch(process_batch, batch_size=1000)
```

### Filtered Streaming

```python
# Stream with level filter
stream.stream_filtered(
    process_entry,
    level_filter=["ERROR", "CRITICAL"]
)
```

### Control Streaming

```bash
stream.pause()    # Pause streaming
stream.resume()   # Resume streaming
stream.stop()     # Stop streaming
```

### Statistics

```python
stats = stream.stats
print(f"Processed: {stats['processed']}")
print(f"Errors: {stats['errors']}")
print(f"Paused: {stats['paused']}")
print(f"Stopped: {stats['stopped']}")

stream.reset_stats()  # Reset statistics
```

## Alerts

### Setup Alert Manager

```python
from src.alerts import AlertManager, AlertSeverity

manager = AlertManager()
```

### Set Thresholds

```python
manager.set_threshold("error_rate", 5.0, AlertSeverity.HIGH)
manager.set_threshold("response_time", 1000, AlertSeverity.MEDIUM)
manager.set_threshold("disk_usage", 90.0, AlertSeverity.CRITICAL)
```

### Register Callbacks

```python
def on_alert(alert):
    print(f"ALERT: {alert}")
    print(f"Severity: {alert.severity}")
    print(f"Message: {alert.message}")

manager.register_callback(on_alert)
```

### Check Metrics

```python
# Check if metric exceeds threshold
alert = manager.check("error_rate", 7.5)
if alert:
    print(f"Alert triggered: {alert}")
```

### Manage Alerts

```python
# Get active alerts
active_alerts = manager.get_active_alerts()

# Acknowledge alert
manager.acknowledge(0)

# Get alert count
count = manager.alert_count

# Clear all alerts
manager.clear_alerts()

# Export alerts
manager.export_alerts("alerts.json")
```

## Webhooks

### Single Webhook

```python
from src.webhooks import WebhookSender

sender = WebhookSender("https://hooks.slack.com/xxx")

# Send alert
sender.send_alert(entry)

# Send summary
sender.send_summary(level_counts, error_rate)

# Get statistics
stats = sender.stats
print(f"Sent: {stats['sent']}, Errors: {stats['errors']}")
```

### Multiple Webhooks

```python
from src.webhooks import WebhookRouter

router = WebhookRouter()

# Add endpoints
router.add_endpoint("slack", "https://hooks.slack.com/xxx")
router.add_endpoint("discord", "https://discord.com/api/webhooks/xxx")

# Send to all
results = router.send_to_all(entry)

# Send to specific
router.send_to("slack", entry)

# List endpoints
endpoints = router.list_endpoints()

# Get endpoint count
count = router.endpoint_count
```

## Tags

### Setup Tag Manager

```python
from src.tags import TagManager, TagRule

manager = TagManager()
```

### Add Rules

```python
rule = TagRule(
    name="database_errors",
    tag="database",
    conditions={"message": "database", "level": "ERROR"},
    color="#ff0000",
    priority=10
)
manager.add_rule(rule)
```

### Apply Rules

```python
tagged_entries = manager.apply_rules(entries)
```

### Manual Tags

```python
# Add tag
manager.add_manual_tag(42, "investigate")

# Get tags
tags = manager.get_tags(42)

# Remove tag
manager.remove_manual_tag(42, "investigate")

# Get all tags
all_tags = manager.get_all_tags()
```

### Check Rules

```python
# Check if rule exists
if manager.has_rule("database_errors"):
    print("Rule exists")
```

### Export/Import Rules

```python
# Export
manager.export_rules("rules.json")

# Import
manager.import_rules("rules.json")
```

## Plugins

### Create Plugin

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
        # Custom processing
        return entries

    def on_startup(self):
        print("Plugin started")

    def on_shutdown(self):
        print("Plugin stopped")
```

### Manage Plugins

```python
from src.plugins import PluginManager

manager = PluginManager()

# Register plugin
manager.register(MyPlugin())

# List plugins
plugins = manager.list_plugins()

# Get plugin names
names = manager.get_plugin_names()

# Enable/disable
manager.enable("my_plugin")
manager.disable("my_plugin")

# Process entries
processed = manager.process_all(entries)

# Load from directory
manager.load_from_directory("./plugins")
```

## Retention

### Define Policy

```python
from src.retention import RetentionPolicy, RetentionManager

policy = RetentionPolicy(
    name="standard",
    max_age_days=30,
    compress_after_days=7,
    delete_after_days=90,
    max_size_mb=100,
    patterns=["*.log", "*.log.*"]
)
```

### Manage Retention

```python
manager = RetentionManager("/var/log/myapp")
manager.add_policy(policy)

# Scan files
files = manager.scan_files()

# Enforce (dry run)
actions = manager.enforce(dry_run=True)

# Enforce (actual)
actions = manager.enforce(dry_run=False)

# Get action log
log = manager.get_actions_log()
```

## Geolocation

### Lookup IP

```python
from src.geolocation import GeoLookup

geo = GeoLookup(cache_size=1000)

# Single lookup
location = geo.lookup("8.8.8.8")
if location:
    print(f"{location.city}, {location.country}")

# Batch lookup
locations = geo.lookup_batch(["8.8.8.8", "1.1.1.1"])

# Extract and lookup
results = geo.enrich_entry("Connection from 8.8.8.8 failed")

# Statistics
stats = geo.stats
```

## Authentication

### Setup Auth

```python
from src.auth import AuthManager

auth = AuthManager(data_dir="./data")
```

### User Management

```python
# Create user
auth.create_user("admin", "securepass123", role="admin")

# Authenticate
token = auth.authenticate("admin", "securepass123")

# Validate session
username = auth.validate_session(token)

# Check permission
has_perm = auth.check_permission(token, "manage")

# List users
users = auth.list_users()

# Delete user
auth.delete_user("admin")
```

## Caching

### Basic Cache

```python
from src.cache import LRUCache

cache = LRUCache(max_size=1000, ttl=300)

# Put/get
cache.put("key", "value")
value = cache.get("key")

# Invalidate
cache.invalidate("key")
cache.invalidate_pattern("prefix_")

# Statistics
stats = cache.stats
print(f"Hit rate: {cache.hit_rate}%")
```

### Cache Decorator

```python
from src.cache import cached

@cached(ttl=600)
def expensive_function(arg):
    # Complex computation
    return result
```

### Query Cache

```python
from src.cache import QueryCache

query_cache = QueryCache(max_size=500)

# Store/retrieve
query_cache.store_results("query", results)
cached_results = query_cache.get_results("query")

# Popular queries
popular = query_cache.popular_queries(limit=10)
```

## See Also

- [CLI Usage](cli-usage.md) - Command-line interface
- [Module Documentation](modules/) - Detailed module docs
- [Examples](../examples/) - Code examples

## Error Handling

### Common Patterns

```python
from src.parser import LogParser
from src.reader import read_log_lines

# Handle missing files
try:
    lines = list(read_log_lines("missing.log"))
except FileNotFoundError as e:
    print(f"File not found: {e}")

# Handle parsing errors
parser = LogParser()
entry = parser.parse_line("invalid log line")
if entry is None:
    print("Failed to parse line")

# Handle invalid patterns
try:
    parser = LogParser(pattern_name="nonexistent")
except ValueError as e:
    print(f"Invalid pattern: {e}")
```

### Type Checking

```python
from src.models import LogEntry, LogLevel

# Validate entry types
if isinstance(entry, LogEntry):
    print(f"Valid entry: {entry.level.value}")

# Check log levels
if entry.level in (LogLevel.ERROR, LogLevel.CRITICAL):
    print("Error level entry")
```
