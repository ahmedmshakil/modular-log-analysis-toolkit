"""Export log analysis results to various formats."""

import csv
import json
from io import StringIO
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import LogEntry, AnalysisResult


class LogExporter:
    """Export log entries and analysis results."""

    def __repr__(self) -> str:
        return "LogExporter()"

    def __str__(self) -> str:
        formats = ", ".join(self.supported_formats())
        return f"LogExporter(formats=[{formats}])"

    @staticmethod
    def to_json(entries: List[LogEntry], output_path: str, indent: int = 2, encoding: str = "utf-8") -> str:
        """Export entries to JSON format.

        Args:
            entries: List of log entries to export.
            output_path: Path to write the JSON file.
            indent: JSON indentation level.
            encoding: File encoding.

        Returns:
            Path to the exported file.

        Raises:
            TypeError: If entries is not a list.
        """
        if not entries:
            return output_path
        if not isinstance(entries, list):
            raise TypeError("entries must be a list")
        data = [entry.to_dict() for entry in entries]
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=indent, default=str)
        return str(path)

    @staticmethod
    def to_csv(entries: List[LogEntry], output_path: str, encoding: str = "utf-8") -> str:
        """Export entries to CSV format.

        Args:
            entries: List of log entries to export.
            output_path: Path to write the CSV file.
            encoding: File encoding.

        Returns:
            Path to the exported file.
        """
        if not entries:
            return output_path
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding=encoding) as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "level", "source", "message", "line_number"])
            for entry in entries:
                writer.writerow([
                    entry.timestamp.isoformat(),
                    entry.level.value,
                    entry.source or "",
                    entry.message,
                    entry.line_number,
                ])
        return str(path)

    @staticmethod
    def to_text(entries: List[LogEntry], output_path: str, encoding: str = "utf-8") -> str:
        """Export entries to plain text format."""
        if not entries:
            return output_path
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            for entry in entries:
                f.write(f"[{entry.level.value}] {entry.timestamp} - {entry.message}\n")
        return str(path)

    @staticmethod
    def result_to_json(result: AnalysisResult, output_path: str) -> str:
        """Export analysis result to JSON."""
        data = {
            "total_entries": result.total_entries,
            "level_counts": result.level_counts,
            "time_range": [t.isoformat() for t in result.time_range] if result.time_range else None,
            "top_errors": result.top_errors,
            "sources": result.sources,
            "duration_seconds": result.duration_seconds,
        }
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return str(path)

    @staticmethod
    def export_all(entries: List[LogEntry], output_dir: str, prefix: str = "logs") -> Dict[str, str]:
        """Export entries in all supported formats at once.

        Args:
            entries: List of log entries to export.
            output_dir: Directory to write export files.
            prefix: Filename prefix for exported files.

        Returns:
            Dictionary mapping format names to output file paths.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        results = {}
        results["json"] = LogExporter.to_json(entries, str(out / f"{prefix}.json"))
        results["csv"] = LogExporter.to_csv(entries, str(out / f"{prefix}.csv"))
        results["text"] = LogExporter.to_text(entries, str(out / f"{prefix}.txt"))
        return results

    @staticmethod
    def supported_formats() -> List[str]:
        """Get list of supported export formats.

        Returns:
            List of format names.
        """
        return ["json", "csv", "text"]

    @staticmethod
    def entries_to_json_string(entries: List[LogEntry], indent: int = 2) -> str:
        """Convert entries to JSON string without writing to file.

        Args:
            entries: List of log entries.
            indent: JSON indentation level.

        Returns:
            JSON string representation.
        """
        if not entries:
            return "[]"
        data = [entry.to_dict() for entry in entries]
        return json.dumps(data, indent=indent, default=str)

    @staticmethod
    def entries_to_csv_string(entries: List[LogEntry]) -> str:
        """Convert entries to CSV string without writing to file.

        Args:
            entries: List of log entries.

        Returns:
            CSV string representation.
        """
        if not entries:
            return ""
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "level", "source", "message", "line_number"])
        for entry in entries:
            writer.writerow([
                entry.timestamp.isoformat(),
                entry.level.value,
                entry.source or "",
                entry.message,
                entry.line_number,
            ])
        return output.getvalue()

    @staticmethod
    def entries_to_text_string(entries: List[LogEntry]) -> str:
        """Convert entries to plain text string without writing to file.

        Args:
            entries: List of log entries.

        Returns:
            Text string representation.
        """
        if not entries:
            return ""
        lines = []
        for entry in entries:
            lines.append(f"[{entry.level.value}] {entry.timestamp} - {entry.message}")
        return "\n".join(lines)

    @staticmethod
    def get_entry_count(entries: List[LogEntry]) -> int:
        """Get number of entries to export.

        Args:
            entries: List of log entries.

        Returns:
            Count of entries.
        """
        return len(entries) if entries else 0

    @staticmethod
    def is_empty(entries: List[LogEntry]) -> bool:
        """Check if entries list is empty.

        Args:
            entries: List of log entries.

        Returns:
            True if entries is empty or None.
        """
        return not entries

    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported export formats.

        Returns:
            List of format strings.
        """
        return ["json", "csv", "text"]

    @staticmethod
    def get_format_count() -> int:
        """Get number of supported formats.

        Returns:
            Count of formats.
        """
        return 3

    @staticmethod
    def is_valid_format(format_name: str) -> bool:
        """Check if a format name is valid.

        Args:
            format_name: Format name to check.

        Returns:
            True if format is supported.
        """
        return format_name.lower() in ["json", "csv", "text"]

    @staticmethod
    def get_entries_summary(entries: List[LogEntry]) -> Dict[str, Any]:
        """Get summary of entries to export.

        Args:
            entries: List of log entries.

        Returns:
            Dictionary with entry summary.
        """
        if not entries:
            return {"count": 0, "levels": {}, "sources": []}
        from collections import Counter
        levels = Counter(e.level.value for e in entries)
        sources = list(set(e.source for e in entries if e.source))
        return {
            "count": len(entries),
            "levels": dict(levels),
            "sources": sources,
        }

    @staticmethod
    def get_summary_string(entries: List[LogEntry]) -> str:
        """Get a formatted summary string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted summary string.
        """
        if not entries:
            return "No entries"
        from collections import Counter
        levels = Counter(e.level.value for e in entries)
        return f"Entries: {len(entries)}, Levels: {dict(levels)}"

    @staticmethod
    def get_stats_dict(entries: List[LogEntry]) -> Dict[str, Any]:
        """Get export statistics as dictionary.

        Args:
            entries: List of log entries.

        Returns:
            Dictionary with export stats.
        """
        return {
            "count": len(entries) if entries else 0,
            "is_empty": not entries,
            "formats": LogExporter.get_format_count(),
        }

    @staticmethod
    def get_level_distribution(entries: List[LogEntry]) -> Dict[str, float]:
        """Get level distribution as percentages.

        Args:
            entries: List of log entries.

        Returns:
            Dictionary mapping level names to percentages.
        """
        if not entries:
            return {}
        from collections import Counter
        total = len(entries)
        counts = Counter(e.level.value for e in entries)
        return {level: round(count / total * 100, 2) for level, count in counts.items()}

    @staticmethod
    def get_source_distribution(entries: List[LogEntry]) -> Dict[str, float]:
        """Get source distribution as percentages.

        Args:
            entries: List of log entries.

        Returns:
            Dictionary mapping source names to percentages.
        """
        if not entries:
            return {}
        from collections import Counter
        total = len(entries)
        counts = Counter(e.source for e in entries if e.source)
        return {source: round(count / total * 100, 2) for source, count in counts.items()}

    @staticmethod
    def get_most_common_level(entries: List[LogEntry]) -> Optional[str]:
        """Get the most common level.

        Args:
            entries: List of log entries.

        Returns:
            Most common level string, or None.
        """
        if not entries:
            return None
        from collections import Counter
        counts = Counter(e.level.value for e in entries)
        return max(counts, key=counts.get) if counts else None

    @staticmethod
    def get_least_common_level(entries: List[LogEntry]) -> Optional[str]:
        """Get the least common level.

        Args:
            entries: List of log entries.

        Returns:
            Least common level string, or None.
        """
        if not entries:
            return None
        from collections import Counter
        counts = Counter(e.level.value for e in entries)
        return min(counts, key=counts.get) if counts else None

    @staticmethod
    def get_most_common_source(entries: List[LogEntry]) -> Optional[str]:
        """Get the most common source.

        Args:
            entries: List of log entries.

        Returns:
            Most common source string, or None.
        """
        if not entries:
            return None
        from collections import Counter
        counts = Counter(e.source for e in entries if e.source)
        return max(counts, key=counts.get) if counts else None

    @staticmethod
    def get_error_rate(entries: List[LogEntry]) -> float:
        """Get error rate as percentage.

        Args:
            entries: List of log entries.

        Returns:
            Error rate percentage.
        """
        if not entries:
            return 0.0
        from collections import Counter
        total = len(entries)
        counts = Counter(e.level.value for e in entries)
        errors = counts.get("ERROR", 0) + counts.get("CRITICAL", 0)
        return round(errors / total * 100, 2)

    @staticmethod
    def get_source_count(entries: List[LogEntry]) -> int:
        """Get number of unique sources.

        Args:
            entries: List of log entries.

        Returns:
            Count of unique sources.
        """
        if not entries:
            return 0
        return len(set(e.source for e in entries if e.source))

    @staticmethod
    def get_warning_rate(entries: List[LogEntry]) -> float:
        """Get warning rate as percentage.

        Args:
            entries: List of log entries.

        Returns:
            Warning rate percentage.
        """
        if not entries:
            return 0.0
        from collections import Counter
        total = len(entries)
        counts = Counter(e.level.value for e in entries)
        warnings = counts.get("WARN", 0)
        return round(warnings / total * 100, 2)

    @staticmethod
    def get_info_rate(entries: List[LogEntry]) -> float:
        """Get info rate as percentage.

        Args:
            entries: List of log entries.

        Returns:
            Info rate percentage.
        """
        if not entries:
            return 0.0
        from collections import Counter
        total = len(entries)
        counts = Counter(e.level.value for e in entries)
        infos = counts.get("INFO", 0)
        return round(infos / total * 100, 2)

    @staticmethod
    def get_least_common_source(entries: List[LogEntry]) -> Optional[str]:
        """Get the least common source.

        Args:
            entries: List of log entries.

        Returns:
            Least common source string, or None.
        """
        if not entries:
            return None
        from collections import Counter
        counts = Counter(e.source for e in entries if e.source)
        return min(counts, key=counts.get) if counts else None

    @staticmethod
    def get_level_counts(entries: List[LogEntry]) -> Dict[str, int]:
        """Get counts per level.

        Args:
            entries: List of log entries.

        Returns:
            Dictionary mapping level names to counts.
        """
        if not entries:
            return {}
        from collections import Counter
        return dict(Counter(e.level.value for e in entries))

    @staticmethod
    def get_source_counts(entries: List[LogEntry]) -> Dict[str, int]:
        """Get counts per source.

        Args:
            entries: List of log entries.

        Returns:
            Dictionary mapping source names to counts.
        """
        if not entries:
            return {}
        from collections import Counter
        return dict(Counter(e.source for e in entries if e.source))

    @staticmethod
    def get_error_rate_formatted(entries: List[LogEntry]) -> str:
        """Get formatted error rate string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted error rate string.
        """
        return f"{LogExporter.get_error_rate(entries):.1f}%"

    @staticmethod
    def get_warning_rate_formatted(entries: List[LogEntry]) -> str:
        """Get formatted warning rate string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted warning rate string.
        """
        return f"{LogExporter.get_warning_rate(entries):.1f}%"

    @staticmethod
    def get_info_rate_formatted(entries: List[LogEntry]) -> str:
        """Get formatted info rate string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted info rate string.
        """
        return f"{LogExporter.get_info_rate(entries):.1f}%"

    @staticmethod
    def get_entry_count_formatted(entries: List[LogEntry]) -> str:
        """Get formatted entry count string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted entry count string.
        """
        return f"{LogExporter.get_entry_count(entries)} entries"

    @staticmethod
    def get_source_count_formatted(entries: List[LogEntry]) -> str:
        """Get formatted source count string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted source count string.
        """
        return f"{LogExporter.get_source_count(entries)} sources"

    @staticmethod
    def get_level_count_formatted(entries: List[LogEntry]) -> str:
        """Get formatted level count string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted level count string.
        """
        counts = LogExporter.get_level_counts(entries)
        return f"{len(counts)} levels"

    @staticmethod
    def get_format_count_formatted() -> str:
        """Get formatted format count string.

        Returns:
            Formatted format count string.
        """
        return f"{LogExporter.get_format_count()} formats"
