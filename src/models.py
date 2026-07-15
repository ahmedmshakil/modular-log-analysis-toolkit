"""Data models for log entries and analysis results."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

__all__ = ["LogLevel", "LogEntry", "AnalysisResult", "LOG_LEVEL_ORDER"]


class LogLevel(Enum):
    """Supported log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    TRACE = "TRACE"


LOG_LEVEL_ORDER = [
    LogLevel.TRACE,
    LogLevel.DEBUG,
    LogLevel.INFO,
    LogLevel.WARN,
    LogLevel.ERROR,
    LogLevel.CRITICAL,
]


@dataclass
class LogEntry:
    """Represents a single parsed log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    source: Optional[str] = None
    line_number: int = 0
    raw: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LogEntry):
            return NotImplemented
        return (
            self.timestamp == other.timestamp
            and self.level == other.level
            and self.message == other.message
            and self.source == other.source
        )

    def __hash__(self) -> int:
        """Make LogEntry hashable for use in sets and dicts."""
        return hash((self.timestamp, self.level, self.message, self.source))

    def __repr__(self) -> str:
        msg_preview = self.message[:50] if self.message else ""
        return f"LogEntry(level={self.level.value}, timestamp={self.timestamp}, message={msg_preview!r})"

    def __str__(self) -> str:
        msg = self.message[:100] if self.message else ""
        return f"[{self.level.value}] {self.timestamp} - {msg}"

    @property
    def is_error(self) -> bool:
        """Check if entry is an error or critical level."""
        return self.level in (LogLevel.ERROR, LogLevel.CRITICAL)

    @property
    def is_warning(self) -> bool:
        """Check if entry is a warning level."""
        return self.level == LogLevel.WARN

    @property
    def is_debug(self) -> bool:
        """Check if entry is a debug level."""
        return self.level == LogLevel.DEBUG

    @property
    def is_info(self) -> bool:
        """Check if entry is an info level."""
        return self.level == LogLevel.INFO

    @property
    def is_critical(self) -> bool:
        """Check if entry is a critical level."""
        return self.level == LogLevel.CRITICAL

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary.

        Returns:
            Dictionary representation of the log entry.
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "line_number": self.line_number,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @property
    def severity_rank(self) -> int:
        """Get numeric severity rank for comparison.

        Returns:
            Integer rank where lower is less severe.
        """
        ranks = {
            LogLevel.TRACE: 0,
            LogLevel.DEBUG: 1,
            LogLevel.INFO: 2,
            LogLevel.WARN: 3,
            LogLevel.ERROR: 4,
            LogLevel.CRITICAL: 5,
        }
        return ranks.get(self.level, 2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create a LogEntry from a dictionary."""
        ts = data.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = datetime.now()
        elif not isinstance(ts, datetime):
            ts = datetime.now()

        level_str = data.get("level", "INFO")
        if not isinstance(level_str, str):
            level_str = "INFO"
        try:
            level = LogLevel(level_str)
        except ValueError:
            level = LogLevel.INFO

        return cls(
            timestamp=ts,
            level=level,
            message=data.get("message", ""),
            source=data.get("source"),
            line_number=data.get("line_number", 0),
            tags=data.get("tags", {}),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AnalysisResult:
    """Aggregated result from log analysis."""
    total_entries: int = 0
    level_counts: Dict[str, int] = field(default_factory=dict)
    time_range: Optional[tuple] = None
    top_errors: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0

    def __str__(self) -> str:
        return (
            f"AnalysisResult(entries={self.total_entries}, "
            f"errors={self.level_counts.get('ERROR', 0)}, "
            f"sources={len(self.sources)})"
        )

    def __repr__(self) -> str:
        return (
            f"AnalysisResult(total_entries={self.total_entries}, "
            f"level_counts={self.level_counts}, "
            f"duration={self.duration_seconds:.2f}s)"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary.

        Returns:
            Dictionary with total_entries, level_counts, time_range,
            top_errors, sources, and duration_seconds.
        """
        return {
            "total_entries": self.total_entries,
            "level_counts": self.level_counts,
            "time_range": [t.isoformat() for t in self.time_range] if self.time_range else None,
            "top_errors": self.top_errors,
            "sources": self.sources,
            "duration_seconds": self.duration_seconds,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Create an AnalysisResult from a dictionary.

        Args:
            data: Dictionary containing analysis result fields.

        Returns:
            AnalysisResult instance.
        """
        time_range = None
        if data.get("time_range"):
            try:
                time_range = tuple(datetime.fromisoformat(t) for t in data["time_range"])
            except (ValueError, TypeError):
                time_range = None

        return cls(
            total_entries=data.get("total_entries", 0),
            level_counts=data.get("level_counts", {}),
            time_range=time_range,
            top_errors=data.get("top_errors", []),
            sources=data.get("sources", []),
            duration_seconds=data.get("duration_seconds", 0.0),
        )

    @property
    def error_count(self) -> int:
        """Get total error and critical count.

        Returns:
            Sum of ERROR and CRITICAL level counts.
        """
        return self.level_counts.get("ERROR", 0) + self.level_counts.get("CRITICAL", 0)

    @property
    def has_errors(self) -> bool:
        """Check if analysis found any errors.

        Returns:
            True if there are ERROR or CRITICAL entries.
        """
        return self.error_count > 0

    @property
    def source_count(self) -> int:
        """Get number of unique sources.

        Returns:
            Count of unique sources.
        """
        return len(self.sources)

    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes.

        Returns:
            Duration in minutes.
        """
        return round(self.duration_seconds / 60, 2)
