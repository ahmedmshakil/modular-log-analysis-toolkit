# Documentation Index

Welcome to the Modular Log Analysis Toolkit documentation. This directory contains comprehensive guides and references for using the toolkit.

## Table of Contents

### Getting Started
- [Installation Guide](installation.md) - How to install and set up the toolkit
- [Quick Start Guide](quickstart.md) - Get up and running in 5 minutes
- [Configuration](configuration.md) - System configuration options

### User Guides
- [CLI Usage](cli-usage.md) - Command-line interface guide
- [Python API](python-api.md) - Python API reference
- [Web Dashboard](dashboard.md) - Real-time monitoring dashboard

### Module Documentation
- [Models](modules/models.md) - Data models and structures
- [Parser](modules/parser.md) - Log parsing engine
- [Filter](modules/filter.md) - Filtering and query engine
- [Aggregator](modules/aggregator.md) - Statistics and aggregation
- [Search](modules/search.md) - Full-text search indexing
- [Exporter](modules/exporter.md) - Data export formats
- [Deduplication](modules/dedup.md) - Duplicate detection and removal
- [Streaming](modules/streaming.md) - Large file processing
- [Alerts](modules/alerts.md) - Alert system and thresholds
- [Webhooks](modules/webhooks.md) - Webhook notifications
- [Tags](modules/tags.md) - Tagging and labeling system
- [Plugins](modules/plugins.md) - Plugin development
- [Retention](modules/retention.md) - Log retention policies
- [Geolocation](modules/geolocation.md) - IP geolocation lookup
- [Authentication](modules/auth.md) - User authentication and authorization
- [Cache](modules/cache.md) - Caching layer

### Developer Guides
- [Plugin Development](plugin-development.md) - Creating custom plugins
- [Contributing](contributing.md) - How to contribute
- [Architecture](architecture.md) - System architecture overview
- [Testing](testing.md) - Running and writing tests

### Reference
- [API Reference](api-reference.md) - Complete API documentation
- [Error Codes](error-codes.md) - Common error codes and solutions
- [FAQ](faq.md) - Frequently asked questions

## Documentation Files

### Main Documentation

| File | Description |
|------|-------------|
| [installation.md](installation.md) | Installation instructions for different platforms |
| [quickstart.md](quickstart.md) | Quick start guide with basic examples |
| [configuration.md](configuration.md) | Configuration file reference |
| [cli-usage.md](cli-usage.md) | Complete CLI command reference |
| [python-api.md](python-api.md) | Python API usage guide |
| [dashboard.md](dashboard.md) | Web dashboard setup and usage |

### Module Documentation

| File | Description |
|------|-------------|
| [modules/models.md](modules/models.md) | LogEntry, LogLevel, AnalysisResult |
| [modules/parser.md](modules/parser.md) | Log parsing and pattern matching |
| [modules/filter.md](modules/filter.md) | Filtering engine documentation |
| [modules/aggregator.md](modules/aggregator.md) | Statistics and aggregation |
| [modules/search.md](modules/search.md) | Full-text search indexing |
| [modules/exporter.md](modules/exporter.md) | Export to JSON, CSV, text |
| [modules/dedup.md](modules/dedup.md) | Deduplication engine |
| [modules/streaming.md](modules/streaming.md) | Streaming mode for large files |
| [modules/alerts.md](modules/alerts.md) | Alert system documentation |
| [modules/webhooks.md](modules/webhooks.md) | Webhook integration guide |
| [modules/tags.md](modules/tags.md) | Tagging system documentation |
| [modules/plugins.md](modules/plugins.md) | Plugin system documentation |
| [modules/retention.md](modules/retention.md) | Retention policy documentation |
| [modules/geolocation.md](modules/geolocation.md) | Geolocation lookup guide |
| [modules/auth.md](modules/auth.md) | Authentication documentation |
| [modules/cache.md](modules/cache.md) | Caching system documentation |

### Developer Documentation

