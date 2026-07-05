# Alerts Module

The `alerts` module provides threshold-based alerting for log monitoring.

## Table of Contents

- [Overview](#overview)
- [AlertSeverity](#alertseverity)
- [Alert Class](#alert-class)
- [AlertManager Class](#alertmanager-class)
- [Usage Examples](#usage-examples)

## Overview

The alerts module provides:

- **AlertSeverity** - Alert severity levels
- **Alert** - Individual alert instance
- **AlertManager** - Manage thresholds and notifications
- **Callbacks** - Custom notification handlers

## AlertSeverity

An enumeration of alert severity levels.

### Values

| Value | Description |
|-------|-------------|
| `LOW` | Low severity |
| `MEDIUM` | Medium severity |
| `HIGH` | High severity |
| `CRITICAL` | Critical severity |

### Usage

```python
from src.alerts import AlertSeverity

print(AlertSeverity.HIGH)        # AlertSeverity.HIGH
print(AlertSeverity.HIGH.value)  # "high"
```

## Alert Class

Represents a triggered alert.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `severity` | `AlertSeverity` | Alert severity |
| `message` | `str` | Alert message |
| `metric_name` | `str` | Name of the metric |
| `current_value` | `float` | Current metric value |
| `threshold` | `float` | Threshold value |
| `timestamp` | `datetime` | When alert was triggered |
| `acknowledged` | `bool` | Whether alert is acknowledged |
| `acknowledged_at` | `Optional[datetime]` | When alert was acknowledged |

### Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |
| `__str__()` | Human-readable string |
| `to_dict()` | Convert to dictionary |
| `to_json()` | Convert to JSON string |

## AlertManager Class

Manage alert thresholds and notifications.

### Constructor

```python
AlertManager()
```

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `thresholds` | `Dict[str, Dict]` | Metric thresholds |
| `alerts` | `List[Alert]` | Triggered alerts |
| `callbacks` | `List[Callable]` | Notification callbacks |

### Methods

#### set_threshold

```python
set_threshold(metric: str, value: float, severity: AlertSeverity = AlertSeverity.MEDIUM) -> None
```

Set an alert threshold.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metric` | `str` | required | Metric name |
| `value` | `float` | required | Threshold value |
| `severity` | `AlertSeverity` | `MEDIUM` | Alert severity |

**Example:**

```python
manager = AlertManager()
manager.set_threshold("error_rate", 5.0, AlertSeverity.HIGH)
manager.set_threshold("response_time", 1000, AlertSeverity.MEDIUM)
```

#### check

```python
check(metric: str, current_value: float) -> Optional[Alert]
```

Check if a metric exceeds its threshold.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `metric` | `str` | Metric name |
| `current_value` | `float` | Current value |

**Returns:** `Optional[Alert]` - Alert if threshold exceeded, None otherwise

**Example:**

```python
alert = manager.check("error_rate", 7.5)
if alert:
    print(f"Alert: {alert}")
```

#### register_callback

```python
register_callback(callback: Callable[[Alert], None]) -> None
```

Register a notification callback.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `callback` | `Callable[[Alert], None]` | Callback function |

**Example:**

```python
def on_alert(alert):
    print(f"ALERT: {alert}")

manager.register_callback(on_alert)
```

#### get_active_alerts

```python
get_active_alerts() -> List[Alert]
```

Get unacknowledged alerts.

**Returns:** `List[Alert]` - Active alerts

**Example:**

```python
active = manager.get_active_alerts()
for alert in active:
    print(f"Active: {alert}")
```

#### acknowledge

```python
acknowledge(index: int) -> None
```

Acknowledge an alert by index.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | `int` | Alert index |

**Raises:** `TypeError` - If index is not an integer

**Example:**

```python
manager.acknowledge(0)  # Acknowledge first alert
```

#### Properties

##### alert_count

```python
@property
alert_count -> int
```

Get total number of alerts.

**Example:**

```python
count = manager.alert_count
print(f"Total alerts: {count}")
```

#### clear_alerts

```python
clear_alerts() -> None
```

Remove all alerts.

**Example:**

```python
manager.clear_alerts()
```

#### export_alerts

```python
export_alerts(output_path: str) -> None
```

Export alerts to JSON file.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `output_path` | `str` | Output file path |

**Example:**

```python
manager.export_alerts("alerts.json")
```

## Usage Examples

### Basic Setup

```python
from src.alerts import AlertManager, AlertSeverity

# Create manager
manager = AlertManager()

# Set thresholds
manager.set_threshold("error_rate", 5.0, AlertSeverity.HIGH)
manager.set_threshold("response_time", 1000, AlertSeverity.MEDIUM)
manager.set_threshold("disk_usage", 90.0, AlertSeverity.CRITICAL)
```

### Check Metrics

```python
from src.aggregator import LogAggregator

aggregator = LogAggregator(entries)

# Check error rate
error_rate = aggregator.error_rate()
alert = manager.check("error_rate", error_rate)

if alert:
    print(f"Alert triggered: {alert}")
else:
    print("No alert")
```

### Register Callbacks

```python
def on_alert(alert):
    print(f"ALERT: {alert.severity.value} - {alert.message}")
    # Send notification, log to file, etc.

manager.register_callback(on_alert)
```

### Manage Alerts

```python
# Get all alerts
all_alerts = manager.alerts

# Get active (unacknowledged) alerts
active = manager.get_active_alerts()
print(f"Active alerts: {len(active)}")

# Acknowledge first alert
if active:
    manager.acknowledge(0)

# Get alert count
count = manager.alert_count
print(f"Total alerts: {count}")

# Clear all alerts
manager.clear_alerts()
```

### Export Alerts

```python
# Export to JSON
manager.export_alerts("alerts.json")
```

### Complete Monitoring Example

```python
from src.alerts import AlertManager, AlertSeverity
from src.aggregator import LogAggregator
from src.webhooks import WebhookSender

# Setup
manager = AlertManager()
manager.set_threshold("error_rate", 5.0, AlertSeverity.HIGH)
manager.set_threshold("error_count", 100, AlertSeverity.CRITICAL)

webhook = WebhookSender("https://hooks.slack.com/xxx")

def send_notification(alert):
    webhook.send_alert(alert)
    print(f"Notification sent: {alert}")

manager.register_callback(send_notification)

# Monitor
aggregator = LogAggregator(entries)
error_rate = aggregator.error_rate()
error_count = aggregator.count_entries(LogLevel.ERROR)

manager.check("error_rate", error_rate)
manager.check("error_count", error_count)

# Get results
active = manager.get_active_alerts()
print(f"Active alerts: {len(active)}")
```

## See Also

- [Webhooks](webhooks.md) - Send alert notifications
- [Aggregator](aggregator.md) - Generate metrics for alerting
