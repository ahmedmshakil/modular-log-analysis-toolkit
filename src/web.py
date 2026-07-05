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
body { font-family: 'Segoe UI', monospace; background: #1a1a2e; color: #e0e0e0; padding: 24px; line-height: 1.5; }
h1 { color: #64b5f6; margin-bottom: 16px; font-size: 1.8rem; }
h2 { color: #90caf9; margin: 20px 0 12px; font-size: 1.2rem; }
.stats { display: flex; gap: 16px; margin: 20px 0; flex-wrap: wrap; }
.stat { background: #16213e; padding: 16px 20px; border-radius: 10px; min-width: 140px; border: 1px solid #1a3a5c; }
.stat h3 { color: #4ec9b0; margin: 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
.stat p { font-size: 28px; margin: 6px 0 0; font-weight: bold; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; }
th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid #1a3a5c; }
th { background: #16213e; color: #90caf9; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }
tr:hover { background: #1a2744; }
.error { color: #ef5350; font-weight: bold; } .warn { color: #ffa726; } .info { color: #42a5f5; } .critical { color: #ff1744; font-weight: bold; }
.nav { display: flex; gap: 12px; margin-bottom: 20px; }
.nav a, .nav button { background: #16213e; color: #64b5f6; padding: 10px 20px; border: 1px solid #1a3a5c; border-radius: 8px; text-decoration: none; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }
.nav a:hover, .nav button:hover { background: #1a3a5c; color: #90caf9; }
.nav .active { background: #1a3a5c; color: #4ec9b0; border-color: #4ec9b0; }
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
        """Serve documentation index page."""
        docs = get_docs_structure()
        html = """<!DOCTYPE html>
<html>
<head><title>Documentation - modular-log-analysis-toolkit</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', monospace; background: #1a1a2e; color: #e0e0e0; padding: 24px; line-height: 1.6; }
h1 { color: #64b5f6; margin-bottom: 24px; font-size: 1.8rem; }
.nav { display: flex; gap: 12px; margin-bottom: 24px; }
.nav a { background: #16213e; color: #64b5f6; padding: 10px 20px; border: 1px solid #1a3a5c; border-radius: 8px; text-decoration: none; font-size: 0.9rem; transition: all 0.2s; }
.nav a:hover { background: #1a3a5c; color: #90caf9; }
.nav .active { background: #1a3a5c; color: #4ec9b0; border-color: #4ec9b0; }
.docs-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.doc-card { background: #16213e; padding: 20px; border-radius: 10px; border: 1px solid #1a3a5c; transition: all 0.2s; }
.doc-card:hover { border-color: #4ec9b0; transform: translateY(-2px); }
.doc-card a { color: #90caf9; text-decoration: none; font-size: 1.1rem; display: block; }
.doc-card a:hover { color: #4ec9b0; }
.doc-card p { color: #7a8a9a; margin-top: 8px; font-size: 0.85rem; }
.section-title { color: #4ec9b0; margin: 24px 0 12px; font-size: 1.2rem; border-bottom: 1px solid #1a3a5c; padding-bottom: 8px; }
</style></head>
<body>
<h1>Documentation</h1>
<div class="nav">
<a href="/">Dashboard</a>
<a href="/docs" class="active">Documentation</a>
</div>
<h2 class="section-title">Getting Started</h2>
<div class="docs-grid">
<div class="doc-card"><a href="/docs/README.md">Documentation Index</a><p>Main documentation index and overview</p></div>
<div class="doc-card"><a href="/docs/installation.md">Installation Guide</a><p>How to install and setup the toolkit</p></div>
<div class="doc-card"><a href="/docs/quickstart.md">Quick Start</a><p>Get started in 5 minutes</p></div>
<div class="doc-card"><a href="/docs/cli-usage.md">CLI Usage</a><p>Command-line interface guide</p></div>
<div class="doc-card"><a href="/docs/python-api.md">Python API</a><p>Python API reference</p></div>
</div>
<h2 class="section-title">Module Documentation</h2>
<div class="docs-grid">
<div class="doc-card"><a href="/docs/modules/models.md">Models</a><p>LogEntry, LogLevel, AnalysisResult</p></div>
<div class="doc-card"><a href="/docs/modules/parser.md">Parser</a><p>Log parsing engine</p></div>
<div class="doc-card"><a href="/docs/modules/filter.md">Filter</a><p>Filtering and query engine</p></div>
<div class="doc-card"><a href="/docs/modules/aggregator.md">Aggregator</a><p>Statistics and aggregation</p></div>
<div class="doc-card"><a href="/docs/modules/search.md">Search</a><p>Full-text search indexing</p></div>
<div class="doc-card"><a href="/docs/modules/exporter.md">Exporter</a><p>Data export formats</p></div>
<div class="doc-card"><a href="/docs/modules/dedup.md">Deduplication</a><p>Remove duplicate entries</p></div>
<div class="doc-card"><a href="/docs/modules/streaming.md">Streaming</a><p>Large file processing</p></div>
<div class="doc-card"><a href="/docs/modules/alerts.md">Alerts</a><p>Alert system and thresholds</p></div>
<div class="doc-card"><a href="/docs/modules/webhooks.md">Webhooks</a><p>Webhook notifications</p></div>
<div class="doc-card"><a href="/docs/modules/tags.md">Tags</a><p>Tagging and labeling system</p></div>
<div class="doc-card"><a href="/docs/modules/plugins.md">Plugins</a><p>Plugin development</p></div>
<div class="doc-card"><a href="/docs/modules/retention.md">Retention</a><p>Log retention policies</p></div>
<div class="doc-card"><a href="/docs/modules/geolocation.md">Geolocation</a><p>IP geolocation lookup</p></div>
<div class="doc-card"><a href="/docs/modules/auth.md">Authentication</a><p>User auth and authorization</p></div>
<div class="doc-card"><a href="/docs/modules/cache.md">Cache</a><p>Caching system</p></div>
</div>
</body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_docs_file(self, filename):
        """Serve a documentation file."""
        docs_dir = Path(__file__).parent.parent / "docs"
        file_path = docs_dir / filename

        if not file_path.exists():
            self.send_error(404)
            return

        content = read_markdown(file_path)
        html = f"""<!DOCTYPE html>
<html>
<head><title>{filename} - Documentation</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', monospace; background: #1a1a2e; color: #e0e0e0; padding: 24px; line-height: 1.6; }}
.nav {{ display: flex; gap: 12px; margin-bottom: 24px; }}
.nav a {{ background: #16213e; color: #64b5f6; padding: 10px 20px; border: 1px solid #1a3a5c; border-radius: 8px; text-decoration: none; font-size: 0.9rem; transition: all 0.2s; }}
.nav a:hover {{ background: #1a3a5c; color: #90caf9; }}
.content {{ background: #16213e; padding: 24px; border-radius: 10px; border: 1px solid #1a3a5c; }}
h1 {{ color: #64b5f6; margin-bottom: 16px; font-size: 1.8rem; }}
h2 {{ color: #90caf9; margin: 20px 0 12px; font-size: 1.3rem; }}
h3 {{ color: #4ec9b0; margin: 16px 0 8px; font-size: 1.1rem; }}
p {{ margin: 8px 0; }}
code {{ background: #0d1b2a; padding: 2px 6px; border-radius: 4px; font-size: 0.9rem; color: #4ec9b0; }}
pre {{ background: #0d1b2a; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 12px 0; }}
pre code {{ background: none; padding: 0; }}
a {{ color: #64b5f6; text-decoration: none; }}
a:hover {{ color: #4ec9b0; }}
li {{ margin: 4px 0 4px 20px; }}
strong {{ color: #90caf9; }}
</style></head>
<body>
<div class="nav">
<a href="/">Dashboard</a>
<a href="/docs">Documentation</a>
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
    server.serve_forever()
