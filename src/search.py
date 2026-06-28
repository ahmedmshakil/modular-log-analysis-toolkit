"""Full-text search indexing for log entries."""

import re
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional

from .models import LogEntry


class LogSearchIndex:
    """In-memory full-text search index for log entries."""

    def __init__(self):
        self._index: Dict[str, Set[int]] = defaultdict(set)
        self._entries: List[LogEntry] = []
        self._field_index: Dict[str, Dict[str, Set[int]]] = {
            "level": defaultdict(set),
            "source": defaultdict(set),
        }

    def add(self, entry: LogEntry):
        """Add an entry to the index."""
        idx = len(self._entries)
        self._entries.append(entry)

        # Index words from message
        words = self._tokenize(entry.message)
        for word in words:
            self._index[word].add(idx)

        # Index fields
        self._field_index["level"][entry.level.value].add(idx)
        if entry.source:
            self._field_index["source"][entry.source.lower()].add(idx)

    def add_batch(self, entries: List[LogEntry]):
        """Add multiple entries to the index."""
        for entry in entries:
            self.add(entry)

    def search(self, query: str, limit: int = 100) -> List[LogEntry]:
        """Full-text search across indexed entries."""
        words = self._tokenize(query)
        if not words:
            return []

        # Find entries matching ALL words
        matching_sets = [self._index.get(w, set()) for w in words]
        if not all(matching_sets):
            return []

        matching_indices = matching_sets[0]
        for s in matching_sets[1:]:
            matching_indices = matching_indices.intersection(s)

        results = [self._entries[i] for i in sorted(matching_indices)]
        return results[:limit]

    def search_field(self, field: str, value: str) -> List[LogEntry]:
        """Search by specific field value."""
        if field in self._field_index:
            indices = self._field_index[field].get(value.lower(), set())
            return [self._entries[i] for i in sorted(indices)]
        return []

    def search_regex(self, pattern: str, limit: int = 100) -> List[LogEntry]:
        """Search using regex pattern."""
        compiled = re.compile(pattern, re.IGNORECASE)
        results = []
        for entry in self._entries:
            if compiled.search(entry.message):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def suggest(self, prefix: str, limit: int = 10) -> List[str]:
        """Suggest completions for a search prefix."""
        prefix = prefix.lower()
        return sorted([word for word in self._index if word.startswith(prefix)])[:limit]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable words."""
        text = re.sub(r"[^\w\s]", " ", text.lower())
        words = text.split()
        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "in", "at", "of", "to", "for"}
        return [w for w in words if w not in stop_words and len(w) > 1]

    @property
    def stats(self) -> Dict[str, int]:
        """Get index statistics."""
        total_words = sum(len(indices) for indices in self._index.values())
        return {
            "entries": len(self._entries),
            "unique_words": len(self._index),
            "total_word_occurrences": total_words,
        }
