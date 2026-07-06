"""IP geolocation lookup for network log entries."""

import re
import json
import urllib.error
import urllib.request
from typing import Dict, Optional, List
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
    def stats(self) -> Dict[str, int]:
        """Get lookup statistics."""
        return {
            "lookups": self._lookup_count,
            "cache_hits": self._cache_hits,
            "cached": len(self._cache),
        }

    def clear_cache(self):
        """Clear the geolocation cache."""
        self._cache.clear()
        self._lookup_count = 0
        self._cache_hits = 0
