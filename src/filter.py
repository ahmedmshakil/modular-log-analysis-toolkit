"""Log filtering and query engine."""

from datetime import datetime
from typing import List, Optional, Callable

from .models import LogEntry, LogLevel


class LogFilter:
    """Filter log entries by various criteria."""

    def __init__(self, entries: List[LogEntry]):
        self.entries = entries
        self._filters: List[Callable[[LogEntry], bool]] = []

    def by_level(self, *levels: LogLevel) -> "LogFilter":
        """Filter by log level."""
        def _filter(entry: LogEntry) -> bool:
            return entry.level in levels
        self._filters.append(_filter)
        return self

    def by_time_range(self, start: datetime, end: datetime) -> "LogFilter":
        """Filter by time range."""
        def _filter(entry: LogEntry) -> bool:
            return start <= entry.timestamp <= end
        self._filters.append(_filter)
        return self

    def by_source(self, source: str) -> "LogFilter":
        """Filter by log source."""
        def _filter(entry: LogEntry) -> bool:
            if not entry.source:
                return False
            return source.lower() in entry.source.lower()
        self._filters.append(_filter)
        return self

    def by_keyword(self, keyword: str, case_sensitive: bool = False) -> "LogFilter":
        """Filter by keyword in message."""
        def _filter(entry: LogEntry) -> bool:
            msg = entry.message if case_sensitive else entry.message.lower()
            kw = keyword if case_sensitive else keyword.lower()
            return kw in msg
        self._filters.append(_filter)
        return self

    def by_regex(self, pattern: str) -> "LogFilter":
        """Filter by regex pattern match on message."""
        import re
        compiled = re.compile(pattern)
        def _filter(entry: LogEntry) -> bool:
            return bool(compiled.search(entry.message))
        self._filters.append(_filter)
        return self

    def clear_filters(self) -> "LogFilter":
        """Remove all pending filters."""
        self._filters.clear()
        return self

    def apply(self) -> List[LogEntry]:
        """Apply all filters and return matching entries."""
        result = self.entries
        for f in self._filters:
            result = [e for e in result if f(e)]
        return result

    def count_by_level(self) -> dict:
        """Count entries grouped by level."""
        if not self.entries:
            return {}
        counts = {}
        for entry in self.entries:
            level = entry.level.value
            counts[level] = counts.get(level, 0) + 1
        return counts
