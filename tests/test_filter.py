"""Unit tests for the log filtering module."""

import pytest
from datetime import datetime, timedelta

from src.filter import LogFilter
from src.models import LogEntry, LogLevel


def _make_entry(level: LogLevel, message: str = "test", source: str = "app") -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 1, 15, 10, 0, 0),
        level=level,
        message=message,
        source=source,
    )


class TestLogFilter:
    """Test suite for LogFilter."""

    def setup_method(self):
        self.entries = [
            _make_entry(LogLevel.INFO, "User login", "auth"),
            _make_entry(LogLevel.ERROR, "DB connection failed", "db"),
            _make_entry(LogLevel.WARN, "Slow query", "db"),
            _make_entry(LogLevel.INFO, "Request processed", "api"),
            _make_entry(LogLevel.CRITICAL, "Out of memory", "app"),
        ]

    def test_filter_by_single_level(self):
        result = LogFilter(self.entries).by_level(LogLevel.ERROR).apply()
        assert len(result) == 1
        assert result[0].level == LogLevel.ERROR

    def test_filter_by_multiple_levels(self):
        result = LogFilter(self.entries).by_level(LogLevel.ERROR, LogLevel.CRITICAL).apply()
        assert len(result) == 2

    def test_filter_by_source(self):
        result = LogFilter(self.entries).by_source("db").apply()
        assert len(result) == 2

    def test_filter_by_keyword(self):
        result = LogFilter(self.entries).by_keyword("connection").apply()
        assert len(result) == 1
        assert "DB connection" in result[0].message

    def test_filter_by_keyword_case_insensitive(self):
        result = LogFilter(self.entries).by_keyword("CONNECTION").apply()
        assert len(result) == 1

    def test_combined_filters(self):
        result = (LogFilter(self.entries)
                  .by_level(LogLevel.INFO, LogLevel.WARN)
                  .by_source("db")
                  .apply())
        assert len(result) == 1
        assert result[0].level == LogLevel.WARN

    def test_count_by_level(self):
        counts = LogFilter(self.entries).count_by_level()
        assert counts["INFO"] == 2
        assert counts["ERROR"] == 1
        assert counts["CRITICAL"] == 1

    def test_empty_filter_returns_all(self):
        result = LogFilter(self.entries).apply()
        assert len(result) == 5

    def test_filter_no_match(self):
        result = LogFilter(self.entries).by_keyword("nonexistent").apply()
        assert len(result) == 0
