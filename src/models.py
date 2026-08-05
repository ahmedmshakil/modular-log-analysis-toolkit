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

    @property
    def is_trace(self) -> bool:
        """Check if entry is a trace level."""
        return self.level == LogLevel.TRACE

    @property
    def message_length(self) -> int:
        """Get length of the message.

        Returns:
            Length of message string.
        """
        return len(self.message) if self.message else 0

    def has_source(self) -> bool:
        """Check if entry has a source.

        Returns:
            True if source is set.
        """
        return self.source is not None and self.source != ""

    def has_tags(self) -> bool:
        """Check if entry has any tags.

        Returns:
            True if tags exist.
        """
        return len(self.tags) > 0

    def has_metadata(self) -> bool:
        """Check if entry has any metadata.

        Returns:
            True if metadata exists.
        """
        return len(self.metadata) > 0

    def get_tag(self, key: str) -> Optional[str]:
        """Get a specific tag value.

        Args:
            key: Tag key.

        Returns:
            Tag value if found, None otherwise.
        """
        return self.tags.get(key)

    def get_metadata(self, key: str) -> Optional[Any]:
        """Get a specific metadata value.

        Args:
            key: Metadata key.

        Returns:
            Metadata value if found, None otherwise.
        """
        return self.metadata.get(key)

    def set_tag(self, key: str, value: str):
        """Set a tag value.

        Args:
            key: Tag key.
            value: Tag value.
        """
        self.tags[key] = value

    def set_metadata(self, key: str, value: Any):
        """Set a metadata value.

        Args:
            key: Metadata key.
            value: Metadata value.
        """
        self.metadata[key] = value

    def remove_tag(self, key: str) -> bool:
        """Remove a tag.

        Args:
            key: Tag key to remove.

        Returns:
            True if tag was removed.
        """
        if key in self.tags:
            del self.tags[key]
            return True
        return False

    def clear_tags(self):
        """Clear all tags."""
        self.tags.clear()

    def clear_metadata(self):
        """Clear all metadata."""
        self.metadata.clear()

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

    def has_tag(self, key: str) -> bool:
        """Check if entry has a specific tag.

        Args:
            key: Tag key to check.

        Returns:
            True if tag exists.
        """
        return key in self.tags

    def has_metadata(self) -> bool:
        """Check if entry has any metadata.

        Returns:
            True if metadata exists.
        """
        return len(self.metadata) > 0

    def get_tags_as_string(self) -> str:
        """Get tags as formatted string.

        Returns:
            Formatted tags string.
        """
        if not self.tags:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in self.tags.items())

    def get_metadata_as_string(self) -> str:
        """Get metadata as formatted string.

        Returns:
            Formatted metadata string.
        """
        if not self.metadata:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in self.metadata.items())

    def get_level_formatted(self) -> str:
        """Get formatted level string.

        Returns:
            Formatted level string.
        """
        return f"[{self.level.value}]"

    def get_timestamp_formatted(self) -> str:
        """Get formatted timestamp string.

        Returns:
            Formatted timestamp string.
        """
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def get_source_formatted(self) -> str:
        """Get formatted source string.

        Returns:
            Formatted source string.
        """
        return self.source if self.source else "unknown"

    def get_message_preview(self, max_length: int = 50) -> str:
        """Get message preview with max length.

        Args:
            max_length: Maximum length of preview.

        Returns:
            Message preview string.
        """
        if not self.message:
            return ""
        if len(self.message) <= max_length:
            return self.message
        return self.message[:max_length] + "..."

    def get_entry_summary(self) -> str:
        """Get entry summary string.

        Returns:
            Entry summary string.
        """
        return (
            f"{self.get_level_formatted()} {self.get_timestamp_formatted()} "
            f"[{self.get_source_formatted()}] {self.get_message_preview()}"
        )

    def has_tag(self, key: str) -> bool:
        """Check if entry has a specific tag.

        Args:
            key: Tag key to check.

        Returns:
            True if tag exists.
        """
        return key in self.tags

    def has_metadata(self) -> bool:
        """Check if entry has any metadata.

        Returns:
            True if metadata exists.
        """
        return len(self.metadata) > 0

    def get_tags_as_string(self) -> str:
        """Get tags as formatted string.

        Returns:
            Formatted tags string.
        """
        if not self.tags:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in self.tags.items())

    def get_metadata_as_string(self) -> str:
        """Get metadata as formatted string.

        Returns:
            Formatted metadata string.
        """
        if not self.metadata:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in self.metadata.items())

    def get_level_formatted(self) -> str:
        """Get formatted level string.

        Returns:
            Formatted level string.
        """
        return f"[{self.level.value}]"

    def get_timestamp_formatted(self) -> str:
        """Get formatted timestamp string.

        Returns:
            Formatted timestamp string.
        """
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def get_source_formatted(self) -> str:
        """Get formatted source string.

        Returns:
            Formatted source string.
        """
        return self.source if self.source else "unknown"

    def get_message_preview(self, max_length: int = 50) -> str:
        """Get message preview with max length.

        Args:
            max_length: Maximum length of preview.

        Returns:
            Message preview string.
        """
        if not self.message:
            return ""
        if len(self.message) <= max_length:
            return self.message
        return self.message[:max_length] + "..."

    def get_entry_summary(self) -> str:
        """Get entry summary string.

        Returns:
            Entry summary string.
        """
        return (
            f"{self.get_level_formatted()} {self.get_timestamp_formatted()} "
            f"[{self.get_source_formatted()}] {self.get_message_preview()}"
        )

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

    @property
    def duration_hours(self) -> float:
        """Get duration in hours.

        Returns:
            Duration in hours.
        """
        return round(self.duration_seconds / 3600, 2)

    @property
    def info_count(self) -> int:
        """Get INFO level count.

        Returns:
            Count of INFO entries.
        """
        return self.level_counts.get("INFO", 0)

    @property
    def warn_count(self) -> int:
        """Get WARN level count.

        Returns:
            Count of WARN entries.
        """
        return self.level_counts.get("WARN", 0)

    @property
    def debug_count(self) -> int:
        """Get DEBUG level count.

        Returns:
            Count of DEBUG entries.
        """
        return self.level_counts.get("DEBUG", 0)

    @property
    def trace_count(self) -> int:
        """Get TRACE level count.

        Returns:
            Count of TRACE entries.
        """
        return self.level_counts.get("TRACE", 0)

    @property
    def has_sources(self) -> bool:
        """Check if analysis has sources.

        Returns:
            True if sources exist.
        """
        return len(self.sources) > 0

    @property
    def has_top_errors(self) -> bool:
        """Check if analysis has top errors.

        Returns:
            True if top errors exist.
        """
        return len(self.top_errors) > 0

    @property
    def has_time_range(self) -> bool:
        """Check if analysis has time range.

        Returns:
            True if time range exists.
        """
        return self.time_range is not None

    @property
    def has_duration(self) -> bool:
        """Check if analysis has duration.

        Returns:
            True if duration is greater than 0.
        """
        return self.duration_seconds > 0

    @property
    def top_error_count(self) -> int:
        """Get number of top errors.

        Returns:
            Count of top errors.
        """
        return len(self.top_errors)

    def get_level_count(self, level: str) -> int:
        """Get count for a specific level.

        Args:
            level: Level string (e.g., "ERROR", "INFO").

        Returns:
            Count for the level, 0 if not found.
        """
        return self.level_counts.get(level.upper(), 0)

    def get_summary_string(self) -> str:
        """Get a formatted summary string.

        Returns:
            Formatted summary string.
        """
        return (
            f"Entries: {self.total_entries}, "
            f"Errors: {self.error_count}, "
            f"Sources: {self.source_count}, "
            f"Duration: {self.duration_minutes:.1f}m"
        )

    def has_entries(self) -> bool:
        """Check if analysis has any entries.

        Returns:
            True if entries exist.
        """
        return self.total_entries > 0

    def has_errors(self) -> bool:
        """Check if analysis found any errors.

        Returns:
            True if errors exist.
        """
        return self.error_count > 0

    def has_sources(self) -> bool:
        """Check if analysis has sources.

        Returns:
            True if sources exist.
        """
        return self.source_count > 0

    def get_error_rate(self) -> float:
        """Get error rate as percentage.

        Returns:
            Error rate percentage.
        """
        if self.total_entries == 0:
            return 0.0
        return round(self.error_count / self.total_entries * 100, 2)

    def get_warning_rate(self) -> float:
        """Get warning rate as percentage.

        Returns:
            Warning rate percentage.
        """
        if self.total_entries == 0:
            return 0.0
        return round(self.warn_count / self.total_entries * 100, 2)

    def get_info_rate(self) -> float:
        """Get info rate as percentage.

        Returns:
            Info rate percentage.
        """
        if self.total_entries == 0:
            return 0.0
        return round(self.info_count / self.total_entries * 100, 2)

    def get_error_rate_formatted(self) -> str:
        """Get formatted error rate string.

        Returns:
            Formatted error rate string.
        """
        return f"{self.get_error_rate():.1f}%"

    def get_warning_rate_formatted(self) -> str:
        """Get formatted warning rate string.

        Returns:
            Formatted warning rate string.
        """
        return f"{self.get_warning_rate():.1f}%"

    def get_info_rate_formatted(self) -> str:
        """Get formatted info rate string.

        Returns:
            Formatted info rate string.
        """
        return f"{self.get_info_rate():.1f}%"

    def get_debug_rate_formatted(self) -> str:
        """Get formatted debug rate string.

        Returns:
            Formatted debug rate string.
        """
        return f"{self.get_debug_rate():.1f}%"

    def get_critical_rate_formatted(self) -> str:
        """Get formatted critical rate string.

        Returns:
            Formatted critical rate string.
        """
        return f"{self.get_critical_rate():.1f}%"

    def get_non_error_rate_formatted(self) -> str:
        """Get formatted non-error rate string.

        Returns:
            Formatted non-error rate string.
        """
        return f"{self.get_non_error_rate():.1f}%"

    def get_duration_formatted(self) -> str:
        """Get formatted duration string.

        Returns:
            Formatted duration string.
        """
        if self.duration_seconds < 60:
            return f"{self.duration_seconds:.1f}s"
        if self.duration_seconds < 3600:
            return f"{self.duration_minutes:.1f}m"
        return f"{self.duration_hours:.1f}h"

    def get_entries_per_second(self) -> float:
        """Get entries per second rate.

        Returns:
            Entries per second.
        """
        if self.duration_seconds == 0:
            return 0.0
        return round(self.total_entries / self.duration_seconds, 2)

    def get_entries_per_minute(self) -> float:
        """Get entries per minute rate.

        Returns:
            Entries per minute.
        """
        if self.duration_seconds == 0:
            return 0.0
        return round(self.total_entries / (self.duration_seconds / 60), 2)

    def get_entries_per_second_formatted(self) -> str:
        """Get formatted entries per second string.

        Returns:
            Formatted entries per second string.
        """
        return f"{self.get_entries_per_second():.2f} entries/s"

    def get_entries_per_minute_formatted(self) -> str:
        """Get formatted entries per minute string.

        Returns:
            Formatted entries per minute string.
        """
        return f"{self.get_entries_per_minute():.2f} entries/m"

    def get_error_count_formatted(self) -> str:
        """Get formatted error count string.

        Returns:
            Formatted error count string.
        """
        return f"{self.error_count} errors"

    def get_warning_count_formatted(self) -> str:
        """Get formatted warning count string.

        Returns:
            Formatted warning count string.
        """
        return f"{self.warn_count} warnings"

    def get_info_count_formatted(self) -> str:
        """Get formatted info count string.

        Returns:
            Formatted info count string.
        """
        return f"{self.info_count} info"

    def get_debug_count_formatted(self) -> str:
        """Get formatted debug count string.

        Returns:
            Formatted debug count string.
        """
        return f"{self.debug_count} debug"

    def get_trace_count_formatted(self) -> str:
        """Get formatted trace count string.

        Returns:
            Formatted trace count string.
        """
        return f"{self.trace_count} trace"

    def get_critical_count_formatted(self) -> str:
        """Get formatted critical count string.

        Returns:
            Formatted critical count string.
        """
        return f"{self.level_counts.get('CRITICAL', 0)} critical"

    def get_source_count_formatted(self) -> str:
        """Get formatted source count string.

        Returns:
            Formatted source count string.
        """
        return f"{self.source_count} sources"

    def get_total_entries_formatted(self) -> str:
        """Get formatted total entries string.

        Returns:
            Formatted total entries string.
        """
        return f"{self.total_entries} entries"

    def get_level_counts_formatted(self) -> str:
        """Get formatted level counts string.

        Returns:
            Formatted level counts string.
        """
        if not self.level_counts:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in self.level_counts.items())

    def get_sources_formatted(self) -> str:
        """Get formatted sources string.

        Returns:
            Formatted sources string.
        """
        if not self.sources:
            return "none"
        return ", ".join(self.sources)

    def get_top_errors_formatted(self, limit: int = 5) -> str:
        """Get formatted top errors string.

        Args:
            limit: Maximum number of errors.

        Returns:
            Formatted top errors string.
        """
        if not self.top_errors:
            return "none"
        return ", ".join(self.top_errors[:limit])

    def get_time_range_formatted(self) -> str:
        """Get formatted time range string.

        Returns:
            Formatted time range string.
        """
        if not self.time_range:
            return "none"
        return f"{self.time_range[0].isoformat()} to {self.time_range[1].isoformat()}"

    def get_level_distribution_formatted(self) -> str:
        """Get formatted level distribution string.

        Returns:
            Formatted level distribution string.
        """
        dist = self.get_level_distribution()
        if not dist:
            return "none"
        return ", ".join(f"{k}:{v:.1f}%" for k, v in dist.items())

    def get_most_common_level_formatted(self) -> str:
        """Get formatted most common level string.

        Returns:
            Formatted most common level string.
        """
        level = self.get_most_common_level()
        return level if level else "none"

    def get_least_common_level_formatted(self) -> str:
        """Get formatted least common level string.

        Returns:
            Formatted least common level string.
        """
        level = self.get_least_common_level()
        return level if level else "none"

    def get_stats_formatted(self) -> str:
        """Get formatted stats string.

        Returns:
            Formatted stats string.
        """
        return f"Entries: {self.total_entries}, Errors: {self.error_count}, Sources: {self.source_count}, Duration: {self.get_duration_formatted()}"

    def get_error_rate_percent(self) -> float:
        """Get error rate as percentage.

        Returns:
            Error rate percentage.
        """
        return self.get_error_rate()

    def get_warning_rate_percent(self) -> float:
        """Get warning rate as percentage.

        Returns:
            Warning rate percentage.
        """
        return self.get_warning_rate()

    def get_info_rate_percent(self) -> float:
        """Get info rate as percentage.

        Returns:
            Info rate percentage.
        """
        return self.get_info_rate()

    def get_debug_rate_percent(self) -> float:
        """Get debug rate as percentage.

        Returns:
            Debug rate percentage.
        """
        return self.get_debug_rate()

    def get_critical_rate_percent(self) -> float:
        """Get critical rate as percentage.

        Returns:
            Critical rate percentage.
        """
        return self.get_critical_rate()

    def get_non_error_rate_percent(self) -> float:
        """Get non-error rate as percentage.

        Returns:
            Non-error rate percentage.
        """
        return self.get_non_error_rate()

    def get_entries_per_second_rate(self) -> float:
        """Get entries per second rate.

        Returns:
            Entries per second rate.
        """
        return self.get_entries_per_second()

    def get_entries_per_minute_rate(self) -> float:
        """Get entries per minute rate.

        Returns:
            Entries per minute rate.
        """
        return self.get_entries_per_minute()

    def get_summary_formatted(self) -> str:
        """Get formatted summary string.

        Returns:
            Formatted summary string.
        """
        return self.get_summary_string()

    def get_duration_seconds_formatted(self) -> str:
        """Get formatted duration seconds string.

        Returns:
            Formatted duration seconds string.
        """
        return f"{self.duration_seconds:.2f}s"

    def get_duration_minutes_formatted(self) -> str:
        """Get formatted duration minutes string.

        Returns:
            Formatted duration minutes string.
        """
        return f"{self.duration_minutes:.2f}m"

    def get_duration_hours_formatted(self) -> str:
        """Get formatted duration hours string.

        Returns:
            Formatted duration hours string.
        """
        return f"{self.duration_hours:.2f}h"

    def get_entries_per_hour(self) -> float:
        """Get entries per hour rate.

        Returns:
            Entries per hour.
        """
        if self.duration_seconds == 0:
            return 0.0
        return round(self.total_entries / (self.duration_seconds / 3600), 2)

    def get_entries_per_hour_formatted(self) -> str:
        """Get formatted entries per hour string.

        Returns:
            Formatted entries per hour string.
        """
        return f"{self.get_entries_per_hour():.2f} entries/h"

    def get_error_to_warning_ratio(self) -> float:
        """Get error to warning ratio.

        Returns:
            Error to warning ratio.
        """
        if self.warn_count == 0:
            return float('inf') if self.error_count > 0 else 0.0
        return round(self.error_count / self.warn_count, 2)

    def get_error_to_warning_ratio_formatted(self) -> str:
        """Get formatted error to warning ratio string.

        Returns:
            Formatted ratio string.
        """
        ratio = self.get_error_to_warning_ratio()
        if ratio == float('inf'):
            return "inf"
        return f"{ratio:.2f}"

    def has_debug_entries(self) -> bool:
        """Check if analysis has debug entries.

        Returns:
            True if debug entries exist.
        """
        return self.debug_count > 0

    def has_trace_entries(self) -> bool:
        """Check if analysis has trace entries.

        Returns:
            True if trace entries exist.
        """
        return self.trace_count > 0

    def has_info_entries(self) -> bool:
        """Check if analysis has info entries.

        Returns:
            True if info entries exist.
        """
        return self.info_count > 0

    def has_warn_entries(self) -> bool:
        """Check if analysis has warning entries.

        Returns:
            True if warning entries exist.
        """
        return self.warn_count > 0

    def get_level_summary(self) -> str:
        """Get level summary string.

        Returns:
            Formatted level summary.
        """
        parts = []
        if self.trace_count > 0:
            parts.append(f"TRACE:{self.trace_count}")
        if self.debug_count > 0:
            parts.append(f"DEBUG:{self.debug_count}")
        if self.info_count > 0:
            parts.append(f"INFO:{self.info_count}")
        if self.warn_count > 0:
            parts.append(f"WARN:{self.warn_count}")
        if self.error_count > 0:
            parts.append(f"ERROR:{self.error_count}")
        if self.level_counts.get("CRITICAL", 0) > 0:
            parts.append(f"CRITICAL:{self.level_counts.get('CRITICAL', 0)}")
        return ", ".join(parts) if parts else "none"

    def get_sources_summary(self) -> str:
        """Get sources summary string.

        Returns:
            Formatted sources summary.
        """
        if not self.sources:
            return "none"
        if len(self.sources) <= 3:
            return ", ".join(self.sources)
        return f"{', '.join(self.sources[:3])} (+{len(self.sources) - 3} more)"

    def get_error_percentage_formatted(self) -> str:
        """Get formatted error percentage string.

        Returns:
            Formatted error percentage string.
        """
        return f"{self.get_error_rate():.1f}%"

    def get_warning_percentage_formatted(self) -> str:
        """Get formatted warning percentage string.

        Returns:
            Formatted warning percentage string.
        """
        return f"{self.get_warning_rate():.1f}%"

    def get_info_percentage_formatted(self) -> str:
        """Get formatted info percentage string.

        Returns:
            Formatted info percentage string.
        """
        return f"{self.get_info_rate():.1f}%"

    def get_debug_percentage_formatted(self) -> str:
        """Get formatted debug percentage string.

        Returns:
            Formatted debug percentage string.
        """
        return f"{self.get_debug_rate():.1f}%"

    def get_critical_percentage_formatted(self) -> str:
        """Get formatted critical percentage string.

        Returns:
            Formatted critical percentage string.
        """
        return f"{self.get_critical_rate():.1f}%"

    def get_non_error_percentage_formatted(self) -> str:
        """Get formatted non-error percentage string.

        Returns:
            Formatted non-error percentage string.
        """
        return f"{self.get_non_error_rate():.1f}%"

    def get_duration_in_seconds_formatted(self) -> str:
        """Get formatted duration in seconds string.

        Returns:
            Formatted duration in seconds string.
        """
        return f"{self.duration_seconds:.2f}s"

    def get_duration_in_minutes_formatted(self) -> str:
        """Get formatted duration in minutes string.

        Returns:
            Formatted duration in minutes string.
        """
        return f"{self.duration_minutes:.2f}m"

    def get_duration_in_hours_formatted(self) -> str:
        """Get formatted duration in hours string.

        Returns:
            Formatted duration in hours string.
        """
        return f"{self.duration_hours:.2f}h"

    def get_entries_per_second_formatted_alt(self) -> str:
        """Get formatted entries per second string (alternative).

        Returns:
            Formatted entries per second string.
        """
        return f"{self.get_entries_per_second():.2f}/s"

    def get_entries_per_minute_formatted_alt(self) -> str:
        """Get formatted entries per minute string (alternative).

        Returns:
            Formatted entries per minute string.
        """
        return f"{self.get_entries_per_minute():.2f}/m"

    def get_entries_per_hour_formatted_alt(self) -> str:
        """Get formatted entries per hour string (alternative).

        Returns:
            Formatted entries per hour string.
        """
        return f"{self.get_entries_per_hour():.2f}/h"

    def get_error_to_warning_ratio_formatted_alt(self) -> str:
        """Get formatted error to warning ratio string (alternative).

        Returns:
            Formatted ratio string.
        """
        ratio = self.get_error_to_warning_ratio()
        if ratio == float('inf'):
            return "inf"
        return f"{ratio:.2f}:1"

    def get_level_summary_formatted(self) -> str:
        """Get formatted level summary string.

        Returns:
            Formatted level summary string.
        """
        return self.get_level_summary()

    def get_sources_summary_formatted(self) -> str:
        """Get formatted sources summary string.

        Returns:
            Formatted sources summary string.
        """
        return self.get_sources_summary()

    def get_error_count_formatted_alt(self) -> str:
        """Get formatted error count string (alternative).

        Returns:
            Formatted error count string.
        """
        return f"{self.error_count} errors"

    def get_warning_count_formatted_alt(self) -> str:
        """Get formatted warning count string (alternative).

        Returns:
            Formatted warning count string.
        """
        return f"{self.warn_count} warnings"

    def get_info_count_formatted_alt(self) -> str:
        """Get formatted info count string (alternative).

        Returns:
            Formatted info count string.
        """
        return f"{self.info_count} info"

    def get_debug_count_formatted_alt(self) -> str:
        """Get formatted debug count string (alternative).

        Returns:
            Formatted debug count string.
        """
        return f"{self.debug_count} debug"

    def get_critical_count_formatted_alt(self) -> str:
        """Get formatted critical count string (alternative).

        Returns:
            Formatted critical count string.
        """
        return f"{self.level_counts.get('CRITICAL', 0)} critical"

    def get_trace_count_formatted_alt(self) -> str:
        """Get formatted trace count string (alternative).

        Returns:
            Formatted trace count string.
        """
        return f"{self.trace_count} trace"

    def get_source_count_formatted_alt(self) -> str:
        """Get formatted source count string (alternative).

        Returns:
            Formatted source count string.
        """
        return f"{self.source_count} sources"

    def get_total_entries_formatted_alt(self) -> str:
        """Get formatted total entries string (alternative).

        Returns:
            Formatted total entries string.
        """
        return f"{self.total_entries} entries"

    def get_level_counts_formatted_alt(self) -> str:
        """Get formatted level counts string (alternative).

        Returns:
            Formatted level counts string.
        """
        if not self.level_counts:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in self.level_counts.items())

    def get_sources_formatted_alt(self) -> str:
        """Get formatted sources string (alternative).

        Returns:
            Formatted sources string.
        """
        if not self.sources:
            return "none"
        return ", ".join(self.sources)

    def get_top_errors_formatted_alt(self, limit: int = 5) -> str:
        """Get formatted top errors string (alternative).

        Args:
            limit: Maximum number of errors.

        Returns:
            Formatted top errors string.
        """
        if not self.top_errors:
            return "none"
        return ", ".join(self.top_errors[:limit])

    def get_time_range_formatted_alt(self) -> str:
        """Get formatted time range string (alternative).

        Returns:
            Formatted time range string.
        """
        if not self.time_range:
            return "none"
        return f"{self.time_range[0].isoformat()} to {self.time_range[1].isoformat()}"

    def get_level_distribution_formatted_alt(self) -> str:
        """Get formatted level distribution string (alternative).

        Returns:
            Formatted level distribution string.
        """
        dist = self.get_level_distribution()
        if not dist:
            return "none"
        return ", ".join(f"{k}:{v:.1f}%" for k, v in dist.items())

    def get_most_common_level_formatted_alt(self) -> str:
        """Get formatted most common level string (alternative).

        Returns:
            Formatted most common level string.
        """
        level = self.get_most_common_level()
        return level if level else "none"

    def get_least_common_level_formatted_alt(self) -> str:
        """Get formatted least common level string (alternative).

        Returns:
            Formatted least common level string.
        """
        level = self.get_least_common_level()
        return level if level else "none"

    def get_stats_formatted_alt(self) -> str:
        """Get formatted stats string (alternative).

        Returns:
            Formatted stats string.
        """
        return f"Entries: {self.total_entries}, Errors: {self.error_count}, Sources: {self.source_count}, Duration: {self.get_duration_formatted()}"

    def get_error_rate_percent_alt(self) -> float:
        """Get error rate as percentage (alternative).

        Returns:
            Error rate percentage.
        """
        return self.get_error_rate()

    def get_warning_rate_percent_alt(self) -> float:
        """Get warning rate as percentage (alternative).

        Returns:
            Warning rate percentage.
        """
        return self.get_warning_rate()

    def get_info_rate_percent_alt(self) -> float:
        """Get info rate as percentage (alternative).

        Returns:
            Info rate percentage.
        """
        return self.get_info_rate()

    def get_debug_rate_percent_alt(self) -> float:
        """Get debug rate as percentage (alternative).

        Returns:
            Debug rate percentage.
        """
        return self.get_debug_rate()

    def get_critical_rate_percent_alt(self) -> float:
        """Get critical rate as percentage (alternative).

        Returns:
            Critical rate percentage.
        """
        return self.get_critical_rate()

    def get_non_error_rate_percent_alt(self) -> float:
        """Get non-error rate as percentage (alternative).

        Returns:
            Non-error rate percentage.
        """
        return self.get_non_error_rate()

    def get_entries_per_second_rate_alt(self) -> float:
        """Get entries per second rate (alternative).

        Returns:
            Entries per second rate.
        """
        return self.get_entries_per_second()

    def get_entries_per_minute_rate_alt(self) -> float:
        """Get entries per minute rate (alternative).

        Returns:
            Entries per minute rate.
        """
        return self.get_entries_per_minute()

    def get_entries_per_hour_rate_alt(self) -> float:
        """Get entries per hour rate (alternative).

        Returns:
            Entries per hour rate.
        """
        return self.get_entries_per_hour()

    def get_summary_formatted_alt(self) -> str:
        """Get formatted summary string (alternative).

        Returns:
            Formatted summary string.
        """
        return self.get_summary_string()

    def get_duration_seconds_formatted_alt(self) -> str:
        """Get formatted duration seconds string (alternative).

        Returns:
            Formatted duration seconds string.
        """
        return f"{self.duration_seconds:.2f}s"

    def get_duration_minutes_formatted_alt(self) -> str:
        """Get formatted duration minutes string (alternative).

        Returns:
            Formatted duration minutes string.
        """
        return f"{self.duration_minutes:.2f}m"

    def get_duration_hours_formatted_alt(self) -> str:
        """Get formatted duration hours string (alternative).

        Returns:
            Formatted duration hours string.
        """
        return f"{self.duration_hours:.2f}h"

