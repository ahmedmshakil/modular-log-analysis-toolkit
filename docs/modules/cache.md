# Cache Module

The `cache` module provides caching capabilities for performance optimization.

## Table of Contents

- [Overview](#overview)
- [LRUCache Class](#lrucache-class)
- [QueryCache Class](#querycache-class)
- [cached Decorator](#cached-decorator)
- [Usage Examples](#usage-examples)

## Overview

The cache module provides:

- **LRUCache** - Thread-safe LRU cache with TTL
- **QueryCache** - Cache for search queries
- **cached** - Decorator for function result caching

## LRUCache Class

Thread-safe LRU cache implementation.

### Constructor

```python
LRUCache(max_size: int = 1000, ttl: int = 300)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_size` | `int` | `1000` | Maximum cache size |
| `ttl` | `int` | `300` | Time to live in seconds |

### Methods

#### get

```python
get(key: str) -> Optional[Any]
```

Get item from cache.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `str` | Cache key |

**Returns:** `Optional[Any]` - Cached value or None

**Example:**

```python
cache = LRUCache()
cache.put("key", "value")
result = cache.get("key")  # "value"
result = cache.get("missing")  # None
```

#### put

```python
put(key: str, value: Any) -> None
```

Put item in cache.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `str` | Cache key |
| `value` | `Any` | Value to cache |

**Example:**

```python
cache.put("key", "value")
```

#### invalidate

```python
invalidate(key: str) -> None
```

Remove item from cache.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `str` | Cache key |

**Example:**

```python
cache.invalidate("key")
```

#### invalidate_pattern

```python
invalidate_pattern(prefix: str) -> None
```

Remove all cache keys matching a prefix.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `prefix` | `str` | Key prefix |

**Example:**

```python
cache.invalidate_pattern("user_")
```

#### clear

```python
clear() -> None
```

Clear all cached items.

**Example:**

```python
cache.clear()
```

#### invalidate_keys

```python
invalidate_keys(keys: list) -> None
```

Remove multiple items from cache by key.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `keys` | `list` | List of keys |

**Example:**

```python
cache.invalidate_keys(["key1", "key2"])
```

#### reset_stats

```python
reset_stats() -> None
```

Reset hit/miss statistics.

**Example:**

```python
cache.reset_stats()
```

#### Properties

##### stats

```python
@property
stats -> Dict[str, int]
```

Return cache performance statistics.

**Returns:** `Dict[str, int]` - Statistics including:
- `size` - Current cache size
- `hits` - Number of cache hits
- `misses` - Number of cache misses
- `hit_rate` - Hit rate percentage

**Example:**

```python
stats = cache.stats
print(f"Size: {stats['size']}")
print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate']}%")
```

##### hit_rate

```python
@property
hit_rate -> float
```

Get cache hit rate as percentage.

**Example:**

```python
print(f"Hit rate: {cache.hit_rate}%")
```

## QueryCache Class

Cache for frequently used search queries.

### Constructor

```python
QueryCache(max_size: int = 500)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_size` | `int` | `500` | Maximum cache size |

### Methods

#### get_results

```python
get_results(query: str) -> Optional[list]
```

Get cached search results.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search query |

**Returns:** `Optional[list]` - Cached results or None

**Example:**

```python
cache = QueryCache()
results = cache.get_results("database error")
```

#### store_results

```python
store_results(query: str, results: list) -> None
```

Cache search results.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search query |
| `results` | `list` | Search results |

**Example:**

```python
cache.store_results("database error", results)
```

#### popular_queries

```python
popular_queries(limit: int = 10) -> list
```

Get most popular queries.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `10` | Maximum queries |

**Returns:** `list` - List of (query, count) tuples

**Example:**

```python
popular = cache.popular_queries(limit=5)
for query, count in popular:
    print(f"{query}: {count} times")
```

#### clear

```python
clear() -> None
```

Clear all cached queries and statistics.

**Example:**

```python
cache.clear()
```

### Special Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |

## cached Decorator

Decorator to cache function results with TTL.

### Usage

```python
from src.cache import cached

@cached(ttl=600)
def expensive_function(arg):
    # Complex computation
    return result
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ttl` | `int` | `300` | Time to live in seconds |

## Usage Examples

### Basic Cache

```python
from src.cache import LRUCache

cache = LRUCache(max_size=1000, ttl=300)

# Put and get
cache.put("key", "value")
result = cache.get("key")

# Check existence
if cache.get("key") is not None:
    print("Found in cache")

# Invalidate
cache.invalidate("key")

# Clear all
cache.clear()
```

### Cache Statistics

```python
# Use cache
cache.put("key1", "value1")
cache.get("key1")  # Hit
cache.get("key2")  # Miss

# Get statistics
stats = cache.stats
print(f"Size: {stats['size']}")
print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate']}%")

# Direct hit rate
print(f"Hit rate: {cache.hit_rate}%")

# Reset statistics
cache.reset_stats()
```

### Pattern Invalidation

```python
# Cache multiple items
cache.put("user_1", data1)
cache.put("user_2", data2)
cache.put("user_3", data3)

# Invalidate by prefix
cache.invalidate_pattern("user_")

# All user_ keys removed
print(cache.get("user_1"))  # None
```

### Query Cache

```python
from src.cache import QueryCache

cache = QueryCache(max_size=500)

# Store results
cache.store_results("database error", results)
cache.store_results("timeout", timeout_results)

# Get results
cached_results = cache.get_results("database error")

# Get popular queries
popular = cache.popular_queries(limit=5)
for query, count in popular:
    print(f"{query}: {count} times")

# Clear
cache.clear()
```

### Cached Decorator

```python
from src.cache import cached

@cached(ttl=600)
def expensive_computation(x, y):
    # Simulate expensive work
    import time
    time.sleep(2)
    return x + y

# First call - slow
result1 = expensive_computation(1, 2)  # Takes 2 seconds

# Second call - fast (cached)
result2 = expensive_computation(1, 2)  # Instant
```

### Thread Safety

```python
import threading
from src.cache import LRUCache

cache = LRUCache()

def worker(thread_id):
    for i in range(100):
        key = f"thread_{thread_id}_item_{i}"
        cache.put(key, f"value_{i}")
        cache.get(key)

threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Cache size: {cache.stats['size']}")
```

## See Also

- [Search](search.md) - Search query caching
