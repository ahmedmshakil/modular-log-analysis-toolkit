"""Data models for log entries and analysis results."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

__all__ = ["LogLevel", "LogEntry", "AnalysisResult"]


class LogLevel(Enum):
    """Supported log severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    TRACE = "TRACE"


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

    def __repr__(self) -> str:
        return f"LogEntry(level={self.level.value}, timestamp={self.timestamp}, message={self.message[:50]!r})"

    def __str__(self) -> str:
        return f"[{self.level.value}] {self.timestamp} - {self.message[:100]}"

    @property
    def is_error(self) -> bool:
        """Check if entry is an error or critical level."""
        return self.level in (LogLevel.ERROR, LogLevel.CRITICAL)

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "line_number": self.line_number,
            "tags": self.tags,
        }

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
        """Convert analysis result to dictionary."""
        return {
            "total_entries": self.total_entries,
            "level_counts": self.level_counts,
            "time_range": [t.isoformat() for t in self.time_range] if self.time_range else None,
            "top_errors": self.top_errors,
            "sources": self.sources,
            "duration_seconds": self.duration_seconds,
        }
