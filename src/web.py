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
    """Read and convert markdown to HTML."""
    import re
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove YAML frontmatter
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

        # Store code blocks to prevent processing inside them
        code_blocks = []
        def save_code_block(match):
            lang = match.group(1) or ''
            code = match.group(2)
            # Escape HTML in code
            code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            placeholder = f"CODE_BLOCK_{len(code_blocks)}"
            code_blocks.append(f'<pre><code class="language-{lang}">{code}</code></pre>')
            return placeholder

        content = re.sub(r'```(\w*)\n(.*?)```', save_code_block, content, flags=re.DOTALL)

        # Store inline code
        inline_codes = []
        def save_inline_code(match):
            code = match.group(1)
            code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            placeholder = f"INLINE_CODE_{len(inline_codes)}"
            inline_codes.append(f'<code>{code}</code>')
            return placeholder

        content = re.sub(r'`([^`]+)`', save_inline_code, content)

        # Process line by line
        lines = content.split('\n')
        html_lines = []
        in_list = False
        in_table = False
        table_rows = []

        for line in lines:
            # Check for code block placeholder
            if line.strip().startswith('CODE_BLOCK_'):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                if in_table:
                    html_lines.append(build_table(table_rows))
                    table_rows = []
                    in_table = False
                html_lines.append(line.strip())
                continue

            # Headers
            if line.startswith('#### '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h4>{line[5:]}</h4>')
            elif line.startswith('### '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('## '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('# '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h1>{line[2:]}</h1>')
            # Horizontal rule
            elif line.strip() in ('---', '***', '___'):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append('<hr>')
            # Table rows
            elif '|' in line and line.strip().startswith('|'):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                # Skip separator rows
                if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                    continue
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(cells)
            # List items
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                if in_table:
                    html_lines.append(build_table(table_rows))
                    table_rows = []
                    in_table = False
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                item = line.strip()[2:]
                html_lines.append(f'<li>{item}</li>')
            # Numbered list
            elif re.match(r'^\d+\.\s', line.strip()):
                if in_table:
                    html_lines.append(build_table(table_rows))
                    table_rows = []
                    in_table = False
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True
                item = re.sub(r'^\d+\.\s', '', line.strip())
                html_lines.append(f'<li>{item}</li>')
            # Empty line
            elif line.strip() == '':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                if in_table:
                    html_lines.append(build_table(table_rows))
                    table_rows = []
                    in_table = False
                html_lines.append('')
            # Regular paragraph
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                if in_table:
                    html_lines.append(build_table(table_rows))
                    table_rows = []
                    in_table = False
                html_lines.append(f'<p>{line}</p>')

        # Close any open tags
        if in_list:
            html_lines.append('</ul>')
        if in_table:
            html_lines.append(build_table(table_rows))

        html = '\n'.join(html_lines)

        # Process inline formatting
        # Bold
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        # Italic
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        # Links - handle relative docs links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="/docs/{m.group(2)}">{m.group(1)}</a>' if not m.group(2).startswith('http') else f'<a href="{m.group(2)}" target="_blank">{m.group(1)}</a>', html)

        # Restore code blocks
        for i, block in enumerate(code_blocks):
            html = html.replace(f'CODE_BLOCK_{i}', block)

        # Restore inline code
        for i, code in enumerate(inline_codes):
            html = html.replace(f'INLINE_CODE_{i}', code)

        return html
    except Exception as e:
        return f'<p style="color: red;">Error reading file: {e}</p>'


def build_table(rows):
    """Build HTML table from rows."""
    if not rows:
        return ''
    html = '<table>'
    # First row is header
    html += '<thead><tr>'
    for cell in rows[0]:
        html += f'<th>{cell}</th>'
    html += '</tr></thead>'
    # Rest are body
    if len(rows) > 1:
        html += '<tbody>'
        for row in rows[1:]:
            html += '<tr>'
            for cell in row:
                html += f'<td>{cell}</td>'
            html += '</tr>'
        html += '</tbody>'
    html += '</table>'
    return html


def get_theme_toggle():
    """Return theme toggle button HTML."""
    return '''
    <div class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Theme">
        <svg id="sun-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
        <svg id="moon-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none;">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
    </div>
    '''


def get_theme_css():
    """Return CSS with both light and dark themes."""
    return '''
    :root {
        --bg-primary: #F4F3EE;
        --bg-secondary: #EBE9E3;
        --bg-tertiary: #E2DFD7;
        --text-primary: #2D2926;
        --text-secondary: #5C5650;
        --text-muted: #B1ADA1;
        --accent-primary: #C15F3C;
        --accent-secondary: #D4764E;
        --accent-green: #5A7A5A;
        --border-color: #B1ADA1;
        --hover-bg: #E8E5DD;
        --code-bg: #EBE9E3;
        --code-text: #C15F3C;
        --pre-bg: #EBE9E3;
        --shadow: 0 2px 8px rgba(0,0,0,0.08);
        --card-shadow: 0 4px 12px rgba(0,0,0,0.08);
        --active-bg: #C15F3C;
        --active-text: #F4F3EE;
    }

    [data-theme="dark"] {
        --bg-primary: #1E1E1E;
        --bg-secondary: #252525;
        --bg-tertiary: #2D2D2D;
        --text-primary: #E0DCD5;
        --text-secondary: #B1ADA1;
        --text-muted: #7A7668;
        --accent-primary: #C15F3C;
        --accent-secondary: #D4764E;
        --accent-green: #7FAF7F;
        --border-color: #3A3A3A;
        --hover-bg: #2D2D2D;
        --code-bg: #252525;
        --code-text: #D4764E;
        --pre-bg: #252525;
        --shadow: 0 2px 8px rgba(0,0,0,0.3);
        --card-shadow: 0 4px 12px rgba(0,0,0,0.3);
        --active-bg: #C15F3C;
        --active-text: #F4F3EE;
    }

    .theme-toggle {
        position: fixed;
        top: 16px;
        right: 16px;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--bg-secondary);
        border: 2px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 1000;
        transition: all 0.3s ease;
        color: var(--accent-primary);
    }

    .theme-toggle:hover {
        background: var(--accent-primary);
        color: var(--active-text);
        transform: rotate(30deg);
        box-shadow: var(--card-shadow);
    }
    '''


def get_theme_js():
    """Return JavaScript for theme toggling."""
    return '''
    function toggleTheme() {
        const body = document.body;
        const isDark = body.getAttribute('data-theme') === 'dark';
        body.setAttribute('data-theme', isDark ? 'light' : 'dark');
        localStorage.setItem('theme', isDark ? 'light' : 'dark');
        updateIcons(!isDark);
    }

    function updateIcons(isDark) {
        const sun = document.getElementById('sun-icon');
        const moon = document.getElementById('moon-icon');
        if (sun && moon) {
            sun.style.display = isDark ? 'none' : 'block';
            moon.style.display = isDark ? 'block' : 'none';
        }
    }

    // Load saved theme
    (function() {
        const saved = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', saved);
        updateIcons(saved === 'dark');
    })();
    '''


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
        html = f"""<!DOCTYPE html>
<html>
<head><title>modular-log-analysis-toolkit Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
{get_theme_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', monospace; background: var(--bg-primary); color: var(--text-primary); padding: 24px; line-height: 1.5; }}
h1 {{ color: var(--accent-primary); margin-bottom: 16px; font-size: 1.8rem; }}
h2 {{ color: var(--accent-secondary); margin: 20px 0 12px; font-size: 1.2rem; }}
.stats {{ display: flex; gap: 16px; margin: 20px 0; flex-wrap: wrap; }}
.stat {{ background: var(--bg-secondary); padding: 16px 20px; border-radius: 10px; min-width: 140px; border: 1px solid var(--border-color); }}
.stat h3 {{ color: var(--accent-green); margin: 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }}
.stat p {{ font-size: 28px; margin: 6px 0 0; font-weight: bold; color: var(--text-primary); }}
table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border-color); }}
th {{ background: var(--bg-secondary); color: var(--accent-primary); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; }}
tr:hover {{ background: var(--hover-bg); }}
.error {{ color: #ef5350; font-weight: bold; }} .warn {{ color: #ffa726; }} .info {{ color: #42a5f5; }} .critical {{ color: #ff1744; font-weight: bold; }}
.nav {{ display: flex; gap: 12px; margin-bottom: 20px; }}
.nav a, .nav button {{ background: var(--bg-secondary); color: var(--accent-primary); padding: 10px 20px; border: 1px solid var(--border-color); border-radius: 8px; text-decoration: none; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }}
.nav a:hover, .nav button:hover {{ background: var(--bg-tertiary); color: var(--accent-primary); }}
.nav .active {{ background: var(--active-bg); color: var(--active-text); border-color: var(--active-bg); }}
</style></head>
<body>
{get_theme_toggle()}
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
{get_theme_js()}
async function refresh() {{
  const r = await fetch('/api/stats'); const d = await r.json();
  document.getElementById('total').textContent = d.total;
  document.getElementById('errors').textContent = d.errors;
  document.getElementById('rate').textContent = d.error_rate + '%';
  const er = await fetch('/api/entries'); const ed = await er.json();
  const tb = document.getElementById('entries'); tb.innerHTML = '';
  ed.forEach(e => {{
    const tr = document.createElement('tr');
    tr.innerHTML = '<td>'+e.timestamp+'</td><td class="'+e.level.toLowerCase()+'">'+e.level+'</td><td>'+(e.source||'')+'</td><td>'+e.message+'</td>';
    tb.appendChild(tr);
  }});
}}
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
        html = f"""<!DOCTYPE html>
<html>
<head><title>Documentation - modular-log-analysis-toolkit</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
{get_theme_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', monospace; background: var(--bg-primary); color: var(--text-primary); display: flex; height: 100vh; }}
.sidebar {{ width: 280px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); overflow-y: auto; padding: 16px; flex-shrink: 0; }}
.sidebar h2 {{ color: var(--accent-primary); font-size: 1.2rem; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--accent-primary); }}
.sidebar h3 {{ color: var(--accent-green); font-size: 0.9rem; margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 1px; }}
.sidebar a {{ display: block; padding: 8px 12px; color: var(--text-primary); text-decoration: none; border-radius: 6px; margin: 2px 0; font-size: 0.9rem; transition: all 0.2s; }}
.sidebar a:hover {{ background: var(--bg-tertiary); color: var(--accent-primary); }}
.sidebar a.active {{ background: var(--active-bg); color: var(--active-text); }}
.nav-top {{ margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }}
.nav-top a {{ display: inline-block; padding: 6px 12px; background: var(--bg-tertiary); color: var(--accent-primary); border-radius: 6px; text-decoration: none; font-size: 0.85rem; margin-right: 8px; }}
.nav-top a:hover {{ background: var(--active-bg); color: var(--active-text); }}
.content {{ flex: 1; overflow-y: auto; padding: 32px; background: var(--bg-primary); position: relative; }}
.content h1 {{ color: var(--accent-primary); margin-bottom: 24px; font-size: 1.8rem; border-bottom: 2px solid var(--border-color); padding-bottom: 12px; }}
.welcome {{ text-align: center; padding: 60px 20px; }}
.welcome h1 {{ border: none; }}
.welcome p {{ color: var(--text-secondary); font-size: 1.1rem; margin-top: 16px; }}
.welcome .hint {{ color: var(--text-muted); margin-top: 24px; font-size: 0.9rem; }}
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
{get_theme_toggle()}
<div class="welcome">
<h1>modular-log-analysis-toolkit</h1>
<p>Welcome to the documentation. Select a topic from the sidebar to start reading.</p>
<p class="hint">Click any link on the left to view the documentation</p>
</div>
</div>
<script>{get_theme_js()}</script>
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
{get_theme_css()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', monospace; background: var(--bg-primary); color: var(--text-primary); display: flex; height: 100vh; }}
.sidebar {{ width: 280px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); overflow-y: auto; padding: 16px; flex-shrink: 0; }}
.sidebar h2 {{ color: var(--accent-primary); font-size: 1.2rem; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--accent-primary); }}
.sidebar h3 {{ color: var(--accent-green); font-size: 0.9rem; margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 1px; }}
.sidebar a {{ display: block; padding: 8px 12px; color: var(--text-primary); text-decoration: none; border-radius: 6px; margin: 2px 0; font-size: 0.9rem; transition: all 0.2s; }}
.sidebar a:hover {{ background: var(--bg-tertiary); color: var(--accent-primary); }}
.sidebar a.active {{ background: var(--active-bg); color: var(--active-text); }}
.nav-top {{ margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }}
.nav-top a {{ display: inline-block; padding: 6px 12px; background: var(--bg-tertiary); color: var(--accent-primary); border-radius: 6px; text-decoration: none; font-size: 0.85rem; margin-right: 8px; }}
.nav-top a:hover {{ background: var(--active-bg); color: var(--active-text); }}
.content {{ flex: 1; overflow-y: auto; padding: 32px 48px; background: var(--bg-primary); position: relative; }}
.content h1 {{ color: var(--accent-primary); margin-bottom: 20px; font-size: 1.8rem; border-bottom: 2px solid var(--border-color); padding-bottom: 12px; }}
.content h2 {{ color: var(--accent-secondary); margin: 28px 0 12px; font-size: 1.4rem; }}
.content h3 {{ color: var(--accent-green); margin: 20px 0 8px; font-size: 1.15rem; }}
.content h4 {{ color: var(--accent-primary); margin: 16px 0 8px; font-size: 1rem; }}
.content p {{ margin: 10px 0; line-height: 1.7; }}
.content code {{ background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-size: 0.9rem; color: var(--code-text); }}
.content pre {{ background: var(--pre-bg); padding: 16px; border-radius: 8px; overflow-x: auto; margin: 16px 0; border: 1px solid var(--border-color); }}
.content pre code {{ background: none; padding: 0; color: var(--text-primary); }}
.content a {{ color: var(--accent-primary); text-decoration: none; }}
.content a:hover {{ text-decoration: underline; }}
.content ul, .content ol {{ margin: 10px 0 10px 24px; }}
.content li {{ margin: 6px 0; line-height: 1.6; }}
.content strong {{ color: var(--accent-primary); }}
.content em {{ color: var(--text-secondary); }}
.content table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
.content th, .content td {{ border: 1px solid var(--border-color); padding: 10px 14px; text-align: left; }}
.content th {{ background: var(--bg-tertiary); color: var(--accent-primary); font-weight: 600; }}
.content tr:hover {{ background: var(--hover-bg); }}
.content blockquote {{ border-left: 4px solid var(--accent-primary); padding: 12px 16px; margin: 16px 0; background: var(--bg-secondary); border-radius: 0 8px 8px 0; font-style: italic; }}
.content hr {{ border: none; border-top: 2px solid var(--border-color); margin: 24px 0; }}
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
{get_theme_toggle()}
{content}
</div>
<script>{get_theme_js()}</script>
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
