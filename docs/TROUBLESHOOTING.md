# Troubleshooting Guide

## Common Issues

### "No log entries found"

**Cause:** The log file is empty, the pattern doesn't match, or the file path is incorrect.

**Fix:**
- Verify the file exists and has content: `wc -l yourfile.log`
- Try a different pattern: `--pattern syslog` or `--pattern apache`
- Test with a custom regex: `--pattern "custom_regex_here"`

### High memory usage with large files

**Cause:** Loading entire file into memory.

**Fix:** Use streaming mode instead:
```python
from src.streaming import LogStream
stream = LogStream("large.log")
stream.stream(lambda entry: None)
```

### Corrupted gzip file error

**Cause:** The `.gz` file is incomplete or corrupted.

**Fix:**
- Verify integrity: `gzip -t file.log.gz`
- Re-download or restore from backup

### Timestamp parsing returns current time

**Cause:** The log timestamp format doesn't match any built-in patterns.

**Fix:** Provide a custom pattern with a named `timestamp` group:
```bash
python -m src.cli app.log --pattern '(?P<timestamp>\d{4}\d{2}\d{2} \d{2}:\d{2}:\d{2}) (?P<message>.*)'
```

### Webhook notifications not sending

**Cause:** Invalid URL, network issues, or timeout.

**Fix:**
- Check URL is reachable: `curl -I https://your-webhook-url`
- Increase timeout in config
- Check firewall rules

### Permission denied on log files

**Cause:** The analyzer doesn't have read access to log files.

**Fix:**
```bash
sudo usermod -aG adm $USER  # Add user to log group
# Or run with appropriate permissions
```

## Debug Mode

Enable verbose output for debugging:
```bash
python -m src.cli app.log --verbose --summary
```
