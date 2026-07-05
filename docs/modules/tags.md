# Tags Module

The `tags` module provides custom tagging and labeling capabilities for log entries.

## Table of Contents

- [Overview](#overview)
- [TagRule Class](#tagrule-class)
- [TagManager Class](#tagmanager-class)
- [Usage Examples](#usage-examples)

## Overview

The tags module provides:

- **TagRule** - Automatic tagging rules based on conditions
- **TagManager** - Manage rules and manual tags
- **Color coding** - Associate colors with tags
- **Import/Export** - Save and load rules

## TagRule Class

Rule for automatically tagging log entries.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Rule name |
| `tag` | `str` | required | Tag to apply |
| `conditions` | `Dict[str, str]` | required | Field -> pattern conditions |
| `color` | `str` | `"#808080"` | Tag color |
| `priority` | `int` | `0` | Rule priority |

### Methods

#### matches

```python
matches(entry_dict: Dict) -> bool
```

Check if an entry matches this rule.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entry_dict` | `Dict` | Entry as dictionary |

**Returns:** `bool` - True if entry matches

**Example:**

```python
rule = TagRule(
    name="db_errors",
    tag="database",
    conditions={"message": "database", "level": "ERROR"}
)

entry_dict = {"message": "Database connection failed", "level": "ERROR"}
if rule.matches(entry_dict):
    print("Matches!")
```

### Special Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |

## TagManager Class

Manage tags and labels for log entries.

### Constructor

```python
TagManager()
```

### Methods

#### add_rule

```python
add_rule(rule: TagRule) -> None
```

Add an automatic tagging rule.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `rule` | `TagRule` | Rule to add |

**Raises:** `ValueError` - If rule has no name or tag

**Example:**

```python
manager = TagManager()
rule = TagRule(
    name="db_errors",
    tag="database",
    conditions={"message": "database"}
)
manager.add_rule(rule)
```

#### bulk_add

```python
bulk_add(rules: List[TagRule]) -> int
```

Add multiple rules at once.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `rules` | `List[TagRule]` | Rules to add |

**Returns:** `int` - Number of rules added

**Example:**

```python
rules = [
    TagRule(name="rule1", tag="tag1", conditions={"message": "error"}),
    TagRule(name="rule2", tag="tag2", conditions={"level": "ERROR"})
]
added = manager.bulk_add(rules)
print(f"Added {added} rules")
```

#### remove_rule

```python
remove_rule(name: str) -> None
```

Remove a tagging rule by name.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Rule name |

**Example:**

```python
manager.remove_rule("db_errors")
```

#### has_rule

```python
has_rule(name: str) -> bool
```

Check if a rule with the given name exists.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Rule name |

**Returns:** `bool` - True if rule exists

**Example:**

```python
if manager.has_rule("db_errors"):
    print("Rule exists")
```

#### apply_rules

```python
apply_rules(entries: List[Dict]) -> List[Dict]
```

Apply tagging rules to entries.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entries` | `List[Dict]` | Entries as dictionaries |

**Returns:** `List[Dict]` - Entries with tags added

**Example:**

```python
entries = [
    {"message": "Database error", "level": "ERROR", "line_number": 1},
    {"message": "User login", "level": "INFO", "line_number": 2}
]
tagged = manager.apply_rules(entries)
```

#### add_manual_tag

```python
add_manual_tag(line_number: int, tag: str) -> None
```

Manually add a tag to an entry.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `line_number` | `int` | Line number |
| `tag` | `str` | Tag to add |

**Example:**

```python
manager.add_manual_tag(42, "investigate")
```

#### remove_manual_tag

```python
remove_manual_tag(line_number: int, tag: str) -> None
```

Remove a manual tag.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `line_number` | `int` | Line number |
| `tag` | `str` | Tag to remove |

**Example:**

```python
manager.remove_manual_tag(42, "investigate")
```

#### get_tags

```python
get_tags(line_number: int) -> Set[str]
```

Get all tags for an entry.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `line_number` | `int` | Line number |

**Returns:** `Set[str]` - Set of tags

**Example:**

```python
tags = manager.get_tags(42)
print(f"Tags: {tags}")
```

#### get_all_tags

```python
get_all_tags() -> Dict[str, int]
```

Get all tags with their counts.

**Returns:** `Dict[str, int]` - Tag counts

**Example:**

```python
all_tags = manager.get_all_tags()
for tag, count in all_tags.items():
    print(f"{tag}: {count}")
```

#### get_color

```python
get_color(tag: str) -> str
```

Get color for a tag.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `tag` | `str` | Tag name |

**Returns:** `str` - Color hex code

**Example:**

```python
color = manager.get_color("database")
print(f"Color: {color}")
```

#### reset

```python
reset() -> None
```

Clear all rules, manual tags, and color mappings.

**Example:**

```python
manager.reset()
```

#### export_rules

```python
export_rules(path: str) -> None
```

Export rules to JSON file.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | Output file path |

**Example:**

```python
manager.export_rules("rules.json")
```

#### import_rules

```python
import_rules(path: str) -> None
```

Import rules from JSON file.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | Input file path |

**Raises:** `ValueError` - If import fails

**Example:**

```python
manager.import_rules("rules.json")
```

## Usage Examples

### Basic Tagging

```python
from src.tags import TagManager, TagRule

# Create manager
manager = TagManager()

# Add rule
rule = TagRule(
    name="db_errors",
    tag="database",
    conditions={"message": "database", "level": "ERROR"},
    color="#ff0000",
    priority=10
)
manager.add_rule(rule)

# Apply rules
entries = [
    {"message": "Database connection failed", "level": "ERROR", "line_number": 1},
    {"message": "User login successful", "level": "INFO", "line_number": 2}
]
tagged = manager.apply_rules(entries)

# Check tags
for entry in tagged:
    print(f"Line {entry['line_number']}: {entry.get('tags', [])}")
```

### Manual Tags

```python
# Add manual tag
manager.add_manual_tag(42, "investigate")
manager.add_manual_tag(42, "high-priority")

# Get tags
tags = manager.get_tags(42)
print(f"Tags for line 42: {tags}")

# Remove tag
manager.remove_manual_tag(42, "investigate")
```

### Multiple Rules

```python
rules = [
    TagRule(
        name="db_errors",
        tag="database",
        conditions={"message": "database"},
        color="#ff0000"
    ),
    TagRule(
        name="auth_events",
        tag="auth",
        conditions={"message": "login"},
        color="#00ff00"
    ),
    TagRule(
        name="errors",
        tag="error",
        conditions={"level": "ERROR"},
        color="#ff0000"
    )
]

added = manager.bulk_add(rules)
print(f"Added {added} rules")
```

### Check Rules

```python
if manager.has_rule("db_errors"):
    print("Rule exists")
else:
    print("Rule not found")
```

### Get All Tags

```python
all_tags = manager.get_all_tags()
print("All tags:")
for tag, count in sorted(all_tags.items(), key=lambda x: x[1], reverse=True):
    print(f"  {tag}: {count}")
```

### Export/Import Rules

```python
# Export
manager.export_rules("tag_rules.json")

# Import
manager.import_rules("tag_rules.json")
```

### Reset

```python
manager.reset()
print("All rules and tags cleared")
```

## See Also

- [Models](models.md) - LogEntry structure
- [Filter](filter.md) - Filter by tags
