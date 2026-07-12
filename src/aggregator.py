"""Log aggregation and statistics module."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

from .models import LogEntry, LogLevel, AnalysisResult


class LogAggregator:
    """Aggregate log entries for analysis and reporting."""

    def __init__(self, entries: List[LogEntry]):
        self.entries = entries

    def __repr__(self) -> str:
        return f"LogAggregator(entries={len(self.entries)})"

    @classmethod
    def from_entries(cls, *entry_lists: List[LogEntry]) -> "LogAggregator":
        """Create an aggregator from multiple entry lists.

        Args:
            *entry_lists: Variable number of entry lists to merge.

        Returns:
            LogAggregator containing all merged entries.

        Raises:
            TypeError: If any entry list is not a list.
        """
        merged = []
        for lst in entry_lists:
            if lst is None:
                continue
            if not isinstance(lst, list):
                raise TypeError(f"Expected list, got {type(lst).__name__}")
            merged.extend(lst)
        return cls(merged)

    def summary(self) -> AnalysisResult:
        """Generate summary statistics.

        Returns:
            AnalysisResult with aggregated statistics.
        """
        if not self.entries:
            return AnalysisResult()

        level_counts = Counter(e.level.value for e in self.entries)
        sources = list({e.source for e in self.entries if e.source})
        timestamps = [e.timestamp for e in self.entries]

        top_errors = [
            e.message[:200]
            for e in self.entries
            if e.level in (LogLevel.ERROR, LogLevel.CRITICAL)
        ][:10]

        return AnalysisResult(
            total_entries=len(self.entries),
            level_counts=dict(level_counts),
            time_range=(min(timestamps), max(timestamps)),
            top_errors=top_errors,
            sources=sources,
            duration_seconds=(max(timestamps) - min(timestamps)).total_seconds(),
        )

    def by_time_window(self, window_minutes: int = 60) -> Dict[str, List[LogEntry]]:
        """Group entries by time windows.

        Args:
            window_minutes: Size of each time window in minutes.

        Returns:
            Dictionary mapping ISO timestamps to lists of entries.

        Raises:
            ValueError: If window_minutes is less than 1.
        """
        if window_minutes < 1:
            raise ValueError("window_minutes must be at least 1")
        if not self.entries:
            return {}
        windows: Dict[str, List[LogEntry]] = defaultdict(list)
        for entry in self.entries:
            window_start = entry.timestamp.replace(
                minute=(entry.timestamp.minute // window_minutes) * window_minutes,
                second=0, microsecond=0
            )
            key = window_start.isoformat()
            windows[key].append(entry)
        return dict(windows)

    def error_rate(self) -> float:
        """Calculate error rate as percentage.

        Returns:
            Error rate as a float between 0 and 100.
        """
        if not self.entries:
            return 0.0
        total = len(self.entries)
        if total == 0:
            return 0.0
        errors = sum(1 for e in self.entries if e.level in (LogLevel.ERROR, LogLevel.CRITICAL))
        return (errors / total) * 100

    def top_sources(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top log sources by count."""
        if limit < 1:
            return []
        counts = Counter(e.source for e in self.entries if e.source)
        return counts.most_common(limit)

    def busiest_hours(self, limit: int = 5) -> List[Tuple[int, int]]:
        """Find busiest hours of the day."""
        hour_counts = Counter(e.timestamp.hour for e in self.entries)
        return sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def count_entries(self, level: Optional[LogLevel] = None) -> int:
        """Count entries, optionally filtered by level."""
        if level is None:
            return len(self.entries)
        return sum(1 for e in self.entries if e.level == level)

    def clear(self):
        """Clear all entries from the aggregator."""
        self.entries.clear()

    def has_entries(self) -> bool:
        """Check if aggregator has any entries."""
        return len(self.entries) > 0

    @property
    def is_empty(self) -> bool:
        """Check if aggregator has no entries."""
        return len(self.entries) == 0

    @property
    def level_counts(self) -> Dict[str, int]:
        """Get entry counts grouped by log level.

        Returns:
            Dictionary mapping level names to counts.
        """
        if not self.entries:
            return {}
        counts: Dict[str, int] = {}
        for entry in self.entries:
            level = entry.level.value
            counts[level] = counts.get(level, 0) + 1
        return counts

    @property
    def source_list(self) -> List[str]:
        """Get unique list of sources in entries.

        Returns:
            List of unique source names.
        """
        return list(set(e.source for e in self.entries if e.source))

    @property
    def entry_count(self) -> int:
        """Get total number of entries in the aggregator.

        Returns:
            Number of entries.
        """
        return len(self.entries)

    def level_distribution(self) -> Dict[str, float]:
        """Get percentage distribution of log levels.

        Returns:
            Dictionary mapping level names to their percentage.
        """
        if not self.entries:
            return {}
        total = len(self.entries)
        counts = self.level_counts
        return {level: round(count / total * 100, 2) for level, count in counts.items()}
