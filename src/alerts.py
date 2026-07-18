"""Alert system for log monitoring thresholds."""

import json
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List, Dict, Optional, Callable
from pathlib import Path


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents a triggered alert."""
    severity: AlertSeverity
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None

    def __repr__(self) -> str:
        return f"Alert(severity={self.severity.value}, metric={self.metric_name}, value={self.current_value})"

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.metric_name}: {self.current_value} > {self.threshold}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert alert to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=indent)


class AlertManager:
    """Manage alert thresholds and notifications."""

    def __init__(self):
        self.thresholds: Dict[str, Dict] = {}
        self.alerts: List[Alert] = []
        self.callbacks: List[Callable[[Alert], None]] = []
        self._lock = threading.Lock()

    def __repr__(self) -> str:
        return (
            f"AlertManager(thresholds={len(self.thresholds)}, "
            f"alerts={len(self.alerts)}, callbacks={len(self.callbacks)})"
        )

    def __str__(self) -> str:
        active = sum(1 for a in self.alerts if not a.acknowledged)
        return f"AlertManager({active} active / {len(self.alerts)} total alerts)"

    def __len__(self) -> int:
        """Get total number of alerts."""
        return len(self.alerts)

    def set_threshold(self, metric: str, value: float, severity: AlertSeverity = AlertSeverity.MEDIUM):
        """Set an alert threshold."""
        self.thresholds[metric] = {"value": value, "severity": severity}

    def check(self, metric: str, current_value: float) -> Optional[Alert]:
        """Check if a metric exceeds its threshold.

        Args:
            metric: Name of the metric to check.
            current_value: Current value of the metric.

        Returns:
            Alert if threshold exceeded, None otherwise.
        """
        if not metric or not isinstance(metric, str):
            return None
        if metric not in self.thresholds:
            return None
        if not isinstance(current_value, (int, float)):
            return None

        threshold = self.thresholds[metric]
        if current_value > threshold["value"]:
            alert = Alert(
                severity=threshold["severity"],
                message=f"{metric} exceeded threshold: {current_value} > {threshold['value']}",
                metric_name=metric,
                current_value=current_value,
                threshold=threshold["value"],
            )
            with self._lock:
                self.alerts.append(alert)
            self._notify(alert)
            return alert
        return None

    def register_callback(self, callback: Callable[[Alert], None]):
        """Register a notification callback."""
        self.callbacks.append(callback)

    def _notify(self, alert: Alert):
        """Send notifications for an alert."""
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception:
                pass

    def get_active_alerts(self) -> List[Alert]:
        """Get unacknowledged alerts."""
        return [a for a in self.alerts if not a.acknowledged]

    def acknowledge(self, index: int):
        """Acknowledge an alert by index.

        Args:
            index: Index of the alert to acknowledge.

        Raises:
            TypeError: If index is not an integer.
            IndexError: If index is out of range.
        """
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= len(self.alerts):
            raise IndexError(f"Alert index {index} out of range")
        self.alerts[index].acknowledged = True
        self.alerts[index].acknowledged_at = datetime.now()

    def export_alerts(self, output_path: str):
        """Export alerts to JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump([a.to_dict() for a in self.alerts], f, indent=2)

    def clear_alerts(self):
        """Remove all alerts from the manager."""
        with self._lock:
            self.alerts.clear()

    @property
    def alert_count(self) -> int:
        """Get total number of alerts."""
        return len(self.alerts)

    @property
    def has_active_alerts(self) -> bool:
        """Check if there are any unacknowledged alerts."""
        return any(not a.acknowledged for a in self.alerts)

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts filtered by severity.

        Args:
            severity: AlertSeverity to filter by.

        Returns:
            List of matching alerts.
        """
        return [a for a in self.alerts if a.severity == severity]

    def get_unacknowledged_count(self) -> int:
        """Get count of unacknowledged alerts.

        Returns:
            Number of alerts that have not been acknowledged.
        """
        return sum(1 for a in self.alerts if not a.acknowledged)

    def acknowledge_all(self) -> int:
        """Acknowledge all active alerts.

        Returns:
            Number of alerts acknowledged.
        """
        count = 0
        now = datetime.now()
        for alert in self.alerts:
            if not alert.acknowledged:
                alert.acknowledged = True
                alert.acknowledged_at = now
                count += 1
        return count

    def remove_threshold(self, metric: str) -> bool:
        """Remove an alert threshold.

        Args:
            metric: Metric name to remove.

        Returns:
            True if threshold was removed, False if not found.
        """
        if metric in self.thresholds:
            del self.thresholds[metric]
            return True
        return False

    def get_threshold(self, metric: str) -> Optional[Dict]:
        """Get threshold configuration for a metric.

        Args:
            metric: Metric name to look up.

        Returns:
            Threshold dict if found, None otherwise.
        """
        return self.thresholds.get(metric)

    def get_threshold_count(self) -> int:
        """Get number of configured thresholds.

        Returns:
            Count of thresholds.
        """
        return len(self.thresholds)

    def has_threshold(self, metric: str) -> bool:
        """Check if a threshold exists for a metric.

        Args:
            metric: Metric name to check.

        Returns:
            True if threshold exists.
        """
        return metric in self.thresholds

    def get_alerts_by_metric(self, metric: str) -> List[Alert]:
        """Get alerts filtered by metric name.

        Args:
            metric: Metric name to filter by.

        Returns:
            List of matching alerts.
        """
        return [a for a in self.alerts if a.metric_name == metric]

    def get_thresholds(self) -> Dict[str, Dict]:
        """Get all configured thresholds.

        Returns:
            Dictionary of threshold configurations.
        """
        return dict(self.thresholds)

    def get_alert_count(self) -> int:
        """Get total number of alerts.

        Returns:
            Count of alerts.
        """
        return len(self.alerts)

    def has_callbacks(self) -> bool:
        """Check if any callbacks are registered.

        Returns:
            True if callbacks exist.
        """
        return len(self.callbacks) > 0

    def get_alerts_dict(self) -> List[Dict[str, Any]]:
        """Get all alerts as dictionaries.

        Returns:
            List of alert dictionaries.
        """
        return [a.to_dict() for a in self.alerts]

    def get_active_alerts_dict(self) -> List[Dict[str, Any]]:
        """Get active alerts as dictionaries.

        Returns:
            List of active alert dictionaries.
        """
        return [a.to_dict() for a in self.alerts if not a.acknowledged]

    def has_thresholds(self) -> bool:
        """Check if any thresholds are configured.

        Returns:
            True if thresholds exist.
        """
        return len(self.thresholds) > 0

    def get_callback_count(self) -> int:
        """Get number of registered callbacks.

        Returns:
            Count of callbacks.
        """
        return len(self.callbacks)

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get alert manager statistics as dictionary.

        Returns:
            Dictionary with alert stats.
        """
        return {
            "thresholds": len(self.thresholds),
            "alerts": len(self.alerts),
            "active": self.get_unacknowledged_count(),
            "callbacks": len(self.callbacks),
        }

    def get_summary_string(self) -> str:
        """Get a formatted summary string.

        Returns:
            Formatted summary string.
        """
        return (
            f"Thresholds: {len(self.thresholds)}, "
            f"Alerts: {len(self.alerts)}, "
            f"Active: {self.get_unacknowledged_count()}"
        )

    def get_threshold_names(self) -> List[str]:
        """Get list of threshold metric names.

        Returns:
            List of metric name strings.
        """
        return list(self.thresholds.keys())
