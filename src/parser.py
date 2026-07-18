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

    def can_parse(self, line: str) -> bool:
        """Check if a line can be parsed by this parser.

        Args:
            line: Log line to check.

        Returns:
            True if the line matches the pattern.
        """
        if not line or not isinstance(line, str):
            return False
        return bool(self.pattern.match(line.strip()))

    def parse_json_line(self, line: str, line_number: int = 0) -> Optional[LogEntry]:
        """Parse a JSON-formatted log line.

        Args:
            line: JSON log line to parse.
            line_number: Line number in the source file.

        Returns:
            LogEntry if parsing succeeds, None otherwise.
        """
        import json
        if not line or not isinstance(line, str):
            return None
        line = line.strip()
        if not line:
            return None
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None

        ts_str = data.get("timestamp", data.get("time", data.get("ts", "")))
        level_str = data.get("level", data.get("severity", data.get("loglevel", "INFO")))
        message = data.get("message", data.get("msg", data.get("text", "")))

        if not message:
            return None

        timestamp = self._parse_timestamp(str(ts_str)) if ts_str else datetime.now()
        level = self._parse_level(str(level_str))

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=str(message),
            source=data.get("source", data.get("host", data.get("logger"))),
            line_number=line_number,
            raw=line,
            metadata={k: v for k, v in data.items()
                     if k not in ("timestamp", "time", "ts", "level", "severity",
                                  "loglevel", "message", "msg", "text", "source",
                                  "host", "logger")},
        )

    def parse_lines_json(self, lines: List[str]) -> List[LogEntry]:
        """Parse multiple JSON log lines.

        Args:
            lines: List of JSON log lines.

        Returns:
            List of parsed LogEntry objects.
        """
        entries = []
        for i, line in enumerate(lines, 1):
            entry = self.parse_json_line(line, line_number=i)
            if entry:
                entries.append(entry)
        return entries

    def get_pattern_name(self) -> str:
        """Get the current pattern name.

        Returns:
            Pattern name string.
        """
        return self.pattern_name

    def has_custom_pattern(self) -> bool:
        """Check if parser uses a custom pattern.

        Returns:
            True if custom pattern is set.
        """
        return self.pattern_name not in PATTERNS

    def get_pattern_count(self) -> int:
        """Get number of available patterns.

        Returns:
            Count of available patterns.
        """
        return len(PATTERNS)

    def is_json_pattern(self) -> bool:
        """Check if parser uses JSON pattern.

        Returns:
            True if using json_log pattern.
        """
        return self.pattern_name == "json_log"

    def get_pattern(self) -> Pattern:
        """Get the compiled pattern.

        Returns:
            Compiled regex pattern.
        """
        return self.pattern

    def is_standard_pattern(self) -> bool:
        """Check if parser uses standard pattern.

        Returns:
            True if using standard pattern.
        """
        return self.pattern_name == "standard"

    def is_syslog_pattern(self) -> bool:
        """Check if parser uses syslog pattern.

        Returns:
            True if using syslog pattern.
        """
        return self.pattern_name == "syslog"

    def is_apache_pattern(self) -> bool:
        """Check if parser uses apache pattern.

        Returns:
            True if using apache pattern.
        """
        return self.pattern_name == "apache"

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get parser statistics as dictionary.

        Returns:
            Dictionary with parser stats.
        """
        return {
            "pattern_name": self.pattern_name,
            "is_custom": self.has_custom_pattern(),
            "available_patterns": self.get_pattern_count(),
        }

    def get_summary_string(self) -> str:
        """Get a formatted summary string.

        Returns:
            Formatted summary string.
        """
        return f"Pattern: {self.pattern_name}, Custom: {self.has_custom_pattern()}"

    def get_available_patterns_list(self) -> List[str]:
        """Get list of available pattern names.

        Returns:
            List of pattern name strings.
        """
        return list(PATTERNS.keys())
