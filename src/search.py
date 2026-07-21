"""Full-text search indexing for log entries."""

import re
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional

from .models import LogEntry


class LogSearchIndex:
    """In-memory full-text search index for log entries."""

    STOP_WORDS = {
        "the", "a", "an", "is", "in", "at", "of", "to", "for", "and", "or", "but",
        "it", "its", "be", "was", "were", "been", "are", "have", "has", "had", "do",
        "does", "did", "will", "would", "could", "should", "may", "might", "can",
        "this", "that", "these", "those", "not", "no", "nor", "so", "if", "then",
        "than", "too", "very", "just", "about", "above", "after", "before", "between",
    }

    def __init__(self):
        self._index: Dict[str, Set[int]] = defaultdict(set)
        self._entries: List[LogEntry] = []
        self._field_index: Dict[str, Dict[str, Set[int]]] = {
            "level": defaultdict(set),
            "source": defaultdict(set),
        }

    def __len__(self) -> int:
        """Get the number of indexed entries."""
        return len(self._entries)

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
        """Full-text search across indexed entries.

        Args:
            query: Search query string.
            limit: Maximum number of results to return.

        Returns:
            List of matching LogEntry objects.
        """
        if not query or not isinstance(query, str) or not query.strip():
            return []
        if limit < 1:
            return []
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

    def search_regex(self, pattern: str, limit: int = 100, case_sensitive: bool = False) -> List[LogEntry]:
        """Search using regex pattern.

        Args:
            pattern: Regular expression pattern to search for.
            limit: Maximum number of results to return.
            case_sensitive: Whether the search is case-sensitive.

        Returns:
            List of matching LogEntry objects.

        Raises:
            ValueError: If pattern is invalid.
        """
        if not pattern or not isinstance(pattern, str):
            return []
        if limit < 1:
            return []
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            compiled = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        results = []
        for entry in self._entries:
            if entry.message and compiled.search(entry.message):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def suggest(self, prefix: str, limit: int = 10) -> List[str]:
        """Suggest completions for a search prefix."""
        if not prefix:
            return []
        if limit < 1:
            return []
        prefix = prefix.lower()
        return sorted([word for word in self._index if word.startswith(prefix)])[:limit]

    def search_count(self, query: str) -> int:
        """Count matching entries without returning them.

        Args:
            query: Search query string.

        Returns:
            Number of entries matching the query.
        """
        words = self._tokenize(query)
        if not words:
            return 0
        matching_sets = []
        for w in words:
            s = self._index.get(w)
            if not s:
                return 0
            matching_sets.append(s)
        matching_indices = matching_sets[0]
        for s in matching_sets[1:]:
            matching_indices = matching_indices.intersection(s)
        return len(matching_indices)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable words."""
        if not text or not isinstance(text, str):
            return []
        text = re.sub(r"[^\w\s]", " ", text.lower())
        words = text.split()
        return [w for w in words if w not in self.STOP_WORDS and len(w) > 1]

    @property
    def stats(self) -> Dict[str, int]:
        """Get index statistics."""
        total_words = sum(len(indices) for indices in self._index.values())
        return {
            "entries": len(self._entries),
            "unique_words": len(self._index),
            "total_word_occurrences": total_words,
        }

    def entry_exists(self, entry: LogEntry) -> bool:
        """Check if an entry is already indexed."""
        return entry in self._entries

    @property
    def entry_count(self) -> int:
        """Get the number of indexed entries."""
        return len(self._entries)

    def remove(self, entry: LogEntry) -> bool:
        """Remove an entry from the index.

        Args:
            entry: The entry to remove.

        Returns:
            True if entry was found and removed, False otherwise.
        """
        try:
            idx = self._entries.index(entry)
            self._entries.pop(idx)
            # Rebuild index to maintain consistency
            old_index = self._index
            old_field_index = self._field_index
            self._index = defaultdict(set)
            self._field_index = {
                "level": defaultdict(set),
                "source": defaultdict(set),
            }
            for i, e in enumerate(self._entries):
                words = self._tokenize(e.message)
                for word in words:
                    self._index[word].add(i)
                self._field_index["level"][e.level.value].add(i)
                if e.source:
                    self._field_index["source"][e.source.lower()].add(i)
            return True
        except ValueError:
            return False

    def suggest_with_count(self, prefix: str, limit: int = 10) -> List[Tuple[str, int]]:
        """Suggest completions with occurrence counts.

        Args:
            prefix: Prefix to search for.
            limit: Maximum number of suggestions.

        Returns:
            List of (word, count) tuples sorted by count descending.
        """
        if not prefix:
            return []
        if limit < 1:
            return []
        prefix = prefix.lower()
        matches = [(word, len(indices)) for word, indices in self._index.items()
                   if word.startswith(prefix)]
        return sorted(matches, key=lambda x: x[1], reverse=True)[:limit]

    def clear(self):
        """Clear the entire search index."""
        self._index.clear()
        self._entries.clear()
        self._field_index["level"].clear()
        self._field_index["source"].clear()

    def get_word_frequency(self, word: str) -> int:
        """Get frequency of a specific word in the index.

        Args:
            word: Word to look up.

        Returns:
            Number of entries containing the word.
        """
        if not word:
            return 0
        return len(self._index.get(word.lower(), set()))

    def get_indexed_words(self) -> List[str]:
        """Get all indexed words.

        Returns:
            List of unique indexed words.
        """
        return list(self._index.keys())

    def get_entries_by_level(self, level: str) -> List[LogEntry]:
        """Get all entries of a specific level.

        Args:
            level: Level string (e.g., "ERROR", "INFO").

        Returns:
            List of entries matching the level.
        """
        indices = self._field_index["level"].get(level.upper(), set())
        return [self._entries[i] for i in sorted(indices)]

    def get_entries_by_source(self, source: str) -> List[LogEntry]:
        """Get all entries from a specific source.

        Args:
            source: Source name.

        Returns:
            List of entries from the source.
        """
        if not source:
            return []
        indices = self._field_index["source"].get(source.lower(), set())
        return [self._entries[i] for i in sorted(indices)]

    def get_unique_sources(self) -> List[str]:
        """Get list of unique sources in the index.

        Returns:
            List of source names.
        """
        return list(self._field_index["source"].keys())

    def get_unique_levels(self) -> List[str]:
        """Get list of unique levels in the index.

        Returns:
            List of level strings.
        """
        return list(self._field_index["level"].keys())

    def has_entries(self) -> bool:
        """Check if index has any entries.

        Returns:
            True if entries exist.
        """
        return len(self._entries) > 0

    def has_words(self) -> bool:
        """Check if index has any words.

        Returns:
            True if words are indexed.
        """
        return len(self._index) > 0

    def get_word_count(self) -> int:
        """Get number of unique words in index.

        Returns:
            Count of unique words.
        """
        return len(self._index)

    def has_level(self, level: str) -> bool:
        """Check if level exists in index.

        Args:
            level: Level string to check.

        Returns:
            True if level exists.
        """
        return level.upper() in self._field_index["level"]

    def has_source(self, source: str) -> bool:
        """Check if source exists in index.

        Args:
            source: Source name to check.

        Returns:
            True if source exists.
        """
        if not source:
            return False
        return source.lower() in self._field_index["source"]

    def get_entries_dict(self) -> List[Dict[str, Any]]:
        """Get all entries as dictionaries.

        Returns:
            List of entry dictionaries.
        """
        return [e.to_dict() for e in self._entries]

    def get_source_count(self) -> int:
        """Get number of unique sources.

        Returns:
            Count of sources.
        """
        return len(self._field_index["source"])

    def get_level_count(self) -> int:
        """Get number of unique levels.

        Returns:
            Count of levels.
        """
        return len(self._field_index["level"])

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get search index statistics as dictionary.

        Returns:
            Dictionary with search stats.
        """
        return {
            "entries": len(self._entries),
            "words": len(self._index),
            "sources": len(self._field_index["source"]),
            "levels": len(self._field_index["level"]),
        }

    def get_summary_string(self) -> str:
        """Get a formatted summary string.

        Returns:
            Formatted summary string.
        """
        return (
            f"Entries: {len(self._entries)}, "
            f"Words: {len(self._index)}, "
            f"Sources: {len(self._field_index['source'])}"
        )

    def get_level_counts(self) -> Dict[str, int]:
        """Get counts per level.

        Returns:
            Dictionary mapping level names to counts.
        """
        return {level: len(indices) for level, indices in self._field_index["level"].items()}

    def get_source_counts(self) -> Dict[str, int]:
        """Get counts per source.

        Returns:
            Dictionary mapping source names to counts.
        """
        return {source: len(indices) for source, indices in self._field_index["source"].items()}

    def get_level_distribution(self) -> Dict[str, float]:
        """Get level distribution as percentages.

        Returns:
            Dictionary mapping level names to percentages.
        """
        if not self._entries:
            return {}
        total = len(self._entries)
        counts = self.get_level_counts()
        return {level: round(count / total * 100, 2) for level, count in counts.items()}

    def get_source_distribution(self) -> Dict[str, float]:
        """Get source distribution as percentages.

        Returns:
            Dictionary mapping source names to percentages.
        """
        if not self._entries:
            return {}
        total = len(self._entries)
        counts = self.get_source_counts()
        return {source: round(count / total * 100, 2) for source, count in counts.items()}

    def get_most_common_level(self) -> Optional[str]:
        """Get the most common level in index.

        Returns:
            Most common level string, or None.
        """
        counts = self.get_level_counts()
        if not counts:
            return None
        return max(counts, key=counts.get)

    def get_most_common_source(self) -> Optional[str]:
        """Get the most common source in index.

        Returns:
            Most common source string, or None.
        """
        counts = self.get_source_counts()
        if not counts:
            return None
        return max(counts, key=counts.get)

    def get_least_common_level(self) -> Optional[str]:
        """Get the least common level in index.

        Returns:
            Least common level string, or None.
        """
        counts = self.get_level_counts()
        if not counts:
            return None
        return min(counts, key=counts.get)

    def get_least_common_source(self) -> Optional[str]:
        """Get the least common source in index.

        Returns:
            Least common source string, or None.
        """
        counts = self.get_source_counts()
        if not counts:
            return None
        return min(counts, key=counts.get)

    def get_average_words_per_entry(self) -> float:
        """Get average words per entry.

        Returns:
            Average words per entry.
        """
        if not self._entries:
            return 0.0
        return round(len(self._index) / len(self._entries), 2)

    def get_index_density(self) -> float:
        """Get index density (words per entry ratio).

        Returns:
            Index density percentage.
        """
        if not self._entries:
            return 0.0
        return round(len(self._index) / len(self._entries) * 100, 2)

    def get_level_counts_formatted(self) -> str:
        """Get formatted level counts string.

        Returns:
            Formatted level counts string.
        """
        counts = self.get_level_counts()
        if not counts:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in counts.items())

    def get_source_counts_formatted(self) -> str:
        """Get formatted source counts string.

        Returns:
            Formatted source counts string.
        """
        counts = self.get_source_counts()
        if not counts:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in counts.items())

    def get_index_size_formatted(self) -> str:
        """Get formatted index size string.

        Returns:
            Formatted index size string.
        """
        return f"{len(self._entries)} entries, {len(self._index)} words"

    def get_average_words_per_entry_formatted(self) -> str:
        """Get formatted average words per entry string.

        Returns:
            Formatted average words string.
        """
        return f"{self.get_average_words_per_entry():.1f} words/entry"

    def get_index_density_formatted(self) -> str:
        """Get formatted index density string.

        Returns:
            Formatted index density string.
        """
        return f"{self.get_index_density():.1f}%"
