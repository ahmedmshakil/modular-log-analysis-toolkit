"""Caching layer for log analysis performance optimization."""

import time
import hashlib
import json
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

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
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
        """Put item in cache."""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = {"value": value, "time": time.time()}
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def invalidate(self, key: str):
        """Remove item from cache."""
        self._cache.pop(key, None)

    def invalidate_pattern(self, prefix: str):
        """Remove all cache keys matching a prefix."""
        keys_to_remove = [k for k in self._cache if k.startswith(prefix)]
        for key in keys_to_remove:
            del self._cache[key]

    def clear(self):
        """Clear all cached items."""
        self._cache.clear()

    @property
    def stats(self) -> Dict[str, int]:
        """Return cache performance statistics."""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total * 100, 2) if total > 0 else 0,
        }


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

    def get_results(self, query: str) -> Optional[list]:
        """Get cached search results."""
        self._popular_queries[query] = self._popular_queries.get(query, 0) + 1
        return self._cache.get(query)

    def store_results(self, query: str, results: list):
        """Cache search results."""
        self._cache.put(query, results)

    def popular_queries(self, limit: int = 10) -> list:
        """Get most popular queries."""
        sorted_queries = sorted(self._popular_queries.items(), key=lambda x: x[1], reverse=True)
        return sorted_queries[:limit]
