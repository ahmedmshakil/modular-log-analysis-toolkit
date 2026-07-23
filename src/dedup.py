"""Log deduplication by hash comparison."""

import hashlib
from collections import defaultdict
from typing import List, Dict, Tuple

from .models import LogEntry


class LogDeduplicator:
    """Remove duplicate log entries based on content hashing."""

    def __init__(self, ignore_timestamp: bool = True):
        self.ignore_timestamp = ignore_timestamp
        self._seen: Dict[str, int] = {}
        self._hash_cache: Dict[int, str] = {}

    def __repr__(self) -> str:
        return f"LogDeduplicator(seen={len(self._seen)}, ignore_timestamp={self.ignore_timestamp})"

    def __str__(self) -> str:
        total = sum(self._seen.values())
        unique = len(self._seen)
        return f"LogDeduplicator({unique} unique / {total} total entries)"

    def __len__(self) -> int:
        """Get number of unique entries seen."""
        return len(self._seen)

    def __contains__(self, entry: LogEntry) -> bool:
        """Check if an entry has been seen before."""
        if not isinstance(entry, LogEntry):
            return False
        h = self._hash_entry(entry)
        return h in self._seen

    def _hash_entry(self, entry: LogEntry) -> str:
        """Generate hash for a log entry."""
        entry_id = id(entry)
        if entry_id in self._hash_cache:
            return self._hash_cache[entry_id]
        parts = [
            entry.level.value,
            entry.message,
            entry.source or "",
        ]
        if not self.ignore_timestamp:
            parts.append(entry.timestamp.isoformat())
        content = "|".join(parts)
        hash_val = hashlib.md5(content.encode()).hexdigest()
        self._hash_cache[entry_id] = hash_val
        return hash_val

    def deduplicate(self, entries: List[LogEntry]) -> Tuple[List[LogEntry], Dict[str, int]]:
        """Remove duplicates, return unique entries and counts.

        Args:
            entries: List of log entries to deduplicate.

        Returns:
            Tuple of (unique entries, duplicate counts by hash).

        Raises:
            TypeError: If entries is not a list.
        """
        if not entries:
            return [], {}
        if not isinstance(entries, list):
            raise TypeError("entries must be a list")
        unique = []
        counts: Dict[str, int] = defaultdict(int)

        for entry in entries:
            if not isinstance(entry, LogEntry):
                continue
            h = self._hash_entry(entry)
            counts[h] += 1
            if h not in self._seen:
                self._seen[h] = 1
                unique.append(entry)
            else:
                self._seen[h] += 1

        return unique, dict(counts)

    def get_duplicate_summary(self) -> List[Tuple[str, int]]:
        """Get summary of duplicated entries."""
        return [(h, count) for h, count in self._seen.items() if count > 1]

    def total_duplicates_removed(self) -> int:
        """Count total duplicates found."""
        return sum(count - 1 for count in self._seen.values() if count > 1)

    def reset(self):
        """Clear deduplication state."""
        self._seen.clear()
        self._hash_cache.clear()

    def get_summary(self) -> Dict[str, int]:
        """Get a summary of deduplication statistics.

        Returns:
            Dictionary with deduplication statistics.
        """
        total = sum(self._seen.values())
        unique = len(self._seen)
        duplicates = total - unique
        return {
            "total_processed": total,
            "unique_entries": unique,
            "duplicates_found": duplicates,
            "dedup_rate": round(duplicates / total * 100, 2) if total > 0 else 0,
            "hash_cache_size": len(self._hash_cache),
        }

    def has_duplicates(self) -> bool:
        """Check if any duplicates were found.

        Returns:
            True if duplicates exist, False otherwise.
        """
        return any(count > 1 for count in self._seen.values())

    def get_most_duplicated(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get the most frequently duplicated entries.

        Args:
            limit: Maximum number of results.

        Returns:
            List of (hash, count) tuples sorted by count descending.
        """
        duplicates = [(h, count) for h, count in self._seen.items() if count > 1]
        return sorted(duplicates, key=lambda x: x[1], reverse=True)[:limit]

    def clear_hash_cache(self):
        """Clear the hash computation cache."""
        self._hash_cache.clear()

    @property
    def unique_count(self) -> int:
        """Get the number of unique entries seen."""
        return len(self._seen)

    @property
    def total_count(self) -> int:
        """Get the total number of entries processed."""
        return sum(self._seen.values())

    @property
    def duplicate_count(self) -> int:
        """Get the number of entries that have duplicates."""
        return sum(1 for count in self._seen.values() if count > 1)

    @property
    def dedup_rate(self) -> float:
        """Get deduplication rate as percentage.

        Returns:
            Percentage of entries that were duplicates.
        """
        total = self.total_count
        if total == 0:
            return 0.0
        duplicates = self.total_duplicates_removed()
        return round(duplicates / total * 100, 2)

    def get_unique_entries(self) -> List[str]:
        """Get list of unique entry hashes.

        Returns:
            List of hash strings for unique entries.
        """
        return [h for h, count in self._seen.items() if count == 1]

    def is_duplicate(self, entry: LogEntry) -> bool:
        """Check if an entry would be a duplicate.

        Args:
            entry: LogEntry to check.

        Returns:
            True if entry is a duplicate.
        """
        if not isinstance(entry, LogEntry):
            return False
        h = self._hash_entry(entry)
        return h in self._seen and self._seen[h] > 1

    @property
    def cache_size(self) -> int:
        """Get size of hash computation cache.

        Returns:
            Number of cached hashes.
        """
        return len(self._hash_cache)

    def get_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics.

        Returns:
            Dictionary with dedup stats.
        """
        return {
            "unique_count": self.unique_count,
            "total_count": self.total_count,
            "duplicate_count": self.duplicate_count,
            "dedup_rate": self.dedup_rate,
            "cache_size": self.cache_size,
        }

    def has_seen(self, entry: LogEntry) -> bool:
        """Check if an entry has been seen before.

        Args:
            entry: LogEntry to check.

        Returns:
            True if entry was previously seen.
        """
        if not isinstance(entry, LogEntry):
            return False
        h = self._hash_entry(entry)
        return h in self._seen

    def is_empty(self) -> bool:
        """Check if no entries have been processed.

        Returns:
            True if no entries seen.
        """
        return len(self._seen) == 0

    def has_cache(self) -> bool:
        """Check if hash cache has entries.

        Returns:
            True if cache is not empty.
        """
        return len(self._hash_cache) > 0

    def get_seen_hashes(self) -> List[str]:
        """Get all seen hashes.

        Returns:
            List of hash strings.
        """
        return list(self._seen.keys())

    def get_duplicate_hashes(self) -> List[str]:
        """Get hashes that have duplicates.

        Returns:
            List of hash strings with count > 1.
        """
        return [h for h, count in self._seen.items() if count > 1]

    def get_unique_hashes(self) -> List[str]:
        """Get hashes that are unique (count == 1).

        Returns:
            List of unique hash strings.
        """
        return [h for h, count in self._seen.items() if count == 1]

    def get_max_duplicates(self) -> int:
        """Get maximum duplicate count for any entry.

        Returns:
            Maximum duplicate count, or 0 if no entries.
        """
        if not self._seen:
            return 0
        return max(self._seen.values())

    def get_min_duplicates(self) -> int:
        """Get minimum duplicate count for any entry.

        Returns:
            Minimum duplicate count, or 0 if no entries.
        """
        if not self._seen:
            return 0
        return min(self._seen.values())

    def get_summary_string(self) -> str:
        """Get a formatted summary string.

        Returns:
            Formatted summary string.
        """
        return (
            f"Unique: {self.unique_count}, "
            f"Total: {self.total_count}, "
            f"Duplicates: {self.duplicate_count}, "
            f"Rate: {self.dedup_rate:.1f}%"
        )

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get deduplication statistics summary.

        Returns:
            Dictionary with dedup stats.
        """
        return {
            "unique": self.unique_count,
            "total": self.total_count,
            "duplicates": self.duplicate_count,
            "dedup_rate": self.dedup_rate,
            "cache_size": self.cache_size,
        }

    def has_duplicates_found(self) -> bool:
        """Check if any duplicates were found.

        Returns:
            True if duplicates exist.
        """
        return self.duplicate_count > 0

    def get_unique_rate(self) -> float:
        """Get unique rate as percentage.

        Returns:
            Unique rate percentage.
        """
        if self.total_count == 0:
            return 0.0
        return round(self.unique_count / self.total_count * 100, 2)

    def get_duplicate_rate_formatted(self) -> str:
        """Get formatted duplicate rate string.

        Returns:
            Formatted duplicate rate string.
        """
        return f"{self.dedup_rate:.1f}%"

    def get_average_duplicates(self) -> float:
        """Get average duplicate count per entry.

        Returns:
            Average duplicate count.
        """
        if self.unique_count == 0:
            return 0.0
        return round(self.total_count / self.unique_count, 2)

    def has_cache_entries(self) -> bool:
        """Check if hash cache has entries.

        Returns:
            True if cache entries exist.
        """
        return len(self._hash_cache) > 0

    def get_unique_rate_formatted(self) -> str:
        """Get formatted unique rate string.

        Returns:
            Formatted unique rate string.
        """
        return f"{self.get_unique_rate():.1f}%"

    def get_cache_hit_rate(self) -> float:
        """Get hash cache hit rate.

        Returns:
            Cache hit rate percentage.
        """
        if self.total_count == 0:
            return 0.0
        return round(len(self._hash_cache) / self.total_count * 100, 2)

    def get_duplicate_ratio(self) -> float:
        """Get duplicate to unique ratio.

        Returns:
            Duplicate ratio.
        """
        if self.unique_count == 0:
            return 0.0
        return round(self.duplicate_count / self.unique_count, 2)

    def get_savings_rate(self) -> float:
        """Get storage savings rate from deduplication.

        Returns:
            Savings rate percentage.
        """
        if self.total_count == 0:
            return 0.0
        return round(self.total_duplicates_removed() / self.total_count * 100, 2)

    def get_savings_rate_formatted(self) -> str:
        """Get formatted savings rate string.

        Returns:
            Formatted savings rate string.
        """
        return f"{self.get_savings_rate():.1f}%"

    def get_duplicate_ratio_formatted(self) -> str:
        """Get formatted duplicate ratio string.

        Returns:
            Formatted duplicate ratio string.
        """
        return f"{self.get_duplicate_ratio():.2f}"

    def get_cache_hit_rate_formatted(self) -> str:
        """Get formatted cache hit rate string.

        Returns:
            Formatted cache hit rate string.
        """
        return f"{self.get_cache_hit_rate():.1f}%"

    def get_average_duplicates_formatted(self) -> str:
        """Get formatted average duplicates string.

        Returns:
            Formatted average duplicates string.
        """
        return f"{self.get_average_duplicates():.2f}"

    def get_total_duplicates_removed_formatted(self) -> str:
        """Get formatted total duplicates removed string.

        Returns:
            Formatted total duplicates removed string.
        """
        return f"{self.total_duplicates_removed()} duplicates"

    def get_unique_count_formatted(self) -> str:
        """Get formatted unique count string.

        Returns:
            Formatted unique count string.
        """
        return f"{self.unique_count} unique"

    def get_total_count_formatted(self) -> str:
        """Get formatted total count string.

        Returns:
            Formatted total count string.
        """
        return f"{self.total_count} total"

    def get_duplicate_count_formatted(self) -> str:
        """Get formatted duplicate count string.

        Returns:
            Formatted duplicate count string.
        """
        return f"{self.duplicate_count} duplicates"

    def get_cache_size_formatted(self) -> str:
        """Get formatted cache size string.

        Returns:
            Formatted cache size string.
        """
        return f"{self.cache_size} cached"

    def get_max_duplicates_formatted(self) -> str:
        """Get formatted max duplicates string.

        Returns:
            Formatted max duplicates string.
        """
        return f"max: {self.get_max_duplicates()}"

    def get_min_duplicates_formatted(self) -> str:
        """Get formatted min duplicates string.

        Returns:
            Formatted min duplicates string.
        """
        return f"min: {self.get_min_duplicates()}"

    def get_duplicate_hashes_count(self) -> int:
        """Get count of duplicate hashes.

        Returns:
            Count of duplicate hashes.
        """
        return len(self.get_duplicate_hashes())

    def get_unique_hashes_count(self) -> int:
        """Get count of unique hashes.

        Returns:
            Count of unique hashes.
        """
        return len(self.get_unique_hashes())

    def get_duplicate_hashes_count_formatted(self) -> str:
        """Get formatted duplicate hashes count string.

        Returns:
            Formatted duplicate hashes count string.
        """
        return f"{self.get_duplicate_hashes_count()} duplicate hashes"

    def get_unique_hashes_count_formatted(self) -> str:
        """Get formatted unique hashes count string.

        Returns:
            Formatted unique hashes count string.
        """
        return f"{self.get_unique_hashes_count()} unique hashes"

    def get_stats_formatted(self) -> str:
        """Get formatted stats string.

        Returns:
            Formatted stats string.
        """
        return f"Unique: {self.unique_count}, Total: {self.total_count}, Duplicates: {self.duplicate_count}, Rate: {self.dedup_rate:.1f}%"

    def get_duplicate_summary_count(self) -> int:
        """Get count of duplicate summary entries.

        Returns:
            Count of duplicate summary entries.
        """
        return len(self.get_duplicate_summary())

    def get_duplicate_summary_count_formatted(self) -> str:
        """Get formatted duplicate summary count string.

        Returns:
            Formatted duplicate summary count string.
        """
        return f"{self.get_duplicate_summary_count()} summary entries"

    def get_summary_string(self) -> str:
        """Get summary string.

        Returns:
            Summary string.
        """
        return self.get_stats_formatted()

    def get_duplicate_efficiency(self) -> float:
        """Get duplicate efficiency (duplicates found / total processed).

        Returns:
            Duplicate efficiency percentage.
        """
        if self.total_count == 0:
            return 0.0
        return round(self.duplicate_count / self.total_count * 100, 2)

    def get_duplicate_efficiency_formatted(self) -> str:
        """Get formatted duplicate efficiency string.

        Returns:
            Formatted duplicate efficiency string.
        """
        return f"{self.get_duplicate_efficiency():.1f}%"

    def get_hash_cache_efficiency(self) -> float:
        """Get hash cache efficiency (cache size / total count).

        Returns:
            Hash cache efficiency percentage.
        """
        if self.total_count == 0:
            return 0.0
        return round(self.cache_size / self.total_count * 100, 2)

    def get_hash_cache_efficiency_formatted(self) -> str:
        """Get formatted hash cache efficiency string.

        Returns:
            Formatted hash cache efficiency string.
        """
        return f"{self.get_hash_cache_efficiency():.1f}%"

    def get_unique_ratio(self) -> float:
        """Get unique ratio (unique / total).

        Returns:
            Unique ratio percentage.
        """
        if self.total_count == 0:
            return 0.0
        return round(self.unique_count / self.total_count * 100, 2)

    def get_unique_ratio_formatted(self) -> str:
        """Get formatted unique ratio string.

        Returns:
            Formatted unique ratio string.
        """
        return f"{self.get_unique_ratio():.1f}%"
