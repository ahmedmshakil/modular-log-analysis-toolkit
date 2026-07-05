# Webhooks Module

The `webhooks` module provides webhook notification capabilities for log alerts.

## Table of Contents

- [Overview](#overview)
- [WebhookSender Class](#webhooksender-class)
- [WebhookRouter Class](#webhookrouter-class)
- [Usage Examples](#usage-examples)

## Overview

The webhooks module provides:

- **WebhookSender** - Send HTTP POST requests with JSON payloads
- **WebhookRouter** - Route webhooks to multiple endpoints
- **Statistics** - Track send success/failure rates

## WebhookSender Class

Send webhook notifications for log events.

### Constructor

```python
WebhookSender(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | required | Webhook URL |
| `headers` | `Optional[Dict[str, str]]` | `None` | HTTP headers |
| `timeout` | `int` | `10` | Request timeout in seconds |

**Raises:**
- `ValueError` - If URL is empty or invalid
- `TypeError` - If timeout is not a number

### Methods

#### send_alert

```python
send_alert(entry: LogEntry, extra: Optional[Dict[str, Any]] = None) -> bool
```

Send a webhook alert for a log entry.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entry` | `LogEntry` | required | Log entry to send |
| `extra` | `Optional[Dict[str, Any]]` | `None` | Extra data to include |

**Returns:** `bool` - True if sent successfully

**Example:**

```python
sender = WebhookSender("https://hooks.slack.com/xxx")
success = sender.send_alert(entry)
```

#### send_summary

```python
send_summary(level_counts: Dict[str, int], error_rate: float) -> bool
```

Send a summary webhook.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `level_counts` | `Dict[str, int]` | Count per log level |
| `error_rate` | `float` | Error rate percentage |

**Returns:** `bool` - True if sent successfully

**Example:**

```python
success = sender.send_summary({"ERROR": 10, "INFO": 100}, 9.09)
```

#### Properties

##### stats

```python
@property
stats -> Dict[str, int]
```

Get webhook send statistics.

**Returns:** `Dict[str, int]` - Statistics including:
- `sent` - Number of successful sends
- `errors` - Number of failed sends

**Example:**

```python
stats = sender.stats
print(f"Sent: {stats['sent']}, Errors: {stats['errors']}")
```

#### reset_stats

```python
reset_stats() -> None
```

Reset send statistics.

**Example:**

```python
sender.reset_stats()
```

#### reset

```python
reset() -> None
```

Reset all sender state including stats.

**Example:**

```python
sender.reset()
```

### Special Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |

## WebhookRouter Class

Route webhooks to multiple endpoints.

### Constructor

```python
WebhookRouter()
```

### Methods

#### add_endpoint

```python
add_endpoint(name: str, url: str, **kwargs) -> None
```

Register a webhook endpoint.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Endpoint name |
| `url` | `str` | Webhook URL |
| `**kwargs` | | Additional WebhookSender options |

**Raises:** `ValueError` - If name or URL is empty

**Example:**

```python
router = WebhookRouter()
router.add_endpoint("slack", "https://hooks.slack.com/xxx")
router.add_endpoint("discord", "https://discord.com/api/webhooks/xxx", timeout=30)
```

#### remove_endpoint

```python
remove_endpoint(name: str) -> None
```

Remove a webhook endpoint.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Endpoint name |

**Example:**

```python
router.remove_endpoint("slack")
```

#### send_to_all

```python
send_to_all(entry: LogEntry) -> Dict[str, bool]
```

Send alert to all registered endpoints.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `entry` | `LogEntry` | Log entry to send |

**Returns:** `Dict[str, bool]` - Results per endpoint

**Example:**

```python
results = router.send_to_all(entry)
for endpoint, success in results.items():
    print(f"{endpoint}: {'success' if success else 'failed'}")
```

#### send_to

```python
send_to(name: str, entry: LogEntry) -> bool
```

Send alert to a specific endpoint.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Endpoint name |
| `entry` | `LogEntry` | Log entry to send |

**Returns:** `bool` - True if sent successfully

**Example:**

```python
success = router.send_to("slack", entry)
```

#### list_endpoints

```python
list_endpoints() -> list
```

List registered endpoints.

**Returns:** `list` - Endpoint names

**Example:**

```python
endpoints = router.list_endpoints()
print(f"Endpoints: {endpoints}")
```

#### Properties

##### endpoint_count

```python
@property
endpoint_count -> int
```

Get number of registered endpoints.

**Example:**

```python
count = router.endpoint_count
print(f"Endpoints: {count}")
```

## Usage Examples

### Basic Webhook

```python
from src.webhooks import WebhookSender

# Create sender
sender = WebhookSender("https://hooks.slack.com/xxx")

# Send alert
success = sender.send_alert(entry)
if success:
    print("Alert sent successfully")

# Get statistics
stats = sender.stats
print(f"Sent: {stats['sent']}, Errors: {stats['errors']}")
```

### Send Summary

```python
from src.webhooks import WebhookSender
from src.aggregator import LogAggregator

sender = WebhookSender("https://hooks.slack.com/xxx")
aggregator = LogAggregator(entries)

summary = aggregator.summary()
sender.send_summary(summary.level_counts, aggregator.error_rate())
```

### Multiple Endpoints

```python
from src.webhooks import WebhookRouter

router = WebhookRouter()

# Add endpoints
router.add_endpoint("slack", "https://hooks.slack.com/xxx")
router.add_endpoint("discord", "https://discord.com/api/webhooks/xxx")
router.add_endpoint("teams", "https://outlook.office.com/webhook/xxx")

# List endpoints
print(f"Endpoints: {router.list_endpoints()}")
print(f"Count: {router.endpoint_count}")

# Send to all
results = router.send_to_all(entry)

# Send to specific
router.send_to("slack", entry)
```

### With Alerts

```python
from src.alerts import AlertManager, AlertSeverity
from src.webhooks import WebhookSender

manager = AlertManager()
manager.set_threshold("error_rate", 5.0, AlertSeverity.HIGH)

sender = WebhookSender("https://hooks.slack.com/xxx")

def on_alert(alert):
    sender.send_alert(alert)

manager.register_callback(on_alert)

# Check metric
alert = manager.check("error_rate", 7.5)
```

### Custom Headers

```python
sender = WebhookSender(
    "https://api.example.com/webhook",
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer token123"
    },
    timeout=30
)
```

### Error Handling

```python
from src.webhooks import WebhookSender

sender = WebhookSender("https://hooks.slack.com/xxx")

# Send with error handling
try:
    success = sender.send_alert(entry)
    if not success:
        print("Failed to send alert")
except Exception as e:
    print(f"Error: {e}")

# Check statistics
stats = sender.stats
if stats['errors'] > 0:
    print(f"Warning: {stats['errors']} failed sends")
```

## See Also

- [Alerts](alerts.md) - Alert system integration
- [Models](models.md) - LogEntry structure
