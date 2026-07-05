"""Webhook notification system for log alerts."""

import json
import urllib.request
import urllib.error
from typing import Dict, Optional, Any
from datetime import datetime

from .models import LogEntry, LogLevel


class WebhookSender:
    """Send webhook notifications for log events."""

    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")
        if not url.startswith(("http://", "https://")):
            raise ValueError("Webhook URL must start with http:// or https://")
        if not isinstance(timeout, (int, float)):
            raise TypeError("Timeout must be a number")
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = max(1, min(int(timeout), 120))
        self._sent_count = 0
        self._error_count = 0

    def __repr__(self) -> str:
        return f"WebhookSender(url={self.url!r}, sent={self._sent_count})"

    def send_alert(self, entry: LogEntry, extra: Optional[Dict[str, Any]] = None) -> bool:
        """Send a webhook alert for a log entry."""
        payload = {
            "timestamp": entry.timestamp.isoformat(),
            "level": entry.level.value,
            "message": entry.message,
            "source": entry.source,
            "line_number": entry.line_number,
        }
        if extra:
            payload.update(extra)

        return self._post(payload)

    def send_summary(self, level_counts: Dict[str, int], error_rate: float) -> bool:
        """Send a summary webhook."""
        payload = {
            "type": "summary",
            "timestamp": datetime.now().isoformat(),
            "level_counts": level_counts,
            "error_rate": error_rate,
        }
        return self._post(payload)

    def _post(self, payload: Dict) -> bool:
        """POST JSON payload to webhook URL."""
        try:
            data = json.dumps(payload, default=str).encode("utf-8")
        except (TypeError, ValueError):
            self._error_count += 1
            return False

        req = urllib.request.Request(self.url, data=data, headers=self.headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                self._sent_count += 1
                return resp.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            self._error_count += 1
            return False

    @property
    def stats(self) -> Dict[str, int]:
        """Get webhook send statistics."""
        return {"sent": self._sent_count, "errors": self._error_count}

    def reset_stats(self):
        """Reset send statistics."""
        self._sent_count = 0
        self._error_count = 0

    def reset(self):
        """Reset all sender state including stats."""
        self.reset_stats()
        self.headers = {"Content-Type": "application/json"}


class WebhookRouter:
    """Route webhooks to multiple endpoints."""

    def __init__(self):
        self._senders: Dict[str, WebhookSender] = {}

    def add_endpoint(self, name: str, url: str, **kwargs) -> None:
        """Register a webhook endpoint."""
        if not name or not isinstance(name, str):
            raise ValueError("Endpoint name must be a non-empty string")
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")
        self._senders[name] = WebhookSender(url, **kwargs)

    def remove_endpoint(self, name: str) -> None:
        """Remove a webhook endpoint."""
        self._senders.pop(name, None)

    def send_to_all(self, entry: LogEntry) -> Dict[str, bool]:
        """Send alert to all registered endpoints."""
        results = {}
        for name, sender in self._senders.items():
            results[name] = sender.send_alert(entry)
        return results

    def send_to(self, name: str, entry: LogEntry) -> bool:
        """Send alert to a specific endpoint."""
        if name in self._senders:
            return self._senders[name].send_alert(entry)
        return False

    def list_endpoints(self) -> list:
        """List registered endpoints."""
        return list(self._senders.keys())

    @property
    def endpoint_count(self) -> int:
        """Get number of registered endpoints."""
        return len(self._senders)
