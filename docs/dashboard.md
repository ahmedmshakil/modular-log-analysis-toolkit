# Web Dashboard

The web dashboard provides real-time log monitoring with a clean, theme-switchable interface.

## Quick Start

```python
from src.web import start_dashboard
from src.parser import LogParser
from src.reader import read_log_lines

parser = LogParser()
entries = parser.parse_lines(list(read_log_lines("app.log")))
start_dashboard(port=8080, entries=entries)
```

## Features

- **Real-time updates** - Auto-refreshes every 5 seconds
- **Dark/Light theme** - Toggle with the theme button
- **Statistics view** - Total entries, error count, error rate
- **Entry table** - Recent log entries with color-coded levels
- **Documentation browser** - Built-in docs viewer

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard HTML page |
| `/api/stats` | GET | JSON statistics |
| `/api/entries` | GET | Recent entries (last 100) |
| `/api/errors` | GET | Error entries (last 50) |
| `/docs` | GET | Documentation index |
| `/docs/*.md` | GET | Documentation files |

## Configuration

### Custom Host and Port

```python
start_dashboard(host="127.0.0.1", port=9090, entries=entries)
```

### Programmatic Access

```python
from src.web import get_dashboard_url

url = get_dashboard_url(port=8080)
print(f"Dashboard at: {url}")
```

## Troubleshooting

### Port already in use

```
OSError: [Errno 98] Address already in use
```

**Fix:** Use a different port or stop the existing process:
```bash
lsof -i :8080
kill <PID>
```

### Dashboard not loading

- Check firewall rules allow the port
- Verify the server is running
- Check browser console for errors
