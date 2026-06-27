"""Unit tests for the log parser module."""

import pytest
from datetime import datetime

from src.parser import LogParser
from src.models import LogLevel


class TestLogParser:
    """Test suite for LogParser."""

    def test_parse_standard_log_line(self):
        parser = LogParser(pattern_name="standard")
        line = "2024-01-15 10:30:45 [INFO] Application started successfully"
        entry = parser.parse_line(line, line_number=1)

        assert entry is not None
        assert entry.level == LogLevel.INFO
        assert "Application started" in entry.message
        assert entry.line_number == 1

    def test_parse_error_level(self):
        parser = LogParser(pattern_name="standard")
        line = "2024-01-15 10:30:45 [ERROR] Connection timeout"
        entry = parser.parse_line(line, line_number=1)

        assert entry is not None
        assert entry.level == LogLevel.ERROR

    def test_parse_warn_level(self):
        parser = LogParser(pattern_name="standard")
        line = "2024-01-15 10:30:45 [WARN] High memory usage"
        entry = parser.parse_line(line, line_number=1)

        assert entry is not None
        assert entry.level == LogLevel.WARN

    def test_parse_invalid_line_returns_none(self):
        parser = LogParser(pattern_name="standard")
        entry = parser.parse_line("invalid log line", line_number=1)
        assert entry is None

    def test_parse_multiple_lines(self):
        parser = LogParser(pattern_name="standard")
        lines = [
            "2024-01-15 10:30:45 [INFO] Line one",
            "2024-01-15 10:30:46 [ERROR] Line two",
            "invalid line",
            "2024-01-15 10:30:47 [WARN] Line three",
        ]
        entries = parser.parse_lines(lines)

        assert len(entries) == 3
        assert entries[0].level == LogLevel.INFO
        assert entries[1].level == LogLevel.ERROR
        assert entries[2].level == LogLevel.WARN

    def test_custom_pattern(self):
        parser = LogParser(custom_pattern=r"(?P<timestamp>\d{4}-\d{2}-\d{2})\s+(?P<message>.*)")
        line = "2024-01-15 Hello world"
        entry = parser.parse_line(line)

        assert entry is not None
        assert entry.message == "Hello world"

    def test_unknown_pattern_raises_error(self):
        with pytest.raises(ValueError):
            LogParser(pattern_name="nonexistent")

    def test_syslog_pattern(self):
        parser = LogParser(pattern_name="syslog")
        line = "Jan 15 10:30:45 myhost sshd[1234]: Accepted publickey"
        entry = parser.parse_line(line)

        assert entry is not None
        assert entry.source == "sshd"
        assert "Accepted" in entry.message
