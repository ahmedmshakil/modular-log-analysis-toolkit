# Error Codes

Common failure modes in the toolkit usually surface as Python exceptions or CLI exit messages.

## Typical Cases

- `FileNotFoundError`: The input log file does not exist.
- `PermissionError`: The current user cannot read the log file.
- `ValueError`: An invalid pattern, log level, or timestamp was provided.
- `TypeError`: Wrong argument type passed to a function.
- `KeyError`: Missing key in dictionary or enum lookup.
- `json.JSONDecodeError`: Invalid JSON in webhook payload or config file.
- `gzip.BadGzipFile`: Corrupted or invalid gzip file.
- `re.error`: Invalid regular expression pattern.
- `OSError`: System-level file operation failure.

## CLI Exit Codes

- Exit 0: Success
- Exit 1: General error (file not found, invalid input, no entries found)

For troubleshooting steps, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
