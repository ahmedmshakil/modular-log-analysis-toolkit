# Streaming Module

The `streaming` module provides memory-efficient processing for large log files.

## Table of Contents

- [Overview](#overview)
- [LogStream Class](#logstream-class)
- [Methods](#methods)
- [Usage Examples](#usage-examples)

## Overview

The streaming module provides:

- **LogStream** - Stream log entries without loading entire file into memory
- **Callback-based processing** - Process entries one at a time
- **Batch processing** - Process entries in batches
- **Filtered streaming** - Stream with filters applied
- **Control flow** - Pause, resume, and stop streaming

## LogStream Class

### Constructor

```python
LogStream(file_path: str, parser: Optional[LogParser] = None)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | required | Path to log file |
| `parser` | `Optional[LogParser]` | `None` | Custom parser (default: standard) |

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `file_path` | `Path` | Path to log file |
| `parser` | `LogParser` | Parser instance |

### Special Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |

## Methods

### stream

```python
stream(callback: Callable[[LogEntry], None], batch_size: int = 1) -> None
```

Stream entries through a callback function.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `callback` | `Callable[[LogEntry], None]` | required | Function to process each entry |
| `batch_size` | `int` | `1` | Batch size (for internal buffering) |

**Example:**

```python
stream = LogStream("large_file.log")

def process_entry(entry):
    if entry.is_error:
        print(f"Error: {entry.message}")

stream.stream(process_entry)
```

### stream_batch

```python
stream_batch(callback: Callable[[List[LogEntry]], None], batch_size: int = 100) -> None
```

Stream entries in batches.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `callback` | `Callable[[List[LogEntry]], None]` | required | Function to process batch |
| `batch_size` | `int` | `100` | Batch size |

**Raises:** `ValueError` - If batch_size < 1 or not integer

**Example:**

```python
stream = LogStream("large_file.log")

def process_batch(batch):
    print(f"Processing {len(batch)} entries")

stream.stream_batch(process_batch, batch_size=1000)
```

### stream_filtered

```python
stream_filtered(callback: Callable[[LogEntry], None], level_filter: Optional[List[str]] = None) -> None
```

Stream with filtering applied.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `callback` | `Callable[[LogEntry], None]` | required | Function to process entry |
| `level_filter` | `Optional[List[str]]]` | `None` | Level filter (e.g., ["ERROR", "CRITICAL"]) |

**Example:**

```python
stream = LogStream("large_file.log")

# Stream only errors
stream.stream_filtered(
    process_entry,
    level_filter=["ERROR", "CRITICAL"]
)
```

### pause

```python
pause() -> None
```

Pause streaming.

**Example:**

```python
stream.pause()
```

### resume

```python
resume() -> None
```

Resume streaming.

**Example:**

```python
stream.resume()
```

### stop

```python
stop() -> None
```

Stop streaming.

**Example:**

```python
stream.stop()
```

### Properties

#### stats

```python
@property
stats -> dict
```

Get streaming statistics.

**Returns:** `dict` - Statistics including:
- `processed` - Number of processed entries
- `errors` - Number of parsing errors
- `paused` - Whether stream is paused
- `stopped` - Whether stream is stopped

**Example:**

```python
stats = stream.stats
print(f"Processed: {stats['processed']}")
print(f"Errors: {stats['errors']}")
print(f"Paused: {stats['paused']}")
print(f"Stopped: {stats['stopped']}")
```

### reset_stats

```python
reset_stats() -> None
```

Reset streaming statistics.

**Example:**

```python
stream.reset_stats()
```

## Usage Examples

### Basic Streaming

```python
from src.streaming import LogStream

# Create stream
stream = LogStream("large_file.log")

# Process entries
def process_entry(entry):
    print(f"[{entry.level.value}] {entry.message}")

stream.stream(process_entry)

# Get statistics
stats = stream.stats
print(f"Processed: {stats['processed']}")
```

### Batch Processing

```python
from src.streaming import LogStream

stream = LogStream("large_file.log")

# Process in batches
def process_batch(batch):
    print(f"Processing batch of {len(batch)} entries")
    for entry in batch:
        # Process each entry
        pass

stream.stream_batch(process_batch, batch_size=1000)
```

### Filtered Streaming

```python
from src.streaming import LogStream

stream = LogStream("large_file.log")

# Stream only errors
def process_error(entry):
    print(f"Error: {entry.message}")

stream.stream_filtered(
    process_error,
    level_filter=["ERROR", "CRITICAL"]
)
```

### Control Flow

```python
import threading
from src.streaming import LogStream

stream = LogStream("large_file.log")

# Process in background
def process():
    stream.stream(process_entry)

thread = threading.Thread(target=process)
thread.start()

# Pause after some time
import time
time.sleep(5)
stream.pause()
print("Paused")

# Resume
time.sleep(2)
stream.resume()
print("Resumed")

# Stop
time.sleep(5)
stream.stop()
print("Stopped")
```

### Error Handling

```python
from src.streaming import LogStream

stream = LogStream("large_file.log")

error_count = 0
def process_entry(entry):
    global error_count
    if entry.is_error:
        error_count += 1
        print(f"Error {error_count}: {entry.message}")

stream.stream(process_entry)

stats = stream.stats
print(f"Total processed: {stats['processed']}")
print(f"Total errors: {stats['errors']}")
print(f"Application errors: {error_count}")
```

### Large File Analysis

```python
from src.streaming import LogStream
from collections import Counter

stream = LogStream("huge_file.log")

level_counts = Counter()
error_messages = []

def analyze_entry(entry):
    level_counts[entry.level.value] += 1
    if entry.is_error:
        error_messages.append(entry.message)

stream.stream(analyze_entry)

print("Level distribution:")
for level, count in level_counts.most_common():
    print(f"  {level}: {count}")

print(f"\nTop error messages:")
for msg in error_messages[:10]:
    print(f"  - {msg}")
```

### Progress Tracking

```python
from src.streaming import LogStream
import time

stream = LogStream("large_file.log")

start_time = time.time()
last_count = 0

def process_entry(entry):
    global last_count
    # Process entry
    pass

# Monitor progress in background
def monitor():
    while True:
        stats = stream.stats
        current = stats['processed']
        elapsed = time.time() - start_time
        rate = current / elapsed if elapsed > 0 else 0
        print(f"\rProcessed: {current} ({rate:.0f} entries/sec)", end="")
        if stats['stopped']:
            break
        time.sleep(1)

import threading
monitor_thread = threading.Thread(target=monitor)
monitor_thread.start()

stream.stream(process_entry)
```

## See Also

- [Models](models.md) - LogEntry structure
- [Parser](parser.md) - Parse log lines
- [Filter](filter.md) - Filter entries
