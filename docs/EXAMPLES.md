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

## Deduplication

```python
from src.dedup import LogDeduplicator

dedup = LogDeduplicator()
unique_entries, counts = dedup.deduplicate(entries)
print(f"Removed {dedup.total_duplicates_removed()} duplicates")
```

## Search Index

```python
from src.search import LogSearchIndex

index = LogSearchIndex()
index.add_batch(entries)

results = index.search("database timeout")
suggestions = index.suggest("data")
```

## Geolocation Enrichment

```python
from src.geolocation import GeoLookup

geo = GeoLookup()
ips = geo.extract_ips_from_entries(entries)
locations = geo.lookup_batch(ips)
```

## Caching Results

```python
from src.cache import LRUCache, cached

cache = LRUCache(max_size=1000, ttl=300)
cache.put("analysis", results)
cached_result = cache.get("analysis")

@cached(ttl=600)
def expensive_analysis(data):
    return process(data)
```
