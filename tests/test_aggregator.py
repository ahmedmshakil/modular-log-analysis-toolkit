"""Unit tests for the log aggregation module."""

import pytest
from datetime import datetime

from src.aggregator import LogAggregator
from src.models import LogEntry, LogLevel


def _entries():
    """Create test log entries."""
    base = datetime(2024, 1, 15, 10, 0, 0)
    return [
        LogEntry(timestamp=base, level=LogLevel.INFO, message="msg1", source="app"),
        LogEntry(timestamp=base, level=LogLevel.ERROR, message="msg2", source="db"),
        LogEntry(timestamp=base, level=LogLevel.WARN, message="msg3", source="app"),
        LogEntry(timestamp=base, level=LogLevel.ERROR, message="msg4", source="db"),
        LogEntry(timestamp=base, level=LogLevel.INFO, message="msg5", source="api"),
    ]


class TestLogAggregator:

    def test_summary_total_count(self):
        agg = LogAggregator(_entries())
        result = agg.summary()
        assert result.total_entries == 5

    def test_summary_level_counts(self):
        agg = LogAggregator(_entries())
        result = agg.summary()
        assert result.level_counts["INFO"] == 2
        assert result.level_counts["ERROR"] == 2
        assert result.level_counts["WARN"] == 1

    def test_error_rate(self):
        agg = LogAggregator(_entries())
        rate = agg.error_rate()
        assert rate == 40.0

    def test_error_rate_empty(self):
        agg = LogAggregator([])
        assert agg.error_rate() == 0.0

    def test_top_sources(self):
        agg = LogAggregator(_entries())
        sources = agg.top_sources(2)
        assert len(sources) == 2
        assert sources[0][0] == "app"
        assert sources[0][1] == 2

    def test_summary_time_range(self):
        agg = LogAggregator(_entries())
        result = agg.summary()
        assert result.time_range is not None
        assert result.time_range[0] == result.time_range[1]
