# Retention Module

The `retention` module provides log file lifecycle management with automatic rotation and cleanup.

## Table of Contents

- [Overview](#overview)
- [RetentionPolicy Class](#retentionpolicy-class)
- [RetentionManager Class](#retentionmanager-class)
- [Usage Examples](#usage-examples)

## Overview

The retention module provides:

- **RetentionPolicy** - Define retention rules
- **RetentionManager** - Enforce policies on log files
- **Compression** - Automatic gzip compression
- **Rotation** - File rotation by size
- **Cleanup** - Delete old files

## RetentionPolicy Class

Defines a log retention policy.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Policy name |
| `max_age_days` | `int` | required | Maximum age in days |
| `compress_after_days` | `int` | `0` | Compress after N days |
| `delete_after_days` | `int` | `0` | Delete after N days |
| `max_size_mb` | `float` | `0` | Maximum file size in MB |
| `patterns` | `List[str]` | `["*.log"]` | File patterns |

### Validation

- `max_age_days` must be non-negative
- `compress_after_days` must be non-negative
- `delete_after_days` must be non-negative
- `max_size_mb` must be non-negative

### Special Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |
| `__str__()` | Human-readable string |

## RetentionManager Class

Manage log file retention and cleanup.

### Constructor

```python
RetentionManager(log_directory: str)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `log_directory` | `str` | Directory containing log files |

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `log_directory` | `Path` | Log directory path |
| `policies` | `List[RetentionPolicy]` | List of policies |

### Methods

#### add_policy

```python
add_policy(policy: RetentionPolicy) -> None
```

Add a retention policy.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `policy` | `RetentionPolicy` | Policy to add |

**Example:**

```python
manager = RetentionManager("/var/log/myapp")
policy = RetentionPolicy(name="standard", max_age_days=30)
manager.add_policy(policy)
```

#### scan_files

```python
scan_files() -> List[Dict]
```

Scan log files and their metadata.

**Returns:** `List[Dict]` - File information including:
- `path` - File path
- `size_mb` - File size in MB
- `age_days` - Age in days
- `modified` - Last modified timestamp
- `policy` - Associated policy name

**Example:**

```python
files = manager.scan_files()
for f in files:
    print(f"{f['path']}: {f['age_days']} days, {f['size_mb']:.1f} MB")
```

#### enforce

```python
enforce(dry_run: bool = False) -> List[Dict]
```

Enforce retention policies.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dry_run` | `bool` | `False` | If True, only report actions |

**Returns:** `List[Dict]` - Actions taken including:
- `action` - Action type (delete, compress, rotate)
- `file` - File path
- `reason` - Reason for action

**Example:**

```python
# Dry run
actions = manager.enforce(dry_run=True)
print(f"Would take {len(actions)} actions")

# Actually enforce
actions = manager.enforce(dry_run=False)
for action in actions:
    print(f"{action['action']}: {action['file']}")
```

#### get_actions_log

```python
get_actions_log() -> List[Dict]
```

Get history of retention actions.

**Returns:** `List[Dict]` - Action history

**Example:**

```python
log = manager.get_actions_log()
print(f"Total actions: {len(log)}")
```

#### Properties

##### stats

```python
@property
stats -> Dict[str, int]
```

Get retention manager statistics.

**Returns:** `Dict[str, int]` - Statistics including:
- `policies` - Number of policies
- `actions_taken` - Number of actions taken

**Example:**

```python
stats = manager.stats
print(f"Policies: {stats['policies']}")
print(f"Actions taken: {stats['actions_taken']}")
```

## Usage Examples

### Basic Retention

```python
from src.retention import RetentionPolicy, RetentionManager

# Create policy
policy = RetentionPolicy(
    name="standard",
    max_age_days=30,
    compress_after_days=7,
    delete_after_days=90,
    max_size_mb=100,
    patterns=["*.log", "*.log.*"]
)

# Create manager
manager = RetentionManager("/var/log/myapp")
manager.add_policy(policy)

# Scan files
files = manager.scan_files()
print(f"Found {len(files)} files")

# Enforce (dry run)
actions = manager.enforce(dry_run=True)
print(f"Would take {len(actions)} actions")

# Actually enforce
actions = manager.enforce(dry_run=False)
```

### Multiple Policies

```python
# Different policies for different log types
app_policy = RetentionPolicy(
    name="app_logs",
    max_age_days=30,
    compress_after_days=7,
    delete_after_days=90,
    patterns=["app*.log"]
)

access_policy = RetentionPolicy(
    name="access_logs",
    max_age_days=90,
    compress_after_days=30,
    delete_after_days=365,
    patterns=["access*.log"]
)

manager = RetentionManager("/var/log")
manager.add_policy(app_policy)
manager.add_policy(access_policy)
```

### Size-based Rotation

```python
policy = RetentionPolicy(
    name="size_rotation",
    max_age_days=30,
    max_size_mb=100,  # Rotate when > 100MB
    patterns=["*.log"]
)

manager = RetentionManager("/var/log/myapp")
manager.add_policy(policy)

# Enforce rotation
actions = manager.enforce(dry_run=False)
for action in actions:
    if action['action'] == 'rotate':
        print(f"Rotated: {action['file']}")
```

### Dry Run

```python
# Check what would happen
actions = manager.enforce(dry_run=True)

for action in actions:
    print(f"{action['action']}: {action['file']}")
    print(f"  Reason: {action['reason']}")

# Confirm and execute
if actions:
    print(f"\nExecuting {len(actions)} actions...")
    manager.enforce(dry_run=False)
```

### Action History

```python
# Get action log
log = manager.get_actions_log()
print(f"Total actions: {len(log)}")

# Show recent actions
for action in log[-10:]:
    print(f"{action['action']}: {action['file']}")
```

### Statistics

```python
stats = manager.stats
print(f"Policies: {stats['policies']}")
print(f"Actions taken: {stats['actions_taken']}")
```

## See Also

- [Reader](reader.md) - File reading utilities
