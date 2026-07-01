"""Web dashboard server for real-time log monitoring."""

import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional
from pathlib import Path

from .aggregator import LogAggregator
from .models import LogEntry, LogLevel


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
        else:
            self.send_error(404)

    def _serve_dashboard(self):
        html = """<!DOCTYPE html>
<html>
<head><title>modular-log-analysis-toolkit Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; }
h1 { color: #569cd6; }
.stats { display: flex; gap: 20px; margin: 20px 0; }
.stat { background: #2d2d2d; padding: 15px; border-radius: 8px; }
.stat h3 { color: #4ec9b0; margin: 0; }
.stat p { font-size: 24px; margin: 5px 0; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #333; }
th { background: #2d2d2d; }
.error { color: #f44747; } .warn { color: #cca700; } .info { color: #4fc1ff; }
</style></head>
<body>
<h1>modular-log-analysis-toolkit Dashboard</h1>
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

    def log_message(self, format, *args):
        pass  # Suppress request logs


def start_dashboard(host: str = "0.0.0.0", port: int = 8080, entries: List[LogEntry] = None):
    """Start the dashboard web server."""
    DashboardHandler.entries = entries or []
    server = HTTPServer((host, port), DashboardHandler)
    print(f"Dashboard running at http://{host}:{port}")
    server.serve_forever()
