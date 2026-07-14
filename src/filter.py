"""Log filtering and query engine."""

import re
from collections import Counter
from datetime import datetime
from typing import List, Optional, Callable

from .models import LogEntry, LogLevel


class LogFilter:
    """Filter log entries by various criteria."""

    def __init__(self, entries: List[LogEntry]):
        self.entries = entries
        self._filters: List[Callable[[LogEntry], bool]] = []
        self._entry_set = {(e.timestamp, e.level, e.message, e.source) for e in entries}
        self._regex_cache: Dict[str, re.Pattern] = {}

    def __repr__(self) -> str:
        return f"LogFilter(entries={len(self.entries)}, filters={len(self._filters)})"

    def __len__(self) -> int:
        return len(self.entries)

    def __contains__(self, entry: LogEntry) -> bool:
        """Check if an entry exists in the filter.

        Args:
            entry: LogEntry to check for.

        Returns:
            True if entry exists, False otherwise.
        """
        if not isinstance(entry, LogEntry):
            return False
        return (entry.timestamp, entry.level, entry.message, entry.source) in self._entry_set

    @property
    def is_empty(self) -> bool:
        """Check if there are no entries to filter."""
        return len(self.entries) == 0

    def has_entries(self) -> bool:
        """Check if there are entries to filter.

        Returns:
            True if entries exist, False otherwise.
        """
        return len(self.entries) > 0

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
        # Use cached compiled regex if available
        if pattern in self._regex_cache:
            compiled = self._regex_cache[pattern]
        else:
            try:
                compiled = re.compile(pattern)
                self._regex_cache[pattern] = compiled
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

    def apply_count(self) -> int:
        """Count matching entries without building the full list.

        Returns:
            Number of entries matching all active filters.
        """
        if not self.entries:
            return 0
        if not self._filters:
            return len(self.entries)
        count = 0
        for entry in self.entries:
            if all(f(entry) for f in self._filters):
                count += 1
        return count

    def count_by_level(self) -> dict:
        """Count entries grouped by level."""
        if not self.entries:
            return {}
        return dict(Counter(e.level.value for e in self.entries))

    def first(self, n: int = 1) -> List[LogEntry]:
        """Get first N entries.

        Args:
            n: Number of entries to return.

        Returns:
            List of first N entries.
        """
        if n < 1:
            return []
        return list(self.entries[:n])

    def last(self, n: int = 1) -> List[LogEntry]:
        """Get last N entries.

        Args:
            n: Number of entries to return.

        Returns:
            List of last N entries.
        """
        if n < 1:
            return []
        return list(self.entries[-n:])

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

    def by_multiple_keywords(self, keywords: List[str], match_all: bool = False) -> "LogFilter":
        """Filter by multiple keywords.

        Args:
            keywords: List of keywords to search for.
            match_all: If True, all keywords must match; if False, any keyword matches.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If keywords list is empty.
        """
        if not keywords or not isinstance(keywords, list):
            raise ValueError("Keywords must be a non-empty list")
        def _filter(entry: LogEntry) -> bool:
            if not entry.message:
                return False
            msg = entry.message.lower()
            matches = [kw.lower() in msg for kw in keywords if kw]
            if match_all:
                return all(matches)
            return any(matches)
        self._filters.append(_filter)
        return self
