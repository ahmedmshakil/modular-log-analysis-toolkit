"""Log parsing engine with pattern matching support."""

import re
from datetime import datetime
from typing import Optional, List, Pattern

from .models import LogEntry, LogLevel


# Common log format patterns
PATTERNS = {
    "syslog": re.compile(
        r"(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"
        r"(?P<host>\S+)\s+(?P<program>\S+?)(?:\[(?P<pid>\d+)\])?:\s+"
        r"(?P<message>.*)"
    ),
    "apache": re.compile(
        r"(?P<ip>\S+)\s+\S+\s+\S+\s+"
        r"\[(?P<timestamp>[^\]]+)\]\s+"
        r'"(?P<request>[^"]*)"\s+(?P<status>\d+)\s+(?P<size>\S+)'
    ),
    "json_log": re.compile(r"^\{.*\}$"),
    "standard": re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+"
        r"\[(?P<level>\w+)\]\s+(?P<message>.*)"
    ),
}


class LogParser:
    """Parse log lines into structured LogEntry objects."""

    DEFAULT_TIMESTAMP_FORMATS = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%d/%b/%Y:%H:%M:%S",
        "%b %d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
    ]

    def __init__(self, pattern_name: str = "standard", custom_pattern: Optional[str] = None):
        if custom_pattern:
            if not isinstance(custom_pattern, str):
                raise TypeError("custom_pattern must be a string")
            try:
                self.pattern: Pattern = re.compile(custom_pattern)
            except re.error as e:
                raise ValueError(f"Invalid custom pattern: {e}")
        elif pattern_name in PATTERNS:
            self.pattern = PATTERNS[pattern_name]
        else:
            available = ", ".join(PATTERNS.keys())
            raise ValueError(f"Unknown pattern: {pattern_name}. Available patterns: {available}")
        self.pattern_name = pattern_name

    def __repr__(self) -> str:
        return f"LogParser(pattern={self.pattern_name!r})"

    def __str__(self) -> str:
        return f"LogParser(pattern='{self.pattern_name}')"

    def parse_line(self, line: str, line_number: int = 0) -> Optional[LogEntry]:
        """Parse a single log line.

        Args:
            line: The log line to parse.
            line_number: Line number in the source file.

        Returns:
            LogEntry if parsing succeeds, None otherwise.
        """
        if not line or not isinstance(line, str):
            return None
        line = line.strip()
        if not line:
            return None
        match = self.pattern.match(line)
        if not match:
            return None

        groups = match.groupdict()
        timestamp = self._parse_timestamp(groups.get("timestamp", ""))
        level = self._parse_level(groups.get("level", "INFO"))
        message = groups.get("message", line)

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=groups.get("host") or groups.get("program"),
            line_number=line_number,
            raw=line,
        )

    def parse_lines(self, lines: List[str]) -> List[LogEntry]:
        """Parse multiple log lines."""
        entries = []
        for i, line in enumerate(lines, 1):
            entry = self.parse_line(line, line_number=i)
            if entry:
                entries.append(entry)
        return entries

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Try multiple timestamp formats.

        Args:
            ts_str: Timestamp string to parse.

        Returns:
            Parsed datetime, or current time if no format matches.
        """
        if not ts_str or not isinstance(ts_str, str):
            return datetime.now()
        ts_str = ts_str.strip()
        if not ts_str:
            return datetime.now()
        for fmt in self.DEFAULT_TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        return datetime.now()

    def _parse_level(self, level_str: str) -> LogLevel:
        """Parse log level string."""
        mapping = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARN": LogLevel.WARN,
            "WARNING": LogLevel.WARN,
            "ERROR": LogLevel.ERROR,
            "ERR": LogLevel.ERROR,
            "CRITICAL": LogLevel.CRITICAL,
            "FATAL": LogLevel.CRITICAL,
            "TRACE": LogLevel.TRACE,
        }
        return mapping.get(level_str.upper(), LogLevel.INFO)

    @staticmethod
    def available_patterns() -> List[str]:
        """Get list of available pattern names.

        Returns:
            List of pattern names.
        """
        return list(PATTERNS.keys())
