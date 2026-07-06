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
