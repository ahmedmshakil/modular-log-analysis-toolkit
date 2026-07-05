"""Web dashboard server for real-time log monitoring."""

import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional
from pathlib import Path

from .aggregator import LogAggregator
from .models import LogEntry, LogLevel


def get_docs_structure():
    """Get documentation file structure."""
    docs_dir = Path(__file__).parent.parent / "docs"
    if not docs_dir.exists():
        return []

    structure = []
    for f in sorted(docs_dir.glob("*.md")):
        structure.append({"name": f.stem.replace("-", " ").title(), "path": f.name, "type": "file"})

    modules_dir = docs_dir / "modules"
    if modules_dir.exists():
        modules = []
        for f in sorted(modules_dir.glob("*.md")):
            modules.append({"name": f.stem.replace("-", " ").title(), "path": f"modules/{f.name}", "type": "module"})
        if modules:
            structure.append({"name": "Modules", "type": "section", "children": modules})

    return structure


def read_markdown(file_path):
    """Read and convert markdown to simple HTML."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple markdown to HTML conversion
        html = content
        # Headers
        html = html.replace("# ", "<h1>").replace("\n<h1>", "\n</h1>\n<h1>")
        html = html.replace("## ", "<h2>").replace("\n<h2>", "\n</h2>\n<h2>")
        html = html.replace("### ", "<h3>").replace("\n<h3>", "\n</h3>\n<h3>")
        # Bold
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        # Italic
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        # Code blocks
        html = re.sub(r'```(\w*)\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="/docs/\2">\1</a>', html)
        # Lists
        html = re.sub(r'^- (.*)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f"<p>{html}</p>"

        return html
    except Exception as e:
        return f"<p>Error reading file: {e}</p>"


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for the log dashboard."""

    entries: List[LogEntry] = []

    def do_GET(self):
        if self.path == "/":
            self._serve_dashboard()
        elif self.path == "/api/stats":
            self._serve_stats()
        elif self.path == "/api/entries":
            self._serve_entries()
        elif self.path == "/api/errors":
            self._serve_errors()
        elif self.path == "/docs":
            self._serve_docs_index()
        elif self.path.startswith("/docs/") and self.path.endswith(".md"):
            self._serve_docs_file(self.path[6:])
        else:
            self.send_error(404)

    def _serve_dashboard(self):
        html = """<!DOCTYPE html>
<html>
<head><title>modular-log-analysis-toolkit Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', monospace; background: #ffffff; color: #333333; padding: 24px; line-height: 1.5; }
h1 { color: #1565c0; margin-bottom: 16px; font-size: 1.8rem; }
h2 { color: #1976d2; margin: 20px 0 12px; font-size: 1.2rem; }
.stats { display: flex; gap: 16px; margin: 20px 0; flex-wrap: wrap; }
.stat { background: #f5f5f5; padding: 16px 20px; border-radius: 10px; min-width: 140px; border: 1px solid #e0e0e0; }
.stat h3 { color: #2e7d32; margin: 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
.stat p { font-size: 28px; margin: 6px 0 0; font-weight: bold; color: #212121; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; }
th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #e0e0e0; }
th { background: #f5f5f5; color: #1565c0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
tr:hover { background: #f0f7ff; }
.error { color: #ef5350; font-weight: bold; } .warn { color: #ffa726; } .info { color: #42a5f5; } .critical { color: #ff1744; font-weight: bold; }
.nav { display: flex; gap: 12px; margin-bottom: 20px; }
.nav a, .nav button { background: #f5f5f5; color: #1565c0; padding: 10px 20px; border: 1px solid #e0e0e0; border-radius: 8px; text-decoration: none; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }
.nav a:hover, .nav button:hover { background: #e3f2fd; color: #0d47a1; }
.nav .active { background: #e3f2fd; color: #1565c0; border-color: #1565c0; }
</style></head>
<body>
<h1>modular-log-analysis-toolkit Dashboard</h1>
<div class="nav">
<a href="/" class="active">Dashboard</a>
<a href="/docs">Documentation</a>
</div>
<div class="stats">
<div class="stat"><h3>Total</h3><p id="total">-</p></div>
<div class="stat"><h3>Errors</h3><p id="errors">-</p></div>
<div class="stat"><h3>Error Rate</h3><p id="rate">-</p></div>
</div>
<h2>Recent Entries</h2>
<table><thead><tr><th>Time</th><th>Level</th><th>Source</th><th>Message</th></tr></thead>
<tbody id="entries"></tbody></table>
<script>
async function refresh() {
  const r = await fetch('/api/stats'); const d = await r.json();
  document.getElementById('total').textContent = d.total;
  document.getElementById('errors').textContent = d.errors;
  document.getElementById('rate').textContent = d.error_rate + '%';
  const er = await fetch('/api/entries'); const ed = await er.json();
  const tb = document.getElementById('entries'); tb.innerHTML = '';
  ed.forEach(e => {
    const tr = document.createElement('tr');
    tr.innerHTML = '<td>'+e.timestamp+'</td><td class="'+e.level.toLowerCase()+'">'+e.level+'</td><td>'+(e.source||'')+'</td><td>'+e.message+'</td>';
    tb.appendChild(tr);
  });
}
refresh(); setInterval(refresh, 5000);
</script></body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_stats(self):
        agg = LogAggregator(self.entries)
        result = agg.summary()
        data = {
            "total": result.total_entries,
            "errors": result.level_counts.get("ERROR", 0) + result.level_counts.get("CRITICAL", 0),
            "error_rate": round(agg.error_rate(), 2),
            "level_counts": result.level_counts,
        }
        self._json_response(data)

    def _serve_entries(self):
        limit = min(100, len(self.entries))
        data = [e.to_dict() for e in self.entries[-limit:]]
        self._json_response(data)

    def _serve_errors(self):
        errors = [e.to_dict() for e in self.entries if e.level in (LogLevel.ERROR, LogLevel.CRITICAL)]
        self._json_response(errors[-50:])

    def _json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def _serve_docs_index(self):
        """Serve documentation index page with sidebar."""
        html = """<!DOCTYPE html>
