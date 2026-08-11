# Exporter Module

The `exporter` module handles exporting log entries and analysis results to various formats.

## Table of Contents

- [Overview](#overview)
- [LogExporter Class](#logexporter-class)
- [Methods](#methods)
- [Usage Examples](#usage-examples)

## Overview

The exporter module provides:

- **LogExporter** - Export entries to JSON, CSV, and text formats
- **Analysis export** - Export analysis results
- **Batch export** - Export to all formats at once
- **Encoding support** - Configurable character encoding
- **String conversion** - Convert entries to formatted strings
- **Statistics** - Entry counts and distribution analysis
- **Formatted output** - Pre-formatted strings for display

## LogExporter Class

### Constructor

```python
LogExporter()
```

### Methods

#### to_json

```python
@staticmethod
to_json(entries: List[LogEntry], output_path: str, indent: int = 2, encoding: str = "utf-8") -> str
```

Export entries to JSON format.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entries` | `List[LogEntry]` | required | Entries to export |
| `output_path` | `str` | required | Output file path |
| `indent` | `int` | `2` | JSON indentation |
| `encoding` | `str` | `"utf-8"` | File encoding |

**Returns:** `str` - Path to exported file

**Example:**

```python
from src.exporter import LogExporter

path = LogExporter.to_json(entries, "output.json")
print(f"Exported to {path}")

# With custom indentation
path = LogExporter.to_json(entries, "output.json", indent=4)
```

#### to_csv

```python
@staticmethod
to_csv(entries: List[LogEntry], output_path: str, encoding: str = "utf-8") -> str
```

Export entries to CSV format.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entries` | `List[LogEntry]` | required | Entries to export |
| `output_path` | `str` | required | Output file path |
| `encoding` | `str` | `"utf-8"` | File encoding |

**Returns:** `str` - Path to exported file

**CSV Columns:**
- `timestamp` - ISO format timestamp
- `level` - Log level
- `source` - Log source
- `message` - Log message
- `line_number` - Line number in original file

**Example:**

```python
path = LogExporter.to_csv(entries, "output.csv")
print(f"Exported to {path}")
```

#### to_text

```python
@staticmethod
to_text(entries: List[LogEntry], output_path: str, encoding: str = "utf-8") -> str
```

Export entries to plain text format.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entries` | `List[LogEntry]` | required | Entries to export |
| `output_path` | `str` | required | Output file path |
| `encoding` | `str` | `"utf-8"` | File encoding |

**Returns:** `str` - Path to exported file

**Text Format:**
```
[LEVEL] timestamp - message
```

**Example:**

```python
path = LogExporter.to_text(entries, "output.txt")
print(f"Exported to {path}")
```

#### result_to_json

```python
@staticmethod
result_to_json(result: AnalysisResult, output_path: str) -> str
```

Export analysis result to JSON.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `result` | `AnalysisResult` | Analysis result to export |
| `output_path` | `str` | Output file path |

**Returns:** `str` - Path to exported file

**Example:**

```python
from src.aggregator import LogAggregator
from src.exporter import LogExporter

aggregator = LogAggregator(entries)
summary = aggregator.summary()

path = LogExporter.result_to_json(summary, "analysis.json")
print(f"Exported to {path}")
```

#### export_all

```python
@staticmethod
export_all(entries: List[LogEntry], output_dir: str, prefix: str = "logs") -> Dict[str, str]
```

Export entries in all supported formats at once.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entries` | `List[LogEntry]` | required | Entries to export |
| `output_dir` | `str` | required | Output directory |
| `prefix` | `str` | `"logs"` | File prefix |

**Returns:** `Dict[str, str]` - Dictionary mapping format to file path

**Example:**

```python
paths = LogExporter.export_all(entries, "output", prefix="app_logs")
print(paths)
# {
#     'json': 'output/app_logs.json',
#     'csv': 'output/app_logs.csv',
#     'text': 'output/app_logs.txt'
# }
```

## Usage Examples

### Basic Export

```python
from src.exporter import LogExporter

# Export to JSON
LogExporter.to_json(entries, "logs.json")

# Export to CSV
LogExporter.to_csv(entries, "logs.csv")

# Export to text
LogExporter.to_text(entries, "logs.txt")
```

### Export Filtered Results

```python
from src.filter import LogFilter
from src.models import LogLevel
from src.exporter import LogExporter

# Filter entries
errors = LogFilter(entries).by_level(LogLevel.ERROR).apply()

# Export filtered results
LogExporter.to_json(errors, "errors.json")
LogExporter.to_csv(errors, "errors.csv")
```

### Export Analysis

```python
from src.aggregator import LogAggregator
from src.exporter import LogExporter

# Generate analysis
aggregator = LogAggregator(entries)
summary = aggregator.summary()

# Export analysis
LogExporter.result_to_json(summary, "analysis.json")
```

### Batch Export

```python
# Export to all formats
paths = LogExporter.export_all(entries, "output", prefix="logs")

# List exported files
for format_type, path in paths.items():
    print(f"{format_type}: {path}")
```

### Custom Encoding

```python
# Export with UTF-8 BOM (for Excel)
LogExporter.to_csv(entries, "output.csv", encoding="utf-8-sig")

# Export with Latin-1 encoding
LogExporter.to_text(entries, "output.txt", encoding="latin-1")
```

### Export with Custom JSON Formatting

```python
# Compact JSON
LogExporter.to_json(entries, "compact.json", indent=None)

# Pretty JSON
LogExporter.to_json(entries, "pretty.json", indent=4)
```

### Batch Export with Splits

```python
# Export in batches for large datasets
result = LogExporter.export_batch(entries, "output", prefix="logs", batch_size=1000)
print(f"Total: {result['total']}")
print(f"Batches: {result['num_batches']}")
for batch in result['files']:
    print(f"Batch {batch['batch']}: {batch['entries']} entries")
```

### Export by Level

```python
# Export entries grouped by log level
result = LogExporter.export_by_level(entries, "output", prefix="logs")
for level, path in result.items():
    print(f"{level}: {path}")
```

### Export by Source

```python
# Export entries grouped by source
result = LogExporter.export_by_source(entries, "output", prefix="logs")
for source, path in result.items():
    print(f"{source}: {path}")
```

### Export with Options

```python
# Export with custom options
options = {
    "format": "json",
    "indent": 4,
    "encoding": "utf-8",
    "filter_level": "ERROR",
    "filter_source": "database",
}
result = LogExporter.export_with_options(entries, "filtered.json", options)
print(f"Exported: {result['entries']} entries")
print(f"Filtered: {result['filtered']} entries")
```

### Export Summary

```python
# Export summary report
result = LogExporter.export_summary(entries, "summary.json")
print(f"Total: {result['summary']['total_entries']}")
print(f"Error Rate: {result['summary']['error_rate']}%")
```

### Format Detection

```python
# Detect format from file extension
info = LogExporter.detect_format("logs.json")
print(f"Format: {info['detected_format']}")
print(f"Supported: {info['is_supported']}")

# Validate export path
result = LogExporter.validate_export_path("output/logs.json")
print(f"Valid: {result['valid']}")
```

## See Also

- [Models](models.md) - LogEntry and AnalysisResult structures
- [Filter](filter.md) - Filter entries before export
- [Aggregator](aggregator.md) - Generate analysis results
