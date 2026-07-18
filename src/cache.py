"""Caching layer for log analysis performance optimization."""

import time
import hashlib
import json
import threading
from collections import OrderedDict
from typing import Any, Optional, Callable, Dict
from functools import wraps


class LRUCache:
    """Thread-safe LRU cache implementation."""

    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self._cache: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl  # Time to live in seconds
        self._hits = 0
        self._misses = 0
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() - entry["time"] < self._ttl:
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return entry["value"]
                else:
                    del self._cache[key]
            self._misses += 1
            return None

    def put(self, key: str, value: Any):
        """Put item in cache.

        Args:
            key: Cache key.
            value: Value to cache.
        """
        if not key:
            return
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = {"value": value, "time": time.time()}
            if len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    def invalidate(self, key: str):
        """Remove item from cache."""
        with self._lock:
            self._cache.pop(key, None)

    def invalidate_pattern(self, prefix: str):
        """Remove all cache keys matching a prefix."""
        with self._lock:
            keys_to_remove = [k for k in self._cache if k.startswith(prefix)]
            for key in keys_to_remove:
                del self._cache[key]

    def clear(self):
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()

    def invalidate_keys(self, keys: list):
        """Remove multiple items from cache by key."""
        with self._lock:
            for key in keys:
                self._cache.pop(key, None)

    def reset_stats(self):
        """Reset hit/miss statistics."""
        with self._lock:
            self._hits = 0
            self._misses = 0

    @property
    def size(self) -> int:
        """Get current number of items in cache."""
        with self._lock:
            return len(self._cache)

    @property
    def is_full(self) -> bool:
        """Check if cache has reached maximum size."""
        with self._lock:
            return len(self._cache) >= self._max_size

    @property
    def max_size(self) -> int:
        """Get maximum cache size."""
        return self._max_size

    @property
    def ttl(self) -> int:
        """Get cache TTL in seconds."""
        return self._ttl

    @property
    def hit_rate(self) -> float:
        """Get cache hit rate as percentage."""
        with self._lock:
            total = self._hits + self._misses
            return round(self._hits / total * 100, 2) if total > 0 else 0.0

    @property
    def stats(self) -> Dict[str, int]:
        """Return cache performance statistics."""
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total * 100, 2) if total > 0 else 0,
            }

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple items from cache at once.

        Args:
            keys: List of cache keys to retrieve.

        Returns:
            Dictionary mapping found keys to their values.
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def put_many(self, items: Dict[str, Any]):
        """Put multiple items in cache at once.

        Args:
            items: Dictionary mapping keys to values.
        """
        for key, value in items.items():
            self.put(key, value)


# Global cache instance
_global_cache = LRUCache()


def cached(ttl: int = 300):
    """Decorator to cache function results with TTL in seconds."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key_parts = [func.__module__, func.__name__] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = hashlib.sha256("|".join(key_parts).encode()).hexdigest()

            result = _global_cache.get(cache_key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            _global_cache.put(cache_key, result)
            return result
        return wrapper
    return decorator


class QueryCache:
    """Cache for frequently used search queries."""

    def __init__(self, max_size: int = 500):
        self._cache = LRUCache(max_size=max_size, ttl=600)
        self._popular_queries: Dict[str, int] = {}

    def __repr__(self) -> str:
        return f"QueryCache(queries_cached={self._cache.stats['size']})"

    def __len__(self) -> int:
        """Get number of cached queries."""
        return self._cache.size

    def get_results(self, query: str) -> Optional[list]:
        """Get cached search results.

        Args:
            query: The search query string.

        Returns:
            Cached results if available, None otherwise.
        """
        if not query or not isinstance(query, str):
            return None
        self._popular_queries[query] = self._popular_queries.get(query, 0) + 1
        return self._cache.get(query)

    def store_results(self, query: str, results: list):
        """Cache search results.

        Args:
            query: The search query string.
            results: Results to cache.
        """
        if not query or not isinstance(query, str):
            return
        self._cache.put(query, results)

    def popular_queries(self, limit: int = 10) -> list:
        """Get most popular queries."""
        sorted_queries = sorted(self._popular_queries.items(), key=lambda x: x[1], reverse=True)
        return sorted_queries[:limit]

    def clear(self):
        """Clear all cached queries and statistics."""
        self._cache.clear()
        self._popular_queries.clear()

    def clear_stats(self):
        """Clear only the query popularity statistics."""
        self._popular_queries.clear()

    @property
    def query_count(self) -> int:
        """Get number of unique queries tracked."""
        return len(self._popular_queries)

    def get_popular_query(self, index: int = 0) -> Optional[str]:
        """Get a popular query by rank.

        Args:
            index: Rank index (0 = most popular).

        Returns:
            Query string if found, None otherwise.
        """
        sorted_queries = sorted(self._popular_queries.items(), key=lambda x: x[1], reverse=True)
        if 0 <= index < len(sorted_queries):
            return sorted_queries[index][0]
        return None

    @property
    def hit_rate(self) -> float:
        """Get cache hit rate.

        Returns:
            Hit rate as percentage.
        """
        return self._cache.hit_rate

    def has_results(self, query: str) -> bool:
        """Check if cached results exist for a query.

        Args:
            query: Query string to check.

        Returns:
            True if results are cached.
        """
        if not query:
            return False
        return self._cache.get(query) is not None

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats.
        """
        return {
            "size": self._cache.size,
            "hit_rate": self.hit_rate,
            "query_count": self.query_count,
        }

    def is_empty(self) -> bool:
        """Check if cache is empty.

        Returns:
            True if no queries cached.
        """
        return self._cache.size == 0

    def get_popular_queries_list(self) -> List[str]:
        """Get list of popular queries without counts.

        Returns:
            List of query strings sorted by popularity.
        """
        sorted_queries = sorted(self._popular_queries.items(), key=lambda x: x[1], reverse=True)
        return [q for q, _ in sorted_queries]

    def has_queries(self) -> bool:
        """Check if any queries are tracked.

        Returns:
            True if queries exist.
        """
        return len(self._popular_queries) > 0

    def get_query_count(self) -> int:
        """Get number of unique queries.

        Returns:
            Count of unique queries.
        """
        return len(self._popular_queries)

    def get_most_popular(self) -> Optional[str]:
        """Get the most popular query.

        Returns:
            Most popular query string, or None.
        """
        return self.get_popular_query(0)

    def get_summary_string(self) -> str:
        """Get a formatted summary string.

        Returns:
            Formatted summary string.
        """
        return (
            f"Size: {self._cache.size}, "
            f"Hit Rate: {self.hit_rate:.1f}%, "
            f"Queries: {self.query_count}"
        )

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get cache statistics summary.

        Returns:
            Dictionary with cache stats.
        """
        return {
            "size": self._cache.size,
            "hit_rate": self.hit_rate,
            "queries": self.query_count,
            "is_empty": self.is_empty(),
        }

    def has_popular_queries(self) -> bool:
        """Check if any popular queries exist.

        Returns:
            True if popular queries exist.
        """
        return len(self._popular_queries) > 0
