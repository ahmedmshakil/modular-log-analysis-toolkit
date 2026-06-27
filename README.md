# sk-loganalyzer

A powerful, modular log analysis toolkit built in Python for parsing, filtering, searching, and monitoring log files at scale.

## Features

- **Multi-format Parsing** — Supports standard, syslog, Apache, Nginx, and custom regex patterns
- **Log Filtering** — Filter by level, time range, source, keyword, or regex
- **Aggregation & Statistics** — Time-window analysis, error rates, busiest hours
- **Export** — JSON, CSV, and plain text output formats
- **Full-text Search** — Indexed word search with regex support
- **Streaming Mode** — Memory-efficient processing for large log files
- **Deduplication** — Hash-based duplicate detection
- **Alert System** — Configurable thresholds with Slack, email, and webhook notifications
- **Web Dashboard** — Real-time monitoring with auto-refresh
- **Plugin System** — Extensible architecture for custom log processors
- **Retention Policies** — Automatic compression, rotation, and cleanup
- **IP Geolocation** — Enrich network logs with location data
- **Tagging** — Custom tags and labels for log categorization
- **Authentication** — Role-based access control (viewer, analyst, admin)
- **Caching** — LRU cache for improved query performance

## Project Structure

```
sk-loganalyzer/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Data models (LogEntry, AnalysisResult)
│   ├── reader.py            # File reader utilities
│   ├── parser.py            # Log parsing engine
│   ├── filter.py            # Log filtering engine
│   ├── aggregator.py        # Statistics and aggregation
│   ├── exporter.py          # JSON/CSV/text export
│   ├── alerts.py            # Alert threshold system
│   ├── cli.py               # Command-line interface
│   ├── web.py               # Web dashboard server
│   ├── plugins.py           # Plugin system
│   ├── dedup.py             # Deduplication by hash
│   ├── streaming.py         # Streaming mode for large files
│   ├── search.py            # Full-text search indexing
│   ├── retention.py         # Log retention policies
│   ├── geolocation.py       # IP geolocation lookup
│   ├── tags.py              # Tag and label system
│   ├── webhooks.py          # Webhook notifications
│   ├── auth.py              # User authentication
│   └── cache.py             # LRU caching layer
├── tests/
│   ├── test_parser.py       # Parser unit tests
│   ├── test_filter.py       # Filter unit tests
│   └── test_aggregator.py   # Aggregator unit tests
├── config/
│   ├── settings.yaml        # Default configuration
│   ├── patterns.yaml        # Custom log patterns
│   └── alerts.yaml          # Alert thresholds
└── README.md
```

## Installation

```bash
git clone https://github.com/ahmedmshakil/sk-loganalyzer.git
cd sk-loganalyzer
pip install -e .
```

## Usage

### CLI

```bash
# Analyze a log file
python -m src.cli /var/log/syslog --summary

# Filter by level and export
python -m src.cli app.log -l ERROR -l CRITICAL -f json -o errors.json

# Search with keyword
python -m src.cli app.log -k "timeout" --summary
```

### Python API

```python
from src.parser import LogParser
from src.reader import read_log_lines
from src.filter import LogFilter
from src.aggregator import LogAggregator
from src.exporter import LogExporter

# Parse log file
parser = LogParser(pattern_name="standard")
lines = list(read_log_lines("/var/log/app.log"))
entries = parser.parse_lines(lines)

# Filter errors
errors = LogFilter(entries).by_level(LogLevel.ERROR).apply()

# Get statistics
agg = LogAggregator(entries)
print(f"Total: {agg.summary().total_entries}")
print(f"Error rate: {agg.error_rate():.2f}%")

# Export results
LogExporter.to_json(errors, "output/errors.json")
```

### Web Dashboard

```python
from src.web import start_dashboard
from src.reader import read_log_lines
from src.parser import LogParser

parser = LogParser()
entries = parser.parse_lines(list(read_log_lines("app.log")))
start_dashboard(port=8080, entries=entries)
```

## Configuration

Edit `config/settings.yaml` to configure log paths, output format, retention policies, and alert thresholds.

Custom log patterns can be added to `config/patterns.yaml` using regex with named groups.

## Running Tests

```bash
pytest tests/
```

## License

MIT
