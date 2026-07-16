"""IP geolocation lookup for network log entries."""

import re
import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class GeoLocation:
    """Geolocation data for an IP address."""
    ip: str
    country: str = ""
    city: str = ""
    region: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    org: str = ""
    timezone: str = ""

    def __str__(self) -> str:
        parts = [self.ip]
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        return " - ".join(parts)

    def to_dict(self) -> Dict:
        return {
            "ip": self.ip,
            "country": self.country,
            "city": self.city,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "org": self.org,
            "timezone": self.timezone,
        }


class GeoLookup:
    """Look up geolocation data for IP addresses found in logs."""

    IP_PATTERN = re.compile(r"\b((?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?))\b")

    def __init__(self, cache_size: int = 1000):
        self._cache: Dict[str, GeoLocation] = {}
        self._cache_size = cache_size
        self._lookup_count = 0
        self._cache_hits = 0

    def __repr__(self) -> str:
        return f"GeoLookup(cached={len(self._cache)}, lookups={self._lookup_count})"

    def __str__(self) -> str:
        return f"GeoLookup({len(self._cache)} cached IPs, {self._lookup_count} lookups)"

    def extract_ips(self, text: str) -> List[str]:
        """Extract IP addresses from text."""
        return self.IP_PATTERN.findall(text)

    def lookup(self, ip: str) -> Optional[GeoLocation]:
        """Look up geolocation for a single IP.

        Args:
            ip: IP address to look up.

        Returns:
            GeoLocation if found, None otherwise.
        """
        if not ip or not isinstance(ip, str):
            return None
        if not self.IP_PATTERN.match(ip):
            return None
        if ip in self._cache:
            self._cache_hits += 1
            return self._cache[ip]

        self._lookup_count += 1
        geo = self._fetch_geo(ip)
        if geo:
            if len(self._cache) < self._cache_size:
                self._cache[ip] = geo
        return geo

    def lookup_batch(self, ips: List[str]) -> Dict[str, Optional[GeoLocation]]:
        """Look up multiple IPs."""
        results = {}
        for ip in ips:
            results[ip] = self.lookup(ip)
        return results

    def _fetch_geo(self, ip: str) -> Optional[GeoLocation]:
        """Fetch geolocation from free API."""
        try:
            url = f"http://ip-api.com/json/{ip}"
            req = urllib.request.Request(url, headers={"User-Agent": "modular-log-analysis-toolkit"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "success":
                    return GeoLocation(
                        ip=ip,
                        country=data.get("country", ""),
                        city=data.get("city", ""),
                        region=data.get("regionName", ""),
                        latitude=data.get("lat", 0.0),
                        longitude=data.get("lon", 0.0),
                        org=data.get("org", ""),
                        timezone=data.get("timezone", ""),
                    )
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            pass
        except (json.JSONDecodeError, KeyError) as e:
            pass
        return None

    def enrich_entry(self, message: str) -> List[Dict]:
        """Extract and look up all IPs in a message.

        Args:
            message: Log message to extract IPs from.

        Returns:
            List of geolocation dictionaries for found IPs.
        """
        if not message or not isinstance(message, str):
            return []
        ips = self.extract_ips(message)
        results = []
        for ip in ips:
            geo = self.lookup(ip)
            if geo:
                results.append(geo.to_dict())
        return results

    @property
    def stats(self) -> Dict[str, Any]:
        """Get lookup statistics.

        Returns:
            Dictionary with lookup stats including hit rate.
        """
        total = self._lookup_count + self._cache_hits
        return {
            "lookups": self._lookup_count,
            "cache_hits": self._cache_hits,
            "cached": len(self._cache),
            "hit_rate": round(self._cache_hits / total * 100, 2) if total > 0 else 0.0,
        }

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate as percentage.

        Returns:
            Cache hit rate as a float between 0 and 100.
        """
        total = self._lookup_count + self._cache_hits
        if total == 0:
            return 0.0
        return round(self._cache_hits / total * 100, 2)

    def reset_stats(self):
        """Reset lookup statistics."""
        self._lookup_count = 0
        self._cache_hits = 0

    def clear_cache(self):
        """Clear the geolocation cache."""
        self._cache.clear()
        self._lookup_count = 0
        self._cache_hits = 0

    def cache_size(self) -> int:
        """Get number of entries in cache."""
        return len(self._cache)

    def is_cached(self, ip: str) -> bool:
        """Check if an IP is already cached.

        Args:
            ip: IP address to check.

        Returns:
            True if IP is in cache, False otherwise.
        """
        return ip in self._cache

    def get_cached_ips(self) -> List[str]:
        """Get list of all cached IP addresses.

        Returns:
            List of IP address strings.
        """
        return list(self._cache.keys())

    def remove_from_cache(self, ip: str) -> bool:
        """Remove a specific IP from cache.

        Args:
            ip: IP address to remove.

        Returns:
            True if IP was removed, False if not found.
        """
        if ip in self._cache:
            del self._cache[ip]
            return True
        return False

    @property
    def cache_size(self) -> int:
        """Get number of entries in cache.

        Returns:
            Number of cached entries.
        """
        return len(self._cache)

    def extract_ips_from_entries(self, entries: List) -> List[str]:
        """Extract unique IPs from a list of log entries.

        Args:
            entries: List of LogEntry objects.

        Returns:
            List of unique IP addresses found.
        """
        ips = set()
        for entry in entries:
            if entry.message:
                ips.update(self.extract_ips(entry.message))
        return list(ips)

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get summary of lookup statistics.

        Returns:
            Dictionary with lookup stats.
        """
        return {
            "lookups": self._lookup_count,
            "cache_hits": self._cache_hits,
            "cached": len(self._cache),
            "hit_rate": self.cache_hit_rate,
        }

    def has_cached(self, ip: str) -> bool:
        """Check if IP is in cache (alias for is_cached).

        Args:
            ip: IP address to check.

        Returns:
            True if cached.
        """
        return ip in self._cache

    def is_cache_full(self) -> bool:
        """Check if cache has reached maximum size.

        Returns:
            True if cache is full.
        """
        return len(self._cache) >= self._cache_size

    def get_cache_capacity(self) -> int:
        """Get maximum cache capacity.

        Returns:
            Maximum cache size.
        """
        return self._cache_size

    def has_lookups(self) -> bool:
        """Check if any lookups have been performed.

        Returns:
            True if lookups exist.
        """
        return self._lookup_count > 0 or self._cache_hits > 0

    def get_lookup_count(self) -> int:
        """Get number of API lookups performed.

        Returns:
            Lookup count.
        """
        return self._lookup_count

    def get_cache_hits(self) -> int:
        """Get number of cache hits.

        Returns:
            Cache hit count.
        """
        return self._cache_hits
