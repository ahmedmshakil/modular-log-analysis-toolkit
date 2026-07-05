# Parser Module

The `parser` module handles parsing log lines into structured LogEntry objects.

## Table of Contents

- [Overview](#overview)
- [LogParser Class](#logparser-class)
- [Built-in Patterns](#built-in-patterns)
- [Custom Patterns](#custom-patterns)
- [Usage Examples](#usage-examples)

## Overview

The parser module provides:

- **LogParser** - Main parser class for converting log lines to LogEntry objects
- **PATTERNS** - Dictionary of built-in log format patterns
- **Pattern matching** - Regex-based log parsing with named groups

## LogParser Class

### Constructor

```python
LogParser(pattern_name: str = "standard", custom_pattern: Optional[str] = None)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pattern_name` | `str` | `"standard"` | Name of built-in pattern to use |
| `custom_pattern` | `Optional[str]` | `None` | Custom regex pattern string |

**Raises:**
- `ValueError` - If pattern_name is unknown or custom_pattern is invalid regex

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `DEFAULT_TIMESTAMP_FORMATS` | `List[str]` | List of timestamp format strings to try |

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `pattern` | `Pattern` | Compiled regex pattern |
| `pattern_name` | `str` | Name of the pattern |

### Methods

#### parse_line

```python
parse_line(line: str, line_number: int = 0) -> Optional[LogEntry]
```

Parse a single log line into a LogEntry.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `line` | `str` | required | Log line to parse |
| `line_number` | `int` | `0` | Line number in the file |

**Returns:** `Optional[LogEntry]` - Parsed entry or None if parsing fails

#### parse_lines

```python
parse_lines(lines: List[str]) -> List[LogEntry]
```

Parse multiple log lines.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lines` | `List[str]` | List of log lines |

**Returns:** `List[LogEntry]` - List of successfully parsed entries

## Built-in Patterns

### Standard Pattern

Format: `YYYY-MM-DD HH:MM:SS [LEVEL] message`

```
2024-01-15 10:30:45 [ERROR] Database connection timeout
2024-01-15 10:31:00 [INFO] Application started
```

**Regex:**
```python
r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[(?P<level>\w+)\]\s+(?P<message>.*)"
```

### Syslog Pattern

Format: `MMM DD HH:MM:SS host program[pid]: message`

```
Jan 15 10:30:45 server1 sshd[1234]: Connection from 192.168.1.1
Jan 15 10:31:00 server1 nginx: GET /index.html 200
```

**Regex:**
```python
r"(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<program>\S+?)(?:\[(?P<pid>\d+)\])?:\s+(?P<message>.*)"
```

### Apache Pattern

Format: `IP - - [timestamp] "request" status size`

```
192.168.1.1 - - [15/Jan/2024:10:30:45 +0000] "GET /index.html HTTP/1.1" 200 1234
```

**Regex:**
```python
r"(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+\"(?P<request>[^"]*)\"\s+(?P<status>\d+)\s+(?P<size>\S+)"
```

### JSON Log Pattern

Format: JSON objects

```json
{"timestamp": "2024-01-15T10:30:45", "level": "ERROR", "message": "Connection timeout"}
```

**Regex:**
```python
r"^\{.*\}$"
```

## Custom Patterns

### Creating Custom Patterns

```python
import re
from src.parser import LogParser

# Define custom pattern with named groups
custom_pattern = r"(?P<timestamp>\d{4}-\d{2}-\d{2})\s+(?P<level>\w+):\s+(?P<message>.*)"

parser = LogParser(custom_pattern=custom_pattern)

# Parse line
entry = parser.parse_line("2024-01-15 ERROR: Database connection failed")
```

### Required Named Groups

Your custom pattern should include these named groups:

| Group | Required | Description |
|-------|----------|-------------|
| `timestamp` | Yes | Timestamp string |
| `level` | No | Log level (defaults to INFO) |
| `message` | Yes | Log message |
| `source` | No | Source/program name |
| `host` | No | Hostname |
| `program` | No | Program name |
| `pid` | No | Process ID |

### Example Custom Patterns

#### Python Logging Format

```python
custom_pattern = r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+-\s+(?P<program>\S+)\s+-\s+(?P<level>\w+)\s+-\s+(?P<message>.*)"
```

#### Nginx Access Log

```python
custom_pattern = r"(?P<ip>\S+)\s+-\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+\"(?P<request>[^"]*)\"\s+(?P<status>\d+)\s+(?P<size>\d+)\s+\"(?P<referrer>[^\"]*)\"\s+\"(?P<user_agent>[^\"]*)\""
```

#### Docker Log Format

```python
custom_pattern = r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)\s+(?P<stream>stdout|stderr)\s+(?P<level>\w+)\s+(?P<message>.*)"
```

## Usage Examples

### Basic Parsing

```python
from src.parser import LogParser