<html>
<head><title>Documentation - modular-log-analysis-toolkit</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', monospace; background: #ffffff; color: #333333; display: flex; height: 100vh; }
.sidebar { width: 280px; background: #f5f5f5; border-right: 1px solid #e0e0e0; overflow-y: auto; padding: 16px; flex-shrink: 0; }
.sidebar h2 { color: #1565c0; font-size: 1.2rem; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #1565c0; }
.sidebar h3 { color: #2e7d32; font-size: 0.9rem; margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 1px; }
.sidebar a { display: block; padding: 8px 12px; color: #333333; text-decoration: none; border-radius: 6px; margin: 2px 0; font-size: 0.9rem; transition: all 0.2s; }
.sidebar a:hover { background: #e3f2fd; color: #1565c0; }
.sidebar a.active { background: #1565c0; color: #ffffff; }
.nav-top { margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #e0e0e0; }
.nav-top a { display: inline-block; padding: 6px 12px; background: #e3f2fd; color: #1565c0; border-radius: 6px; text-decoration: none; font-size: 0.85rem; margin-right: 8px; }
.nav-top a:hover { background: #1565c0; color: #ffffff; }
.content { flex: 1; overflow-y: auto; padding: 32px; background: #ffffff; }
.content h1 { color: #1565c0; margin-bottom: 24px; font-size: 1.8rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 12px; }
.welcome { text-align: center; padding: 60px 20px; }
.welcome h1 { border: none; }
.welcome p { color: #616161; font-size: 1.1rem; margin-top: 16px; }
.welcome .hint { color: #9e9e9e; margin-top: 24px; font-size: 0.9rem; }
</style></head>
<body>
<div class="sidebar">
<div class="nav-top">
<a href="/">Dashboard</a>
</div>
<h2>Documentation</h2>
<h3>Getting Started</h3>
<a href="/docs/README.md">Documentation Index</a>
<a href="/docs/installation.md">Installation Guide</a>
<a href="/docs/quickstart.md">Quick Start</a>
<a href="/docs/cli-usage.md">CLI Usage</a>
<a href="/docs/python-api.md">Python API</a>
<h3>Modules</h3>
<a href="/docs/modules/models.md">Models</a>
<a href="/docs/modules/parser.md">Parser</a>
<a href="/docs/modules/filter.md">Filter</a>
<a href="/docs/modules/aggregator.md">Aggregator</a>
<a href="/docs/modules/search.md">Search</a>
<a href="/docs/modules/exporter.md">Exporter</a>
<a href="/docs/modules/dedup.md">Deduplication</a>
<a href="/docs/modules/streaming.md">Streaming</a>
<a href="/docs/modules/alerts.md">Alerts</a>
<a href="/docs/modules/webhooks.md">Webhooks</a>
<a href="/docs/modules/tags.md">Tags</a>
<a href="/docs/modules/plugins.md">Plugins</a>
<a href="/docs/modules/retention.md">Retention</a>
<a href="/docs/modules/geolocation.md">Geolocation</a>
<a href="/docs/modules/auth.md">Authentication</a>
<a href="/docs/modules/cache.md">Cache</a>
</div>
<div class="content">
<div class="welcome">
<h1>modular-log-analysis-toolkit</h1>
<p>Welcome to the documentation. Select a topic from the sidebar to start reading.</p>
<p class="hint">Click any link on the left to view the documentation</p>
</div>
</div>
</body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_docs_file(self, filename):
        """Serve a documentation file with sidebar."""
        docs_dir = Path(__file__).parent.parent / "docs"
        file_path = docs_dir / filename

        if not file_path.exists():
            self.send_error(404)
            return

        content = read_markdown(file_path)

        # Highlight current file in sidebar
        def make_active(current, check):
            return ' class="active"' if current == check else ''

        html = f"""<!DOCTYPE html>
<html>
<head><title>{filename} - Documentation</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', monospace; background: #ffffff; color: #333333; display: flex; height: 100vh; }}
.sidebar {{ width: 280px; background: #f5f5f5; border-right: 1px solid #e0e0e0; overflow-y: auto; padding: 16px; flex-shrink: 0; }}
.sidebar h2 {{ color: #1565c0; font-size: 1.2rem; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #1565c0; }}
.sidebar h3 {{ color: #2e7d32; font-size: 0.9rem; margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 1px; }}
.sidebar a {{ display: block; padding: 8px 12px; color: #333333; text-decoration: none; border-radius: 6px; margin: 2px 0; font-size: 0.9rem; transition: all 0.2s; }}
.sidebar a:hover {{ background: #e3f2fd; color: #1565c0; }}
.sidebar a.active {{ background: #1565c0; color: #ffffff; }}
.nav-top {{ margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #e0e0e0; }}
.nav-top a {{ display: inline-block; padding: 6px 12px; background: #e3f2fd; color: #1565c0; border-radius: 6px; text-decoration: none; font-size: 0.85rem; margin-right: 8px; }}
.nav-top a:hover {{ background: #1565c0; color: #ffffff; }}
.content {{ flex: 1; overflow-y: auto; padding: 32px 48px; background: #ffffff; }}
.content h1 {{ color: #1565c0; margin-bottom: 20px; font-size: 1.8rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 12px; }}
.content h2 {{ color: #1976d2; margin: 28px 0 12px; font-size: 1.4rem; }}
.content h3 {{ color: #2e7d32; margin: 20px 0 8px; font-size: 1.15rem; }}
.content h4 {{ color: #1565c0; margin: 16px 0 8px; font-size: 1rem; }}
.content p {{ margin: 10px 0; line-height: 1.7; }}
.content code {{ background: #e8f5e9; padding: 2px 6px; border-radius: 4px; font-size: 0.9rem; color: #2e7d32; }}
.content pre {{ background: #f5f5f5; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 16px 0; border: 1px solid #e0e0e0; }}
.content pre code {{ background: none; padding: 0; color: #333333; }}
.content a {{ color: #1565c0; text-decoration: none; }}
.content a:hover {{ color: #0d47a1; text-decoration: underline; }}
.content ul, .content ol {{ margin: 10px 0 10px 24px; }}
.content li {{ margin: 6px 0; line-height: 1.6; }}
.content strong {{ color: #1565c0; }}
.content em {{ color: #616161; }}
.content table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
.content th, .content td {{ border: 1px solid #e0e0e0; padding: 10px 14px; text-align: left; }}
.content th {{ background: #e3f2fd; color: #1565c0; font-weight: 600; }}
.content tr:hover {{ background: #f0f7ff; }}
.content blockquote {{ border-left: 4px solid #1565c0; padding: 12px 16px; margin: 16px 0; background: #f5f5f5; border-radius: 0 8px 8px 0; }}
.content hr {{ border: none; border-top: 2px solid #e0e0e0; margin: 24px 0; }}
.error {{ color: #ef5350; font-weight: bold; }}
.warn {{ color: #ffa726; }}
.info {{ color: #42a5f5; }}
.critical {{ color: #ff1744; font-weight: bold; }}
</style></head>
<body>
<div class="sidebar">
<div class="nav-top">
<a href="/">Dashboard</a>
</div>
<h2>Documentation</h2>
<h3>Getting Started</h3>
<a href="/docs/README.md"{make_active(filename, 'README.md')}>Documentation Index</a>
<a href="/docs/installation.md"{make_active(filename, 'installation.md')}>Installation Guide</a>
<a href="/docs/quickstart.md"{make_active(filename, 'quickstart.md')}>Quick Start</a>
<a href="/docs/cli-usage.md"{make_active(filename, 'cli-usage.md')}>CLI Usage</a>
<a href="/docs/python-api.md"{make_active(filename, 'python-api.md')}>Python API</a>
<h3>Modules</h3>
<a href="/docs/modules/models.md"{make_active(filename, 'modules/models.md')}>Models</a>
<a href="/docs/modules/parser.md"{make_active(filename, 'modules/parser.md')}>Parser</a>
<a href="/docs/modules/filter.md"{make_active(filename, 'modules/filter.md')}>Filter</a>
<a href="/docs/modules/aggregator.md"{make_active(filename, 'modules/aggregator.md')}>Aggregator</a>
<a href="/docs/modules/search.md"{make_active(filename, 'modules/search.md')}>Search</a>
<a href="/docs/modules/exporter.md"{make_active(filename, 'modules/exporter.md')}>Exporter</a>
<a href="/docs/modules/dedup.md"{make_active(filename, 'modules/dedup.md')}>Deduplication</a>
<a href="/docs/modules/streaming.md"{make_active(filename, 'modules/streaming.md')}>Streaming</a>
<a href="/docs/modules/alerts.md"{make_active(filename, 'modules/alerts.md')}>Alerts</a>
<a href="/docs/modules/webhooks.md"{make_active(filename, 'modules/webhooks.md')}>Webhooks</a>
<a href="/docs/modules/tags.md"{make_active(filename, 'modules/tags.md')}>Tags</a>
<a href="/docs/modules/plugins.md"{make_active(filename, 'modules/plugins.md')}>Plugins</a>
<a href="/docs/modules/retention.md"{make_active(filename, 'modules/retention.md')}>Retention</a>
<a href="/docs/modules/geolocation.md"{make_active(filename, 'modules/geolocation.md')}>Geolocation</a>
<a href="/docs/modules/auth.md"{make_active(filename, 'modules/auth.md')}>Authentication</a>
<a href="/docs/modules/cache.md"{make_active(filename, 'modules/cache.md')}>Cache</a>
</div>
<div class="content">
{content}
</div>
</body></html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass  # Suppress request logs


def start_dashboard(host: str = "0.0.0.0", port: int = 8080, entries: List[LogEntry] = None):
    """Start the dashboard web server."""
    DashboardHandler.entries = entries or []
    server = HTTPServer((host, port), DashboardHandler)
    print(f"Dashboard running at http://{host}:{port}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        server.shutdown()


if __name__ == "__main__":
    from .parser import LogParser
    from .reader import read_log_lines
    import sys

    # Default test data if no file provided
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        # Create sample log file
        sample = """2024-01-15 10:30:45 [ERROR] Database connection timeout
2024-01-15 10:31:00 [INFO] Application started successfully
2024-01-15 10:31:15 [WARN] High memory usage detected: 85%
2024-01-15 10:31:30 [ERROR] Failed to process request
2024-01-15 10:31:45 [INFO] User login: admin@example.com
2024-01-15 10:32:00 [CRITICAL] System out of memory
2024-01-15 10:32:15 [INFO] Cleanup initiated
2024-01-15 10:32:30 [INFO] System recovered"""
        log_file = "sample.log"
        with open(log_file, "w") as f:
            f.write(sample)
        print(f"Created sample log file: {log_file}")

    parser = LogParser()
    entries = parser.parse_lines(list(read_log_lines(log_file)))
    print(f"Loaded {len(entries)} entries from {log_file}")
    start_dashboard(port=8080, entries=entries)
