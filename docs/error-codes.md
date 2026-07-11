# Error Codes

Common failure modes in the toolkit usually surface as Python exceptions or CLI exit messages.

## Typical Cases

- `FileNotFoundError`: The input log file does not exist.
- `PermissionError`: The current user cannot read the log file.
- `ValueError`: An invalid pattern, log level, or timestamp was provided.

For troubleshooting steps, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
