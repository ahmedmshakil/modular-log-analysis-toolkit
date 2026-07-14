# Configuration Guide

modular-log-analysis-toolkit uses YAML files in the `config/` directory for configuration.

## settings.yaml

Main configuration file for the analyzer.

```yaml
log_paths:
  - /var/log/syslog
  - /var/log/app/*.log

output_format: json
output_dir: ./output

retention:
  max_age_days: 30
  compress_after_days: 7
  max_size_mb: 500

parser:
  default_pattern: standard
  custom_patterns_dir: ./config/patterns
```

## alerts.yaml

Configure alert thresholds and notification channels.

```yaml
thresholds:
  error_rate: 5.0       # Alert if error rate exceeds 5%
  critical_count: 10    # Alert on 10+ critical errors

channels:
  slack:
    webhook_url: "https://hooks.slack.com/..."
    channel: "#alerts"
  email:
    smtp_host: "smtp.example.com"
    recipients: ["admin@example.com"]
```

## patterns.yaml

Define custom log format patterns using regex with named groups.

```yaml
patterns:
  my_app: '(?P<timestamp>\d{4}-\d{2}-\d{2}) (?P<level>\w+) (?P<message>.*)'
  nginx: '(?P<ip>\S+) - .* "(?P<request>[^"]*)" (?P<status>\d+)'
```

## Environment Variables

Override configuration via environment variables:

- `SK_LOG_PATH` — Override log file path
- `SK_OUTPUT_DIR` — Override output directory
- `SK_LOG_LEVEL` — Set minimum log level to process

## Cache Configuration

Configure caching behavior for performance optimization:

```yaml
cache:
  max_size: 1000        # Maximum cache entries
  ttl: 300              # Time to live in seconds
  query_cache_size: 500 # Search query cache size
```

## Streaming Configuration

Configure streaming mode for large files:

```yaml
streaming:
  batch_size: 1000      # Entries per batch
  buffer_size: 8192     # Read buffer size in bytes
```
