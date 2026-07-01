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

    def __repr__(self) -> str:
        return f"LogEntry(level={self.level.value}, timestamp={self.timestamp}, message={self.message[:50]!r})"

    def __str__(self) -> str:
        return f"[{self.level.value}] {self.timestamp} - {self.message[:100]}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "line_number": self.line_number,
            "tags": self.tags,
        }


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
