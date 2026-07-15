"""File reader utilities for log analysis."""

import gzip
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterator, Optional


def read_log_lines(file_path: str, encoding: str = "utf-8") -> Iterator[str]:
    """Read log file line by line with memory efficiency.

    Args:
        file_path: Path to the log file.
        encoding: File encoding (default: utf-8).

    Yields:
        Lines from the log file with trailing newlines removed.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a regular file: {file_path}")
    with open(path, "r", encoding=encoding) as f:
        for line in f:
            yield line.rstrip("\n")


def read_compressed_log(file_path: str, encoding: str = "utf-8") -> Iterator[str]:
    """Read gzip-compressed log files line by line.

    Args:
        file_path: Path to the gzip-compressed log file.
        encoding: File encoding (default: utf-8).

    Yields:
        Lines from the compressed log file with trailing newlines removed.

    Raises:
        ValueError: If the file is not a valid gzip file.
    """
    try:
        with gzip.open(file_path, "rt", encoding=encoding) as f:
            for line in f:
                yield line.rstrip("\n")
    except gzip.BadGzipFile:
        raise ValueError(f"File is not a valid gzip file: {file_path}")


def get_file_size(file_path: str) -> int:
    """Return file size in bytes.

    Args:
        file_path: Path to the file.

    Returns:
        File size in bytes.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
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


def read_log_lines_with_numbers(file_path: str, encoding: str = "utf-8") -> Iterator[tuple]:
    """Read log file with line numbers.

    Args:
        file_path: Path to the log file.
        encoding: File encoding (default: utf-8).

    Yields:
        Tuples of (line_number, line_content).

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {file_path}")
    with open(path, "r", encoding=encoding) as f:
        for i, line in enumerate(f, 1):
            yield (i, line.rstrip("\n"))


def format_size(size_bytes: int) -> str:
    """Format byte size into human-readable string."""
    if size_bytes < 0:
        raise ValueError("Size must be non-negative")
    if size_bytes == 0:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


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


def file_exists(file_path: str) -> bool:
    """Check if a file exists and is accessible.

    Args:
        file_path: Path to check.

    Returns:
        True if file exists, False otherwise.
    """
    return Path(file_path).is_file()


def is_compressed(file_path: str) -> bool:
    """Check if a file is gzip compressed.

    Args:
        file_path: Path to check.

    Returns:
        True if file has .gz extension, False otherwise.
    """
    return file_path.endswith(".gz")


def get_file_info(file_path: str) -> Dict:
    """Get comprehensive file information.

    Args:
        file_path: Path to the file.

    Returns:
        Dictionary with file metadata.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    stat = path.stat()
    return {
        "path": str(path.absolute()),
        "name": path.name,
        "extension": path.suffix,
        "size_bytes": stat.st_size,
        "size_formatted": format_size(stat.st_size),
        "is_compressed": is_compressed(file_path),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
    }


def get_line_count_fast(file_path: str) -> int:
    """Count lines in a file quickly using buffer.

    Args:
        file_path: Path to the file.

    Returns:
        Number of lines.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    count = 0
    buffer_size = 1024 * 1024  # 1MB buffer
    with open(path, "rb") as f:
        while True:
            buffer = f.read(buffer_size)
            if not buffer:
                break
            count += buffer.count(b"\n")
    return count


def read_last_lines(file_path: str, n: int = 10, encoding: str = "utf-8") -> List[str]:
    """Read last N lines from a file.

    Args:
        file_path: Path to the file.
        n: Number of lines to read from end.
        encoding: File encoding.

    Returns:
        List of last N lines.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(path, "r", encoding=encoding) as f:
        lines = f.readlines()
    return [line.rstrip("\n") for line in lines[-n:]]


def get_file_extension(file_path: str) -> str:
    """Get file extension.

    Args:
        file_path: Path to the file.

    Returns:
        File extension string (e.g., ".log", ".gz").
    """
    return Path(file_path).suffix


def get_file_name(file_path: str) -> str:
    """Get file name without path.

    Args:
        file_path: Path to the file.

    Returns:
        File name string.
    """
    return Path(file_path).name


def get_parent_directory(file_path: str) -> str:
    """Get parent directory of a file.

    Args:
        file_path: Path to the file.

    Returns:
        Parent directory path string.
    """
    return str(Path(file_path).parent)
