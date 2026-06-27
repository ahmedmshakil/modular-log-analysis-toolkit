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

    def stream(self, callback: Callable[[LogEntry], None], batch_size: int = 1):
        """Stream entries through a callback function."""
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
        """Stream entries in batches."""
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

    @property
    def stats(self) -> dict:
        """Get streaming statistics."""
        return {
            "processed": self._processed,
            "errors": self._errors,
            "paused": self._paused,
            "stopped": self._stopped,
        }
