"""Streaming mode for processing large log files."""

import time
from typing import Iterator, Callable, Optional, List
from pathlib import Path

from .models import LogEntry
from .parser import LogParser
from .reader import read_log_lines


class LogStream:
    """Stream log entries for memory-efficient processing."""

    def __init__(self, file_path: str, parser: Optional[LogParser] = None):
        self.file_path = Path(file_path)
        self.parser = parser or LogParser()
        self._paused = False
        self._stopped = False
        self._processed = 0
        self._errors = 0

    def __repr__(self) -> str:
        return f"LogStream(file={self.file_path.name}, processed={self._processed})"

    def stream(self, callback: Callable[[LogEntry], None], batch_size: int = 1):
        """Stream entries through a callback function.

        Args:
            callback: Function to call for each log entry.
            batch_size: Unused, kept for API compatibility.
        """
        if not callable(callback):
            raise TypeError("callback must be callable")
        for line in read_log_lines(str(self.file_path)):
            if self._stopped:
                break
            while self._paused:
                time.sleep(0.1)

            entry = self.parser.parse_line(line, self._processed + 1)
            if entry:
                try:
                    callback(entry)
                    self._processed += 1
                except Exception as e:
                    self._errors += 1
            else:
                self._errors += 1

    def stream_batch(self, callback: Callable[[List[LogEntry]], None], batch_size: int = 100):
        """Stream entries in batches.

        Args:
            callback: Function to call for each batch of entries.
            batch_size: Number of entries per batch.

        Raises:
            ValueError: If batch_size is not a positive integer.
            TypeError: If callback is not callable.
        """
        if not callable(callback):
            raise TypeError("callback must be callable")
        if not isinstance(batch_size, int) or batch_size < 1:
            raise ValueError("batch_size must be a positive integer")
        batch = []
        for line in read_log_lines(str(self.file_path)):
            if self._stopped:
                break
            while self._paused:
                time.sleep(0.1)

            entry = self.parser.parse_line(line, self._processed + 1)
            if entry:
                batch.append(entry)
                self._processed += 1

                if len(batch) >= batch_size:
                    callback(batch)
                    batch = []

        if batch:
            callback(batch)

    def stream_filtered(self, callback: Callable[[LogEntry], None],
                        level_filter: Optional[List[str]] = None):
        """Stream with filtering applied."""
        def _process(entry: LogEntry):
            if level_filter and entry.level.value not in level_filter:
                return
            callback(entry)
        self.stream(_process)

    def pause(self):
        """Pause streaming."""
        self._paused = True

    def resume(self):
        """Resume streaming."""
        self._paused = False

    def stop(self):
        """Stop streaming."""
        self._stopped = True
        self._paused = False

    @property
    def stats(self) -> dict:
        """Get streaming statistics."""
        return {
            "processed": self._processed,
            "errors": self._errors,
            "paused": self._paused,
            "stopped": self._stopped,
        }

    def reset_stats(self):
        """Reset streaming statistics."""
        self._processed = 0
        self._errors = 0
