# CLI Usage Guide

Complete reference for the Modular Log Analysis Toolkit command-line interface.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Command Reference](#command-reference)
- [Options](#options)
- [Examples](#examples)
- [Output Formats](#output-formats)
- [Error Handling](#error-handling)

## Basic Usage

```bash
python -m src.cli [OPTIONS] INPUT [INPUT ...]
```

### Simplest Command

```bash
# Analyze a log file and print entries
python -m src.cli app.log
```

### Show Summary

```bash
# Show summary statistics
python -m src.cli app.log --summary
```

## Command Reference

### Positional Arguments

| Argument | Description |
|----------|-------------|
| `INPUT` | Log file(s) to analyze (one or more) |

### Optional Arguments

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output file path |
| `--format` | `-f` | Output format: json, csv, text |
| `--pattern` | `-p` | Log format pattern (default: standard) |
| `--level` | `-l` | Filter by log level (can be repeated) |
| `--source` | `-s` | Filter by log source |
| `--keyword` | `-k` | Filter by keyword |
| `--since` | | Start time filter (YYYY-MM-DD HH:MM:SS) |
| `--until` | | End time filter (YYYY-MM-DD HH:MM:SS) |
| `--summary` | | Show summary statistics |
| `--top-errors` | | Number of top errors to show (default: 10) |
| `--verbose` | `-v` | Verbose output |
| `--quiet` | `-q` | Suppress non-essential output |
| `--version` | | Show version and exit |
| `--help` | `-h` | Show help message |

## Options

### Output Options

#### Output File (`-o`, `--output`)

Specify the output file path:

```bash
python -m src.cli app.log -o output.json
```

If not specified, output is printed to stdout.

#### Output Format (`-f`, `--format`)

Choose the output format:

```bash
# JSON format (default)
python -m src.cli app.log -f json -o output.json

# CSV format
python -m src.cli app.log -f csv -o output.csv

# Plain text format
python -m src.cli app.log -f text -o output.txt
```

### Filter Options

#### Log Level (`-l`, `--level`)

Filter by log level. Can be used multiple times:

```bash
# Single level
python -m src.cli app.log -l ERROR

# Multiple levels
python -m src.cli app.log -l ERROR -l CRITICAL

# All error levels
python -m src.cli app.log -l ERROR -l CRITICAL -l WARN
```

**Available Levels:**
- `DEBUG` - Debug messages
- `INFO` - Informational messages
- `WARN` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors
- `TRACE` - Trace messages

#### Source Filter (`-s`, `--source`)

Filter by log source:

```bash
python -m src.cli app.log -s "database"
python -m src.cli app.log -s "auth-service"
```

#### Keyword Filter (`-k`, `--keyword`)

Filter by keyword in message:

```bash
python -m src.cli app.log -k "timeout"
python -m src.cli app.log -k "connection failed"
```

#### Time Range Filters

Filter by time range:

```bash
# After a specific time
python -m src.cli app.log --since "2024-01-15 10:00:00"

# Before a specific time
python -m src.cli app.log --until "2024-01-15 12:00:00"

# Within a time range
python -m src.cli app.log --since "2024-01-15 10:00:00" --until "2024-01-15 12:00:00"
```

### Pattern Options

#### Log Pattern (`-p`, `--pattern`)

Specify the log format pattern:

```bash
# Standard format (default)
python -m src.cli app.log -p standard

# Syslog format
python -m src.cli app.log -p syslog

# Apache format
python -m src.cli app.log -p apache
```

**Available Patterns:**
- `standard` - `YYYY-MM-DD HH:MM:SS [LEVEL] message`
- `syslog` - `MMM DD HH:MM:SS host program[pid]: message`
- `apache` - `IP - - [timestamp] "request" status size`
- `json_log` - JSON formatted logs

### Display Options

#### Summary (`--summary`)

Show summary statistics:

```bash
python -m src.cli app.log --summary
```

**Output:**
```
Total entries: 1234
Level counts: {'INFO': 1000, 'ERROR': 200, 'WARN': 34}
Error rate: 16.21%
Top sources: [('app', 800), ('database', 400)]
```

#### Top Errors (`--top-errors`)

Number of top errors to show (default: 10):

```bash
python -m src.cli app.log --summary --top-errors 20
```

#### Verbose (`-v`, `--verbose`)

Enable verbose output:

```bash
python -m src.cli app.log -v
```

#### Quiet (`-q`, `--quiet`)

Suppress non-essential output:

```bash
python -m src.cli app.log -q
```

**Note:** Verbose and quiet are mutually exclusive.

## Examples

### Basic Examples

```bash
# Show help
python -m src.cli --help

# Show version
python -m src.cli --version

# Analyze single file
python -m src.cli app.log

# Analyze multiple files
python -m src.cli app.log system.log access.log
```

### Filtering Examples

```bash
# Show only errors
python -m src.cli app.log -l ERROR

# Show errors and critical
python -m src.cli app.log -l ERROR -l CRITICAL

# Filter by source
python -m src.cli app.log -s "database"

# Filter by keyword
python -m src.cli app.log -k "timeout"

# Combine filters
python -m src.cli app.log -l ERROR -k "database" -s "auth"
```

### Export Examples

```bash
# Export to JSON
python -m src.cli app.log -f json -o output.json

# Export errors to CSV
python -m src.cli app.log -l ERROR -f csv -o errors.csv

# Export filtered results
python -m src.cli app.log -l ERROR -k "timeout" -f json -o timeout_errors.json
```

### Time Range Examples

```bash
# Logs from today
python -m src.cli app.log --since "2024-01-15 00:00:00"

# Logs from a specific hour
python -m src.cli app.log --since "2024-01-15 10:00:00" --until "2024-01-15 11:00:00"

# Recent logs
python -m src.cli app.log --since "2024-01-15 12:00:00"
```

### Advanced Examples

```bash
# Analyze syslog
python -m src.cli /var/log/syslog -p syslog --summary

# Analyze Apache logs
python -m src.cli /var/log/apache2/access.log -p apache -l ERROR -f json -o apache_errors.json

# Process compressed logs
python -m src.cli app.log.gz -p standard -f csv -o output.csv

# Full analysis
python -m src.cli app.log -l ERROR -l CRITICAL -k "database" --since "2024-01-01" --summary --top-errors 20 -v
```

## Output Formats

### JSON Format

```json
[
  {
    "timestamp": "2024-01-15T10:30:45",
    "level": "ERROR",
    "message": "Database connection timeout",
    "source": "database",
    "line_number": 42,
    "tags": {}
  }
]
```

### CSV Format

```csv
timestamp,level,source,message,line_number
2024-01-15T10:30:45,ERROR,database,Database connection timeout,42
```

### Text Format

```
[ERROR] 2024-01-15 10:30:45 - Database connection timeout
[INFO] 2024-01-15 10:31:00 - Connection restored
```

## Error Handling

### Common Errors

#### File Not Found

```
Error: file not found: nonexistent.log
```

**Solution:** Check the file path and ensure the file exists.

#### Permission Denied

```
Error: permission denied: /var/log/syslog
```

**Solution:** Use `sudo` or check file permissions.

#### Invalid Pattern

```
Error: Unknown pattern: invalid_pattern. Available patterns: standard, syslog, apache, json_log
```

**Solution:** Use a valid pattern name.

#### Invalid Time Format

```
Error: Invalid time format. Use: YYYY-MM-DD HH:MM:SS
```

**Solution:** Use the correct time format.

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (file not found, permission denied, etc.) |

## Tips and Tricks

### Combine Multiple Filters

```bash
# Complex filtering
python -m src.cli app.log \
  -l ERROR -l CRITICAL \
  -s "database" \
  -k "timeout" \
  --since "2024-01-15 10:00:00" \
  -f json \
  -o filtered_errors.json
```

### Process Multiple Files

```bash
# Analyze multiple files
python -m src.cli *.log --summary

# Specific files
python -m src.cli app.log system.log access.log -l ERROR
```

### Use with Other Tools

```bash
# Count errors
python -m src.cli app.log -l ERROR | wc -l

# Search output
python -m src.cli app.log | grep "timeout"

# Pipe to another command
python -m src.cli app.log -f json | jq '.[] | select(.level == "ERROR")'
```

### Create Aliases

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
alias loganalyze='python -m src.cli'
alias logerrors='python -m src.cli -l ERROR -l CRITICAL'
alias logsummary='python -m src.cli --summary'
```

Then use:

```bash
loganalyze app.log --summary
logerrors app.log -f json -o errors.json
logsummary app.log
```

## See Also

- [Python API](python-api.md) - Programmatic usage
- [Configuration](configuration.md) - Configuration options
- [FAQ](faq.md) - Frequently asked questions
