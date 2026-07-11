# Usage Examples

## Basic Log Parsing

```python
from src.parser import LogParser
from src.reader import read_log_lines

parser = LogParser(pattern_name="standard")
lines = list(read_log_lines("/var/log/app.log"))
entries = parser.parse_lines(lines)

for entry in entries[:5]:
    print(f"[{entry.level.value}] {entry.message}")
```

## Filtering Errors from Last Hour

```python
from datetime import datetime, timedelta
from src.filter import LogFilter
from src.models import LogLevel

cutoff = datetime.now() - timedelta(hours=1)
errors = (LogFilter(entries)
          .by_level(LogLevel.ERROR, LogLevel.CRITICAL)
          .by_time_range(cutoff, datetime.now())
          .apply())
print(f"Found {len(errors)} recent errors")
```

## Export to CSV

```python
from src.exporter import LogExporter

exporter = LogExporter()
path = exporter.to_csv(entries, "output/report.csv")
print(f"Exported to {path}")
```

## Real-time Monitoring

```python
from src.streaming import LogStream

stream = LogStream("/var/log/syslog")
stream.stream(lambda entry: print(entry) if entry.level.value == "ERROR" else None)
```

## Custom Pattern

```python
pattern = r'(?P<ip>\S+) - .* "(?P<method>\w+) (?P<path>\S+)" (?P<status>\d+)'
parser = LogParser(custom_pattern=pattern)
entries = parser.parse_lines(access_log_lines)
```

## Webhook Alerting

```python
from src.alerts import AlertManager, AlertSeverity
from src.webhooks import WebhookSender

webhook = WebhookSender("https://hooks.slack.com/services/xxx")
alerts = AlertManager()
alerts.set_threshold("error_rate", 10, severity=AlertSeverity.HIGH)
alerts.register_callback(lambda alert: webhook.send(alert.message))
alerts.check("error_rate", 12)
```