| File | Description |
|------|-------------|
| [plugin-development.md](plugin-development.md) | Guide to developing plugins |
| [contributing.md](contributing.md) | Contribution guidelines |
| [architecture.md](architecture.md) | System architecture overview |
| [testing.md](testing.md) | Testing guide |

### Reference Documentation

| File | Description |
|------|-------------|
| [api-reference.md](api-reference.md) | Complete API reference |
| [error-codes.md](error-codes.md) | Error code reference |
| [faq.md](faq.md) | Frequently asked questions |

## Quick Links

- **New to the toolkit?** Start with [Quick Start Guide](quickstart.md)
- **Want to use the CLI?** See [CLI Usage](cli-usage.md)
- **Building integrations?** Check [Python API](python-api.md)
- **Creating plugins?** Read [Plugin Development](plugin-development.md)
- **Need help?** Check [FAQ](faq.md)

## Search Documentation

Use the search functionality of your IDE or text editor to find specific topics across all documentation files.

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-format Parsing** | Parse standard, syslog, Apache, and custom log formats |
| **Advanced Filtering** | Filter by level, time range, source, keyword, and regex |
| **Full-text Search** | In-memory search index with stop-word filtering |
| **Deduplication** | Hash-based duplicate detection and removal |
| **Streaming Mode** | Memory-efficient processing of large log files |
| **Export** | Export to JSON, CSV, and plain text formats |
| **Alerts** | Configurable thresholds with callback notifications |
| **Web Dashboard** | Real-time monitoring with dark/light theme |
| **Plugin System** | Extensible architecture with custom plugins |
| **Caching** | LRU cache with TTL for performance optimization |
| **Geolocation** | IP address lookup with caching |
| **Retention Policies** | Automated log compression, rotation, and deletion |
| **Authentication** | Role-based access control (viewer, analyst, admin) |
| **Webhooks** | Send alerts to external endpoints |
| **Tagging** | Rule-based and manual log categorization |

## Documentation Updates

This documentation is regularly updated. Last update: 2026

## Quick Reference

### Common Import Patterns

```python
# Core models
from src.models import LogEntry, LogLevel, AnalysisResult

# Parsing
from src.parser import LogParser
from src.reader import read_log_lines

# Filtering and analysis
from src.filter import LogFilter
from src.aggregator import LogAggregator

# Export
from src.exporter import LogExporter

# Search
from src.search import LogSearchIndex

# Streaming
from src.streaming import LogStream
```

### Log Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| TRACE | Finest-grained debug info | Detailed tracing |
| DEBUG | Debug information | Development debugging |
| INFO | General information | Normal operations |
| WARN | Warning messages | Potential issues |
| ERROR | Error messages | Failures |
| CRITICAL | Critical failures | System-breaking issues |

## Feedback

Found an error or have a suggestion? Please open an issue on GitHub.

## Module Overview

| Module        | Description                              |
| ------------- | ---------------------------------------- |
| `models.py`   | Data models: LogEntry, LogLevel, AnalysisResult |
| `parser.py`   | Log parsing with pattern matching        |
| `filter.py`   | Chainable filtering engine               |
| `aggregator.py` | Statistics and aggregation              |
| `exporter.py` | JSON, CSV, text export                   |
| `reader.py`   | File reading utilities                   |
| `search.py`   | Full-text search indexing                |
| `dedup.py`    | Duplicate detection                      |
| `streaming.py` | Large file processing                   |
| `alerts.py`   | Threshold-based alerting                 |
| `webhooks.py` | Webhook notifications                    |
| `tags.py`     | Tagging system                           |
| `plugins.py`  | Plugin architecture                      |
| `retention.py` | Log retention policies                  |
| `geolocation.py` | IP geolocation lookup                  |
| `auth.py`     | User authentication                      |
| `cache.py`    | LRU caching layer                        |
| `web.py`      | Web dashboard                            |
| `cli.py`      | Command-line interface                   |
