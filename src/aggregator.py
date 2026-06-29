"""Log aggregation and statistics module."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

from .models import LogEntry, LogLevel, AnalysisResult


class LogAggregator:
    """Aggregate log entries for analysis and reporting."""

    def __init__(self, entries: List[LogEntry]):
        self.entries = entries

    def summary(self) -> AnalysisResult:
        """Generate summary statistics."""
        if not self.entries:
            return AnalysisResult()

        level_counts = Counter(e.level.value for e in self.entries)
        sources = list(set(e.source for e in self.entries if e.source))
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
        )

    def by_time_window(self, window_minutes: int = 60) -> Dict[str, List[LogEntry]]:
        """Group entries by time windows."""
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
        """Calculate error rate as percentage."""
        if not self.entries:
            return 0.0
        total = len(self.entries)
        errors = sum(1 for e in self.entries if e.level in (LogLevel.ERROR, LogLevel.CRITICAL))
        return (errors / total) * 100

    def top_sources(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top log sources by count."""
        counts = Counter(e.source for e in self.entries if e.source)
        return counts.most_common(limit)

    def busiest_hours(self, limit: int = 5) -> List[Tuple[int, int]]:
        """Find busiest hours of the day."""
        hour_counts = Counter(e.timestamp.hour for e in self.entries)
        return sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
