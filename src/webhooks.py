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
        self._last_error: Optional[str] = None

    def __repr__(self) -> str:
        return f"WebhookSender(url={self.url!r}, sent={self._sent_count})"

    def __str__(self) -> str:
        return f"WebhookSender({self.url}, {self._sent_count} sent, {self._error_count} errors)"

    def send_alert(self, entry: LogEntry, extra: Optional[Dict[str, Any]] = None) -> bool:
        """Send a webhook alert for a log entry.

        Args:
            entry: The log entry to send as an alert.
            extra: Additional data to include in the payload.

        Returns:
            True if the webhook was sent successfully.
        """
        if not entry:
            return False
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

        # Reject payloads larger than 1MB
        if len(data) > 1024 * 1024:
            self._error_count += 1
            return False

        req = urllib.request.Request(self.url, data=data, headers=self.headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                self._sent_count += 1
                return resp.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            self._error_count += 1
            return False
        except Exception:
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

    def __repr__(self) -> str:
        return f"WebhookRouter(endpoints={len(self._senders)})"

    def __len__(self) -> int:
        """Get number of registered endpoints."""
        return len(self._senders)

    def add_endpoint(self, name: str, url: str, **kwargs) -> None:
        """Register a webhook endpoint.

        Args:
            name: Unique name for the endpoint.
            url: Webhook URL.

        Raises:
            ValueError: If name or url is empty, or URL format is invalid.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Endpoint name must be a non-empty string")
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        if name in self._senders:
            raise ValueError(f"Endpoint '{name}' already exists")
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

    @property
    def stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all endpoints.

        Returns:
            Dictionary mapping endpoint names to their stats.
        """
        return {name: sender.stats for name, sender in self._senders.items()}

    def clear(self):
        """Remove all registered endpoints."""
        self._senders.clear()

    def get_endpoint(self, name: str) -> Optional[WebhookSender]:
        """Get a specific endpoint by name.

        Args:
            name: Endpoint name.

        Returns:
            WebhookSender if found, None otherwise.
        """
        return self._senders.get(name)

    def has_endpoint(self, name: str) -> bool:
        """Check if an endpoint exists.

        Args:
            name: Endpoint name to check.

        Returns:
            True if endpoint exists, False otherwise.
        """
        return name in self._senders

    def total_sent(self) -> int:
        """Get total messages sent across all endpoints.

        Returns:
            Total sent count.
        """
        return sum(sender.stats["sent"] for sender in self._senders.values())

    def total_errors(self) -> int:
        """Get total errors across all endpoints.

        Returns:
            Total error count.
        """
        return sum(sender.stats["errors"] for sender in self._senders.values())

    def reset_all_stats(self):
        """Reset statistics for all endpoints."""
        for sender in self._senders.values():
            sender.reset_stats()

    def get_endpoint_stats(self, name: str) -> Optional[Dict[str, int]]:
        """Get statistics for a specific endpoint.

        Args:
            name: Endpoint name.

        Returns:
            Stats dict if found, None otherwise.
        """
        sender = self._senders.get(name)
        return sender.stats if sender else None

    def get_all_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics for all endpoints.

        Returns:
            Dictionary with aggregated stats.
        """
        return {
            "endpoints": self.endpoint_count,
            "total_sent": self.total_sent(),
            "total_errors": self.total_errors(),
            "per_endpoint": self.stats,
        }

    def is_empty(self) -> bool:
        """Check if router has no endpoints.

        Returns:
            True if no endpoints registered.
        """
        return len(self._senders) == 0

    def has_endpoints(self) -> bool:
        """Check if any endpoints are registered.

        Returns:
            True if endpoints exist.
        """
        return len(self._senders) > 0

    def has_sent(self) -> bool:
        """Check if any messages have been sent.

        Returns:
            True if messages sent.
        """
        return self.total_sent() > 0

    def has_errors(self) -> bool:
        """Check if any errors have occurred.

        Returns:
            True if errors exist.
        """
        return self.total_errors() > 0

    def get_endpoint_names(self) -> List[str]:
        """Get list of endpoint names.

        Returns:
            List of endpoint name strings.
        """
        return list(self._senders.keys())

    def get_endpoints_dict(self) -> List[Dict[str, Any]]:
        """Get all endpoints as dictionaries.

        Returns:
            List of endpoint dictionaries.
        """
        return [
            {
                "name": name,
                "url": sender.url,
                "stats": sender.stats,
            }
            for name, sender in self._senders.items()
        ]

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get router statistics as dictionary.

        Returns:
            Dictionary with router stats.
        """
        return {
            "endpoints": self.endpoint_count,
            "total_sent": self.total_sent(),
            "total_errors": self.total_errors(),
        }

    def has_multiple_endpoints(self) -> bool:
        """Check if multiple endpoints are registered.

        Returns:
            True if more than one endpoint exists.
        """
        return len(self._senders) > 1

    def get_total_sent_formatted(self) -> str:
        """Get formatted total sent string.

        Returns:
            Formatted total sent string.
        """
        return f"{self.total_sent()} sent"

    def get_total_errors_formatted(self) -> str:
        """Get formatted total errors string.

        Returns:
            Formatted total errors string.
        """
        return f"{self.total_errors()} errors"

    def get_endpoint_count_formatted(self) -> str:
        """Get formatted endpoint count string.

        Returns:
            Formatted endpoint count string.
        """
        return f"{self.endpoint_count} endpoints"

    def get_success_rate(self) -> float:
        """Get success rate as percentage.

        Returns:
            Success rate percentage.
        """
        total = self.total_sent() + self.total_errors()
        if total == 0:
            return 0.0
        return round(self.total_sent() / total * 100, 2)

    def get_error_rate(self) -> float:
        """Get error rate as percentage.

        Returns:
            Error rate percentage.
        """
        total = self.total_sent() + self.total_errors()
        if total == 0:
            return 0.0
        return round(self.total_errors() / total * 100, 2)

    def get_success_rate_formatted(self) -> str:
        """Get formatted success rate string.

        Returns:
            Formatted success rate string.
        """
        return f"{self.get_success_rate():.1f}%"

    def get_error_rate_formatted(self) -> str:
        """Get formatted error rate string.

        Returns:
            Formatted error rate string.
        """
        return f"{self.get_error_rate():.1f}%"

    def get_stats_formatted(self) -> str:
        """Get formatted stats string.

        Returns:
            Formatted stats string.
        """
        return f"Endpoints: {self.endpoint_count}, Sent: {self.total_sent()}, Errors: {self.total_errors()}"

    def get_endpoint_names_formatted(self) -> str:
        """Get formatted endpoint names string.

        Returns:
            Formatted endpoint names string.
        """
        names = self.get_endpoint_names()
        if not names:
            return "none"
        return ", ".join(names)

    def get_total_count(self) -> int:
        """Get total count of sent and errors.

        Returns:
            Total count.
        """
        return self.total_sent() + self.total_errors()

    def get_total_count_formatted(self) -> str:
        """Get formatted total count string.

        Returns:
            Formatted total count string.
        """
        return f"{self.get_total_count()} total"
