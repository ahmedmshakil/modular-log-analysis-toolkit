"""Log filtering and query engine."""

import re
from datetime import datetime
from typing import List, Optional, Callable

from .models import LogEntry, LogLevel


class LogFilter:
    """Filter log entries by various criteria."""

    def __init__(self, entries: List[LogEntry]):
        self.entries = entries
        self._filters: List[Callable[[LogEntry], bool]] = []

    def __repr__(self) -> str:
        return f"LogFilter(entries={len(self.entries)}, filters={len(self._filters)})"

    def __len__(self) -> int:
        return len(self.entries)

    def __contains__(self, entry: LogEntry) -> bool:
        """Check if an entry exists in the filter."""
        return any(
            e.timestamp == entry.timestamp
            and e.level == entry.level
            and e.message == entry.message
            and e.source == entry.source
            for e in self.entries
        )

    @property
    def is_empty(self) -> bool:
        """Check if there are no entries to filter."""
        return len(self.entries) == 0

    @property
    def entry_count(self) -> int:
        """Get the total number of entries."""
        return len(self.entries)

    def by_level(self, *levels: LogLevel) -> "LogFilter":
        """Filter by log level.

        Args:
            *levels: One or more LogLevel values to match.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If no levels provided.
        """
        if not levels:
            raise ValueError("At least one level must be provided")
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
        if not source:
            raise ValueError("Source filter cannot be empty")
        def _filter(entry: LogEntry) -> bool:
            if not entry.source:
                return False
            return source.lower() in entry.source.lower()
        self._filters.append(_filter)
        return self

    def by_keyword(self, keyword: str, case_sensitive: bool = False) -> "LogFilter":
        """Filter by keyword in message.

        Args:
            keyword: The keyword to search for.
            case_sensitive: Whether the search is case-sensitive.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If keyword is empty.
        """
        if not keyword or not isinstance(keyword, str):
            raise ValueError("Keyword must be a non-empty string")
        def _filter(entry: LogEntry) -> bool:
            if not entry.message:
                return False
            msg = entry.message if case_sensitive else entry.message.lower()
            kw = keyword if case_sensitive else keyword.lower()
            return kw in msg
        self._filters.append(_filter)
        return self

    def by_regex(self, pattern: str) -> "LogFilter":
        """Filter by regex pattern match on message.

        Args:
            pattern: Regular expression pattern to match.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If pattern is empty or invalid.
        """
        if not pattern or not isinstance(pattern, str):
            raise ValueError("Pattern must be a non-empty string")
        try:
            compiled = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        def _filter(entry: LogEntry) -> bool:
            if not entry.message:
                return False
            return bool(compiled.search(entry.message))
        self._filters.append(_filter)
        return self

    def clear_filters(self) -> "LogFilter":
        """Remove all pending filters."""
        self._filters.clear()
        return self

    def apply(self) -> List[LogEntry]:
        """Apply all filters and return matching entries.

        Returns:
            List of entries matching all active filters.
        """
        if not self.entries:
            return []
        if not self._filters:
            return list(self.entries)
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

    def merge(self, other: "LogFilter") -> "LogFilter":
        """Merge entries from another LogFilter, removing duplicates."""
        seen = set()
        merged = []
        for entry in self.entries + other.entries:
            key = (entry.timestamp, entry.level, entry.message, entry.source)
            if key not in seen:
                seen.add(key)
                merged.append(entry)
        return LogFilter(merged)

    def reset(self) -> "LogFilter":
        """Clear all pending filters without removing entries.

        Returns:
            Self for method chaining.
        """
        self._filters.clear()
        return self

    def get_entries(self) -> List[LogEntry]:
        """Get a copy of the current entries list.

        Returns:
            Copy of the entries list.
        """
        return list(self.entries)
