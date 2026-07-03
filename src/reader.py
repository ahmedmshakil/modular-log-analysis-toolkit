"""File reader utilities for log analysis."""

import gzip
import os
from pathlib import Path
from typing import Iterator, Optional


def read_log_lines(file_path: str, encoding: str = "utf-8") -> Iterator[str]:
    """Read log file line by line with memory efficiency."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {file_path}")
    with open(path, "r", encoding=encoding) as f:
        for line in f:
            yield line.rstrip("\n")


def read_compressed_log(file_path: str, encoding: str = "utf-8") -> Iterator[str]:
    """Read gzip-compressed log files."""
    try:
        with gzip.open(file_path, "rt", encoding=encoding) as f:
            for line in f:
                yield line.rstrip("\n")
    except gzip.BadGzipFile:
        raise ValueError(f"File is not a valid gzip file: {file_path}")


def get_file_size(file_path: str) -> int:
    """Return file size in bytes."""
    return os.path.getsize(file_path)


def count_lines(file_path: str) -> int:
    """Count total lines in a file efficiently."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a regular file: {file_path}")
    with open(path, "rb") as f:
        return sum(1 for _ in f)


def detect_encoding(file_path: str) -> str:
    """Auto-detect file encoding."""
    try:
        with open(file_path, "rb") as f:
            sample = f.read(4096)
        if sample.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        if sample.startswith(b"\xff\xfe"):
            return "utf-16-le"
        if sample.startswith(b"\xfe\xff"):
            return "utf-16-be"
        # Try utf-8 decode to validate
        try:
            sample.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            return "latin-1"
    except Exception:
        return "utf-8"