# Create parser
parser = LogParser(pattern_name="standard")

# Parse single line
entry = parser.parse_line("2024-01-15 10:30:45 [ERROR] Connection timeout")

if entry:
    print(f"Level: {entry.level}")
    print(f"Message: {entry.message}")
    print(f"Timestamp: {entry.timestamp}")
else:
    print("Failed to parse line")
```

### Parse File

```python
from src.parser import LogParser
from src.reader import read_log_lines

# Create parser
parser = LogParser(pattern_name="standard")

# Read and parse lines
lines = list(read_log_lines("app.log"))
entries = parser.parse_lines(lines)

print(f"Parsed {len(entries)} entries from {len(lines)} lines")
print(f"Parse rate: {len(entries)/len(lines)*100:.1f}%")
```

### Multiple Patterns

```python
from src.parser import LogParser, PATTERNS

# Use different patterns for different files
standard_parser = LogParser(pattern_name="standard")
syslog_parser = LogParser(pattern_name="syslog")
apache_parser = LogParser(pattern_name="apache")

# Parse with appropriate parser
standard_entries = standard_parser.parse_lines(standard_lines)
syslog_entries = syslog_parser.parse_lines(syslog_lines)
apache_entries = apache_parser.parse_lines(apache_lines)
```

### Custom Pattern

```python
from src.parser import LogParser

# Define custom pattern
custom_pattern = r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[(?P<level>\w+)\]\s+\[(?P<source>\w+)\]\s+(?P<message>.*)"

# Create parser
parser = LogParser(custom_pattern=custom_pattern)

# Parse line
entry = parser.parse_line("2024-01-15 10:30:45 [ERROR] [database] Connection timeout")
```

### Error Handling

```python
from src.parser import LogParser

# Invalid pattern
try:
    parser = LogParser(custom_pattern="[invalid regex")
except ValueError as e:
    print(f"Error: {e}")

# Unknown pattern name
try:
    parser = LogParser(pattern_name="unknown")
except ValueError as e:
    print(f"Error: {e}")
```

### Filtering Unparsed Lines

```python
from src.parser import LogParser
from src.reader import read_log_lines

parser = LogParser(pattern_name="standard")
lines = list(read_log_lines("app.log"))

# Parse and track failures
parsed = []
failed = []
for i, line in enumerate(lines, 1):
    entry = parser.parse_line(line, line_number=i)
    if entry:
        parsed.append(entry)
    else:
        failed.append((i, line))

print(f"Parsed: {len(parsed)}")
print(f"Failed: {len(failed)}")

# Show failed lines
for line_num, line in failed[:10]:
    print(f"Line {line_num}: {line[:100]}")
```

### Timestamp Parsing

```python
from src.parser import LogParser

parser = LogParser(pattern_name="standard")

# Try different timestamp formats
timestamps = [
    "2024-01-15 10:30:45",      # Standard
    "2024-01-15T10:30:45",      # ISO format
    "15/Jan/2024:10:30:45",     # Apache
    "Jan 15 10:30:45",          # Syslog
    "2024/01/15 10:30:45",      # Alternative
    "01/15/2024 10:30:45",      # US format
]

for ts in timestamps:
    entry = parser.parse_line(f"{ts} [INFO] Test message")
    if entry:
        print(f"{ts} -> {entry.timestamp}")
```

## See Also

- [Models](models.md) - LogEntry and LogLevel definitions
- [Reader](reader.md) - File reading utilities
- [Filter](filter.md) - Filtering parsed entries
