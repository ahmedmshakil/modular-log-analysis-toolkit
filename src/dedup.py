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
