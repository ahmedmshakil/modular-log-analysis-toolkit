# Quick Start Guide

Get up and running with the Modular Log Analysis Toolkit in 5 minutes.

## Table of Contents

- [Installation](#installation)
- [Your First Analysis](#your-first-analysis)
- [Using the CLI](#using-the-cli)
- [Using Python API](#using-python-api)
- [Web Dashboard](#web-dashboard)
- [Common Tasks](#common-tasks)
- [Next Steps](#next-steps)

## Installation

```bash
# Clone the repository
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git
cd modular-log-analysis-toolkit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install the package
pip install -e .
```

## Your First Analysis

### Create a Sample Log File

Create a file named `sample.log` with the following content:

```
2024-01-15 10:30:45 [INFO] Application started successfully
2024-01-15 10:31:02 [INFO] User login: john@example.com
2024-01-15 10:31:15 [WARN] High memory usage detected: 85%
2024-01-15 10:31:30 [ERROR] Database connection timeout after 30s
2024-01-15 10:31:45 [INFO] Retrying database connection
2024-01-15 10:32:00 [INFO] Database connection restored
2024-01-15 10:32:15 [ERROR] Failed to process request: invalid input
2024-01-15 10:32:30 [CRITICAL] System out of memory
2024-01-15 10:32:45 [INFO] Emergency cleanup initiated
2024-01-15 10:33:00 [INFO] System recovered
```

### Run Your First Analysis

```bash
# Show summary statistics
python -m src.cli sample.log --summary
```

**Output:**
```
Total entries: 10
Level counts: {'INFO': 6, 'WARN': 1, 'ERROR': 2, 'CRITICAL': 1}
Error rate: 30.00%
Top sources: []
```

## Using the CLI

### Basic Commands

```bash
# Show help
python -m src.cli --help

# Show version
python -m src.cli --version

# Analyze with summary
python -m src.cli sample.log --summary

# Verbose output
python -m src.cli sample.log -v
```

### Filtering

```bash
# Filter by log level
python -m src.cli sample.log -l ERROR -l CRITICAL

# Filter by keyword
python -m src.cli sample.log -k "database"

# Filter by time range
python -m src.cli sample.log --since "2024-01-15 10:31:00" --until "2024-01-15 10:32:00"
```

### Exporting

```bash
# Export to JSON
python -m src.cli sample.log -f json -o output.json

# Export to CSV
python -m src.cli sample.log -f csv -o output.csv

# Export to text
python -m src.cli sample.log -f text -o output.txt

# Export filtered results
python -m src.cli sample.log -l ERROR -f json -o errors.json
```

## Using Python API

### Basic Analysis

```python
from src.parser import LogParser
from src.reader import read_log_lines
from src.filter import LogFilter
from src.aggregator import LogAggregator
from src.models import LogLevel

# 1. Parse the log file
parser = LogParser(pattern_name="standard")
lines = list(read_log_lines("sample.log"))
entries = parser.parse_lines(lines)

print(f"Parsed {len(entries)} log entries")

# 2. Filter entries
log_filter = LogFilter(entries)
errors = log_filter.by_level(LogLevel.ERROR, LogLevel.CRITICAL).apply()

print(f"Found {len(errors)} errors")

# 3. Generate statistics
aggregator = LogAggregator(entries)
summary = aggregator.summary()

print(f"Total entries: {summary.total_entries}")
print(f"Error rate: {aggregator.error_rate():.2f}%")
print(f"Top errors: {summary.top_errors}")
```

### Advanced Filtering

```python
from src.filter import LogFilter
from src.models import LogLevel
from datetime import datetime

# Create filter with multiple conditions
log_filter = LogFilter(entries)

# Chain filters
filtered = (log_filter
    .by_level(LogLevel.ERROR, LogLevel.CRITICAL)
    .by_time_range(
        start=datetime(2024, 1, 15, 10, 31),
        end=datetime(2024, 1, 15, 10, 33)
    )
    .by_keyword("database")
    .apply())

print(f"Filtered entries: {len(filtered)}")
```

### Exporting Results

```python
from src.exporter import LogExporter

exporter = LogExporter()

# Export to different formats
exporter.to_json(entries, "output.json")
exporter.to_csv(entries, "output.csv")
exporter.to_text(entries, "output.txt")

# Export filtered results
exporter.to_json(filtered, "errors.json")

# Export analysis result
exporter.result_to_json(summary, "analysis.json")
```

### Search

```python
from src.search import LogSearchIndex

# Create search index
index = LogSearchIndex()
index.add_batch(entries)

# Search for terms
results = index.search("database timeout")
print(f"Found {len(results)} matching entries")

# Search by field
errors = index.search_field("level", "ERROR")
print(f"Found {len(errors)} error entries")

# Regex search
pattern_results = index.search_regex(r"timeout.*\d+s")
print(f"Found {len(pattern_results)} timeout entries")
```

## Web Dashboard

### Start the Dashboard

```python
from src.web import start_dashboard
from src.parser import LogParser
from src.reader import read_log_lines

# Parse log file
parser = LogParser()
entries = parser.parse_lines(list(read_log_lines("sample.log")))

# Start dashboard
start_dashboard(host="0.0.0.0", port=8080, entries=entries)
```

### Access the Dashboard

Open your web browser and navigate to:
```
http://localhost:8080
```

The dashboard shows:
- Total log entries
- Error count and rate
- Recent log entries
- Real-time updates (every 5 seconds)

For a short reference to the dashboard entry point, see [dashboard.md](dashboard.md).

## Common Tasks

### Task 1: Find All Errors

```bash
# Using CLI
python -m src.cli app.log -l ERROR -l CRITICAL -f json -o errors.json

# Using Python
from src.filter import LogFilter
from src.models import LogLevel

errors = LogFilter(entries).by_level(LogLevel.ERROR, LogLevel.CRITICAL).apply()
```

### Task 2: Analyze Error Rate Over Time

```python
from src.aggregator import LogAggregator

aggregator = LogAggregator(entries)

# Get hourly windows
windows = aggregator.by_time_window(window_minutes=60)

for time_window, window_entries in windows.items():
    window_agg = LogAggregator(window_entries)
    error_rate = window_agg.error_rate()
    print(f"{time_window}: {error_rate:.2f}% error rate")
```

### Task 3: Search for Specific Patterns

```python
from src.search import LogSearchIndex

index = LogSearchIndex()
index.add_batch(entries)

# Search for database issues
db_issues = index.search("database")
print(f"Database issues: {len(db_issues)}")

# Search for timeout issues
timeout_issues = index.search_regex(r"timeout.*\d+s")
print(f"Timeout issues: {len(timeout_issues)}")
```

### Task 4: Remove Duplicates

```python
from src.dedup import LogDeduplicator

deduplicator = LogDeduplicator()
unique_entries, counts = deduplicator.deduplicate(entries)

summary = deduplicator.get_summary()
print(f"Total processed: {summary['total_processed']}")
print(f"Duplicates found: {summary['duplicates_found']}")
```

### Task 5: Process Large Files

```python
from src.streaming import LogStream

stream = LogStream("large_file.log")

# Process entries one by one
error_count = 0
def count_errors(entry):
    global error_count
    if entry.is_error:
        error_count += 1

stream.stream(count_errors)
print(f"Total errors: {error_count}")

# Get statistics
stats = stream.stats
print(f"Processed: {stats['processed']}")
print(f"Errors: {stats['errors']}")
```

### Task 6: Set Up Alerts

```python
from src.alerts import AlertManager, AlertSeverity

manager = AlertManager()

# Set thresholds
manager.set_threshold("error_rate", 5.0, AlertSeverity.HIGH)
manager.set_threshold("response_time", 1000, AlertSeverity.MEDIUM)

# Register callback
def on_alert(alert):
    print(f"ALERT: {alert}")

manager.register_callback(on_alert)

# Check metrics
aggregator = LogAggregator(entries)
error_rate = aggregator.error_rate()

alert = manager.check("error_rate", error_rate)
if alert:
    print(f"Alert triggered: {alert}")
```

## Next Steps

Now that you're up and running:

1. **Read the [CLI Usage Guide](cli-usage.md)** - Learn all CLI commands
2. **Explore the [Python API](python-api.md)** - Detailed API reference
3. **Set up [Web Dashboard](dashboard.md)** - Real-time monitoring
4. **Create [Custom Plugins](plugin-development.md)** - Extend functionality
5. **Configure [Alerts](modules/alerts.md)** - Set up notifications
6. **Learn about [Retention Policies](modules/retention.md)** - Manage log files

## Getting Help

- **Documentation**: Browse the [docs/](../docs/) directory
- **Issues**: Report bugs on [GitHub Issues](https://github.com/ahmedmshakil/modular-log-analysis-toolkit/issues)
- **FAQ**: Check the [FAQ](faq.md) for common questions

## Examples Repository

Find more examples in the `examples/` directory:

```bash
examples/
├── basic_analysis.py      # Basic log analysis
├── advanced_filtering.py  # Advanced filtering techniques
├── search_examples.py     # Search functionality
├── streaming_example.py   # Large file processing
├── alert_setup.py         # Alert configuration
├── plugin_example.py      # Custom plugin example
└── dashboard_example.py   # Web dashboard setup
```

## Quick Tips

### Performance Tips

- Use `LogStream` for files larger than 100MB
- Enable caching for repeated queries with `LRUCache`
- Use `add_batch` instead of individual `add` calls for search indexing
- Use `LogDeduplicator` to reduce storage for repetitive logs

### Common Pitfalls

- Always check for `None` return values from `parse_line`
- Use `encoding` parameter when reading non-UTF-8 files
- Call `reset()` on filters before reusing them
- Close web dashboard with Ctrl+C to free the port

## New Features (v1.2.0)

### CLI Enhancements

```bash
# Show entry count only
python -m src.cli app.log --count

# Remove duplicates
python -m src.cli app.log --dedup

# Disable colored output
python -m src.cli app.log --no-color
```

### New Python API Methods

```python
# Get statistics as dictionary
stats = aggregator.get_stats_dict()
summary = aggregator.get_summary_string()

# Get entries as dictionaries
entries_dict = filter.get_entries_dict()

# Get source counts
source_counts = aggregator.get_source_counts()

# Get level distribution
distribution = result.get_level_distribution()
```
