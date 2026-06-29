# Architecture Overview

modular-log-analysis-toolkit follows a modular pipeline architecture for log processing.

## Processing Pipeline

```
Input Files → Reader → Parser → Filter → Aggregator → Exporter
                                      ↓
                                   Alerts → Webhooks/Slack
```

## Core Modules

### Reader (`src/reader.py`)
Handles file I/O including plain text and gzip-compressed log files. Provides line-by-line iteration for memory efficiency.

### Parser (`src/parser.py`)
Converts raw log lines into structured `LogEntry` objects using regex-based pattern matching. Supports syslog, Apache, standard, and custom formats.

### Filter (`src/filter.py`)
Chainable filtering engine. Supports filtering by level, time range, source, keyword, and regex pattern. Filters are composable and applied in sequence.

### Aggregator (`src/aggregator.py`)
Computes statistics: level counts, error rates, time-window grouping, busiest hours, and top sources.

### Exporter (`src/exporter.py`)
Outputs results in JSON, CSV, or plain text format.

## Supporting Modules

- **Alerts** — Threshold-based alerting with callbacks
- **Cache** — LRU cache with TTL for query performance
- **Search** — Full-text indexing with word tokenization
- **Streaming** — Memory-efficient processing for large files
- **Dedup** — Hash-based duplicate detection
- **Auth** — Role-based access control
- **Web** — Real-time monitoring dashboard
- **Plugins** — Extensible processor architecture

## Data Flow

1. Raw log files are read via `Reader`
2. Each line is parsed into a `LogEntry` dataclass
3. Filters narrow the entry set
4. Aggregator computes statistics
5. Results are exported or displayed
