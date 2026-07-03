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
        """Remove duplicates, return unique entries and counts."""
        if not entries:
            return [], {}
        unique = []
        counts: Dict[str, int] = defaultdict(int)

        for entry in entries:
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
        """Get a summary of deduplication statistics."""
        total = sum(self._seen.values())
        unique = len(self._seen)
        duplicates = total - unique
        return {
            "total_processed": total,
            "unique_entries": unique,
            "duplicates_found": duplicates,
            "dedup_rate": round(duplicates / total * 100, 2) if total > 0 else 0,
        }
