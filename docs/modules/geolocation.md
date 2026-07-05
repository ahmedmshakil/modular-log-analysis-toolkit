# Geolocation Module

The `geolocation` module provides IP address geolocation lookup for network log entries.

## Table of Contents

- [Overview](#overview)
- [GeoLocation Class](#geolocation-class)
- [GeoLookup Class](#geolookup-class)
- [Usage Examples](#usage-examples)

## Overview

The geolocation module provides:

- **GeoLocation** - Data class for location information
- **GeoLookup** - IP address lookup with caching
- **IP extraction** - Extract IPs from log messages
- **Batch lookup** - Look up multiple IPs at once

## GeoLocation Class

Geolocation data for an IP address.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ip` | `str` | required | IP address |
| `country` | `str` | `""` | Country name |
| `city` | `str` | `""` | City name |
| `region` | `str` | `""` | Region/state |
| `latitude` | `float` | `0.0` | Latitude |
| `longitude` | `float` | `0.0` | Longitude |
| `org` | `str` | `""` | Organization |
| `timezone` | `str` | `""` | Timezone |

### Methods

| Method | Description |
|--------|-------------|
| `__str__()` | Human-readable string |
| `to_dict()` | Convert to dictionary |

## GeoLookup Class

Look up geolocation data for IP addresses found in logs.

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `IP_PATTERN` | `Pattern` | Regex pattern for IP extraction |

### Constructor

```python
GeoLookup(cache_size: int = 1000)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cache_size` | `int` | `1000` | Maximum cache size |

### Methods

#### extract_ips

```python
extract_ips(text: str) -> List[str]
```

Extract IP addresses from text.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Text to extract IPs from |

**Returns:** `List[str]` - List of IP addresses

**Example:**

```python
geo = GeoLookup()
ips = geo.extract_ips("Connection from 192.168.1.1 failed")
print(ips)  # ['192.168.1.1']
```

#### lookup

```python
lookup(ip: str) -> Optional[GeoLocation]
```

Look up geolocation for a single IP.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ip` | `str` | IP address |

**Returns:** `Optional[GeoLocation]` - Location data or None

**Example:**

```python
location = geo.lookup("8.8.8.8")
if location:
    print(f"{location.city}, {location.country}")
```

#### lookup_batch

```python
lookup_batch(ips: List[str]) -> Dict[str, Optional[GeoLocation]]
```

Look up multiple IPs.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ips` | `List[str]` | List of IP addresses |

**Returns:** `Dict[str, Optional[GeoLocation]]` - Results per IP

**Example:**

```python
results = geo.lookup_batch(["8.8.8.8", "1.1.1.1"])
for ip, location in results.items():
    if location:
        print(f"{ip}: {location.city}, {location.country}")
```

#### enrich_entry

```python
enrich_entry(message: str) -> List[Dict]
```

Extract and look up all IPs in a message.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Log message |

**Returns:** `List[Dict]` - List of location dictionaries

**Example:**

```python
results = geo.enrich_entry("Connection from 8.8.8.8 and 1.1.1.1")
for r in results:
    print(r)
```

#### clear_cache

```python
clear_cache() -> None
```

Clear the geolocation cache.

**Example:**

```python
geo.clear_cache()
```

#### Properties

##### stats

```python
@property
stats -> Dict[str, int]
```

Get lookup statistics.

**Returns:** `Dict[str, int]` - Statistics including:
- `lookups` - Number of API lookups
- `cache_hits` - Number of cache hits
- `cached` - Number of cached entries

**Example:**

```python
stats = geo.stats
print(f"Lookups: {stats['lookups']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cached: {stats['cached']}")
```

### Special Methods

| Method | Description |
|--------|-------------|
| `__repr__()` | String representation |

## Usage Examples

### Basic Lookup

```python
from src.geolocation import GeoLookup

geo = GeoLookup()

# Single lookup
location = geo.lookup("8.8.8.8")
if location:
    print(f"IP: {location.ip}")
    print(f"City: {location.city}")
    print(f"Country: {location.country}")
    print(f"Organization: {location.org}")
```

### Extract IPs

```python
# Extract IPs from message
message = "Connection from 192.168.1.1 and 10.0.0.1 failed"
ips = geo.extract_ips(message)
print(f"Found IPs: {ips}")
```

### Batch Lookup

```python
# Look up multiple IPs
ips = ["8.8.8.8", "1.1.1.1", "192.168.1.1"]
results = geo.lookup_batch(ips)

for ip, location in results.items():
    if location:
        print(f"{ip}: {location.city}, {location.country}")
    else:
        print(f"{ip}: Not found")
```

### Enrich Log Entries

```python
# Enrich log message with geo data
message = "Failed login from 8.8.8.8"
results = geo.enrich_entry(message)

for r in results:
    print(f"IP: {r['ip']}")
    print(f"Location: {r['city']}, {r['country']}")
```

### Statistics

```python
stats = geo.stats
print(f"Lookups: {stats['lookups']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cached: {stats['cached']}")

# Calculate hit rate
total = stats['lookups'] + stats['cache_hits']
hit_rate = stats['cache_hits'] / total * 100 if total > 0 else 0
print(f"Hit rate: {hit_rate:.1f}%")
```

### Clear Cache

```python
geo.clear_cache()
stats = geo.stats
print(f"Cached after clear: {stats['cached']}")
```

## See Also

- [Models](models.md) - LogEntry structure
