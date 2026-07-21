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

    def sample(self, n: int = 10) -> List[LogEntry]:
        """Get a sample of N entries evenly distributed.

        Args:
            n: Number of entries to sample.

        Returns:
            List of sampled entries.
        """
        if n < 1 or not self.entries:
            return []
        if n >= len(self.entries):
            return list(self.entries)
        step = len(self.entries) // n
        return [self.entries[i] for i in range(0, len(self.entries), step)][:n]

    @property
    def unique_sources(self) -> List[str]:
        """Get unique sources from entries.

        Returns:
            List of unique source names.
        """
        return list(set(e.source for e in self.entries if e.source))

    def by_source_list(self, sources: List[str]) -> "LogFilter":
        """Filter by multiple sources.

        Args:
            sources: List of source names to match.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If sources list is empty.
        """
        if not sources or not isinstance(sources, list):
            raise ValueError("Sources must be a non-empty list")
        def _filter(entry: LogEntry) -> bool:
            if not entry.source:
                return False
            return any(s.lower() in entry.source.lower() for s in sources if s)
        self._filters.append(_filter)
        return self

    def by_min_severity(self, min_level: LogLevel) -> "LogFilter":
        """Filter by minimum severity level.

        Args:
            min_level: Minimum LogLevel to include.

        Returns:
            Self for method chaining.
        """
        ranks = {
            LogLevel.TRACE: 0,
            LogLevel.DEBUG: 1,
            LogLevel.INFO: 2,
            LogLevel.WARN: 3,
            LogLevel.ERROR: 4,
            LogLevel.CRITICAL: 5,
        }
        min_rank = ranks.get(min_level, 0)
        def _filter(entry: LogEntry) -> bool:
            return ranks.get(entry.level, 0) >= min_rank
        self._filters.append(_filter)
        return self

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

    def by_message_length(self, min_length: int = 0, max_length: int = 0) -> "LogFilter":
        """Filter by message length.

        Args:
            min_length: Minimum message length (0 for no minimum).
            max_length: Maximum message length (0 for no maximum).

        Returns:
            Self for method chaining.
        """
        def _filter(entry: LogEntry) -> bool:
            if not entry.message:
                return False
            length = len(entry.message)
            if min_length and length < min_length:
                return False
            if max_length and length > max_length:
                return False
            return True
        self._filters.append(_filter)
        return self

    def get_filter_count(self) -> int:
        """Get number of active filters.

        Returns:
            Count of filters.
        """
        return len(self._filters)

    def has_filters(self) -> bool:
        """Check if any filters are active.

        Returns:
            True if filters exist.
        """
        return len(self._filters) > 0

    def get_entries_dict(self) -> List[Dict[str, Any]]:
        """Get all entries as dictionaries.

        Returns:
            List of entry dictionaries.
        """
        return [e.to_dict() for e in self.entries]

    def get_entries_str(self) -> List[str]:
        """Get all entries as strings.

        Returns:
            List of entry string representations.
        """
        return [str(e) for e in self.entries]

    def has_level(self, level: LogLevel) -> bool:
        """Check if entries contain a specific level.

        Args:
            level: LogLevel to check.

        Returns:
            True if level exists in entries.
        """
        return any(e.level == level for e in self.entries)

    def get_level_count(self, level: LogLevel) -> int:
        """Count entries of a specific level.

        Args:
            level: LogLevel to count.

        Returns:
            Count of entries with the level.
        """
        return sum(1 for e in self.entries if e.level == level)

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get filter statistics as dictionary.

        Returns:
            Dictionary with filter stats.
        """
        return {
            "entries": self.entry_count,
            "filters": self.get_filter_count(),
            "unique_sources": len(self.unique_sources),
            "has_filters": self.has_filters(),
        }

    def get_summary_string(self) -> str:
        """Get a formatted summary string.

        Returns:
            Formatted summary string.
        """
        return (
            f"Entries: {self.entry_count}, "
            f"Filters: {self.get_filter_count()}, "
            f"Sources: {len(self.unique_sources)}"
        )

    def get_source_counts(self) -> Dict[str, int]:
        """Get counts per source.

        Returns:
            Dictionary mapping source names to counts.
        """
        from collections import Counter
        return dict(Counter(e.source for e in self.entries if e.source))

    def get_level_distribution(self) -> Dict[str, float]:
        """Get level distribution as percentages.

        Returns:
            Dictionary mapping level names to percentages.
        """
        if not self.entries:
            return {}
        total = len(self.entries)
        counts = self.count_by_level()
        return {level: round(count / total * 100, 2) for level, count in counts.items()}

    def get_most_common_level(self) -> Optional[str]:
        """Get the most common log level.

        Returns:
            Most common level string, or None.
        """
        counts = self.count_by_level()
        if not counts:
            return None
        return max(counts, key=counts.get)

    def get_error_rate(self) -> float:
        """Get error rate as percentage.

        Returns:
            Error rate percentage.
        """
        if not self.entries:
            return 0.0
        total = len(self.entries)
        errors = self.get_level_count(LogLevel.ERROR) + self.get_level_count(LogLevel.CRITICAL)
        return round(errors / total * 100, 2)

    def get_least_common_level(self) -> Optional[str]:
        """Get the least common log level.

        Returns:
            Least common level string, or None.
        """
        counts = self.count_by_level()
        if not counts:
            return None
        return min(counts, key=counts.get)

    def get_most_common_source(self) -> Optional[str]:
        """Get the most common source.

        Returns:
            Most common source string, or None.
        """
        counts = self.get_source_counts()
        if not counts:
            return None
        return max(counts, key=counts.get)

    def get_source_distribution(self) -> Dict[str, float]:
        """Get source distribution as percentages.

        Returns:
            Dictionary mapping source names to percentages.
        """
        if not self.entries:
            return {}
        total = len(self.entries)
        counts = self.get_source_counts()
        return {source: round(count / total * 100, 2) for source, count in counts.items()}

    def get_warning_rate(self) -> float:
        """Get warning rate as percentage.

        Returns:
            Warning rate percentage.
        """
        if not self.entries:
            return 0.0
        total = len(self.entries)
        warnings = self.get_level_count(LogLevel.WARN)
        return round(warnings / total * 100, 2)

    def get_info_rate(self) -> float:
        """Get info rate as percentage.

        Returns:
            Info rate percentage.
        """
        if not self.entries:
            return 0.0
        total = len(self.entries)
        infos = self.get_level_count(LogLevel.INFO)
        return round(infos / total * 100, 2)

    def get_debug_rate(self) -> float:
        """Get debug rate as percentage.

        Returns:
            Debug rate percentage.
        """
        if not self.entries:
            return 0.0
        total = len(self.entries)
        debugs = self.get_level_count(LogLevel.DEBUG)
        return round(debugs / total * 100, 2)

    def get_critical_rate(self) -> float:
        """Get critical rate as percentage.

        Returns:
            Critical rate percentage.
        """
        if not self.entries:
            return 0.0
        total = len(self.entries)
        criticals = self.get_level_count(LogLevel.CRITICAL)
        return round(criticals / total * 100, 2)

    def get_non_error_rate(self) -> float:
        """Get non-error rate as percentage.

        Returns:
            Non-error rate percentage.
        """
        if not self.entries:
            return 0.0
        total = len(self.entries)
        errors = self.get_level_count(LogLevel.ERROR) + self.get_level_count(LogLevel.CRITICAL)
        return round((total - errors) / total * 100, 2)

    def get_least_common_source(self) -> Optional[str]:
        """Get the least common source.

        Returns:
            Least common source string, or None.
        """
        counts = self.get_source_counts()
        if not counts:
            return None
        return min(counts, key=counts.get)
