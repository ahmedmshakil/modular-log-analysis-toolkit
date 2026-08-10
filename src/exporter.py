"""Export log analysis results to various formats."""

import os
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

    @staticmethod
    def get_level_counts_formatted(entries: List[LogEntry]) -> str:
        """Get formatted level counts string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted level counts string.
        """
        counts = LogExporter.get_level_counts(entries)
        if not counts:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in counts.items())

    @staticmethod
    def get_source_counts_formatted(entries: List[LogEntry]) -> str:
        """Get formatted source counts string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted source counts string.
        """
        counts = LogExporter.get_source_counts(entries)
        if not counts:
            return "none"
        return ", ".join(f"{k}:{v}" for k, v in counts.items())

    @staticmethod
    def get_level_distribution_formatted(entries: List[LogEntry]) -> str:
        """Get formatted level distribution string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted level distribution string.
        """
        dist = LogExporter.get_level_distribution(entries)
        if not dist:
            return "none"
        return ", ".join(f"{k}:{v:.1f}%" for k, v in dist.items())

    @staticmethod
    def get_source_distribution_formatted(entries: List[LogEntry]) -> str:
        """Get formatted source distribution string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted source distribution string.
        """
        dist = LogExporter.get_source_distribution(entries)
        if not dist:
            return "none"
        return ", ".join(f"{k}:{v:.1f}%" for k, v in dist.items())

    @staticmethod
    def get_most_common_level_formatted(entries: List[LogEntry]) -> str:
        """Get formatted most common level string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted most common level string.
        """
        level = LogExporter.get_most_common_level(entries)
        return level if level else "none"

    @staticmethod
    def get_most_common_source_formatted(entries: List[LogEntry]) -> str:
        """Get formatted most common source string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted most common source string.
        """
        source = LogExporter.get_most_common_source(entries)
        return source if source else "none"

    @staticmethod
    def get_least_common_level_formatted(entries: List[LogEntry]) -> str:
        """Get formatted least common level string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted least common level string.
        """
        level = LogExporter.get_least_common_level(entries)
        return level if level else "none"

    @staticmethod
    def get_least_common_source_formatted(entries: List[LogEntry]) -> str:
        """Get formatted least common source string.

        Args:
            entries: List of log entries.

        Returns:
            Formatted least common source string.
        """
        source = LogExporter.get_least_common_source(entries)
        return source if source else "none"

    @staticmethod
    def get_supported_formats_formatted() -> str:
        """Get formatted supported formats string.

        Returns:
            Formatted supported formats string.
        """
        formats = LogExporter.get_supported_formats()
        return ", ".join(formats)

    @staticmethod
    def detect_format(file_path: str) -> Dict[str, Any]:
        """Detect export format from file extension.

        Args:
            file_path: Path to file.

        Returns:
            Dictionary with format info.
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        format_map = {
            ".json": "json",
            ".csv": "csv",
            ".txt": "text",
            ".log": "text",
            ".html": "html",
            ".xml": "xml",
        }

        detected = format_map.get(ext, "unknown")

        return {
            "file": str(path),
            "extension": ext,
            "detected_format": detected,
            "is_supported": detected != "unknown",
        }

    @staticmethod
    def validate_export_path(file_path: str) -> Dict[str, Any]:
        """Validate export file path.

        Args:
            file_path: Path to export file.

        Returns:
            Dictionary with validation result.
        """
        path = Path(file_path)

        # Check parent directory
        parent = path.parent
        if not parent.exists():
            return {"valid": False, "error": f"Parent directory does not exist: {parent}"}

        # Check write permission
        if not os.access(parent, os.W_OK):
            return {"valid": False, "error": f"No write permission: {parent}"}

        # Check if file exists
        exists = path.exists()

        return {
            "valid": True,
            "error": None,
            "path": str(path),
            "exists": exists,
            "parent_exists": True,
        }

    @staticmethod
    def get_export_stats(entries: List[LogEntry]) -> Dict[str, Any]:
        """Get export statistics.

        Args:
            entries: List of log entries.

        Returns:
            Dictionary with export stats.
        """
        if not entries:
            return {"total": 0, "size_estimate_kb": 0}

        # Estimate size
        size_estimate = 0
        for entry in entries:
            size_estimate += len(entry.message) + 50  # Rough estimate

        return {
            "total": len(entries),
            "size_estimate_kb": round(size_estimate / 1024, 2),
            "levels": LogExporter.get_level_distribution(entries),
            "sources": len(LogExporter.get_source_distribution(entries)),
        }

    @staticmethod
    def get_export_preview(entries: List[LogEntry], limit: int = 5) -> List[Dict[str, Any]]:
        """Get preview of entries to export.

        Args:
            entries: List of log entries.
            limit: Number of entries to preview.

        Returns:
            List of entry dictionaries.
        """
        if not entries:
            return []

        preview = []
        for entry in entries[:limit]:
            preview.append({
                "timestamp": entry.timestamp.isoformat(),
                "level": entry.level.value,
                "source": entry.source,
                "message": entry.message[:100] + "..." if len(entry.message) > 100 else entry.message,
            })

        return preview

    @staticmethod
    def export_batch(entries: List[LogEntry], output_dir: str, prefix: str = "logs", batch_size: int = 1000) -> Dict[str, Any]:
        """Export entries in batches for large datasets.

        Args:
            entries: List of log entries to export.
            output_dir: Directory to write export files.
            prefix: Filename prefix for exported files.
            batch_size: Number of entries per batch (default 1000).

        Returns:
            Dictionary with export results.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        results = {
            "total": len(entries),
            "batch_size": batch_size,
            "num_batches": 0,
            "files": [],
        }

        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            batch_num = i // batch_size + 1
            batch_prefix = f"{prefix}_batch{batch_num}"

            batch_files = {}
            batch_files["json"] = LogExporter.to_json(batch, str(out / f"{batch_prefix}.json"))
            batch_files["csv"] = LogExporter.to_csv(batch, str(out / f"{batch_prefix}.csv"))
            batch_files["text"] = LogExporter.to_text(batch, str(out / f"{batch_prefix}.txt"))

            results["files"].append({
                "batch": batch_num,
                "entries": len(batch),
                "files": batch_files,
            })

        results["num_batches"] = len(results["files"])
        return results

    @staticmethod
    def export_by_level(entries: List[LogEntry], output_dir: str, prefix: str = "logs") -> Dict[str, str]:
        """Export entries grouped by log level.

        Args:
            entries: List of log entries to export.
            output_dir: Directory to write export files.
            prefix: Filename prefix for exported files.

        Returns:
            Dictionary mapping level names to output file paths.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # Group entries by level
        level_groups: Dict[str, List[LogEntry]] = {}
        for entry in entries:
            level = entry.level.value
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(entry)

        # Export each level group
        results = {}
        for level, level_entries in level_groups.items():
            level_prefix = f"{prefix}_{level.lower()}"
            results[level] = LogExporter.to_json(level_entries, str(out / f"{level_prefix}.json"))

        return results

    @staticmethod
    def export_by_source(entries: List[LogEntry], output_dir: str, prefix: str = "logs") -> Dict[str, str]:
        """Export entries grouped by source.

        Args:
            entries: List of log entries to export.
            output_dir: Directory to write export files.
            prefix: Filename prefix for exported files.

        Returns:
            Dictionary mapping source names to output file paths.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # Group entries by source
        source_groups: Dict[str, List[LogEntry]] = {}
        for entry in entries:
            source = entry.source or "unknown"
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(entry)

        # Export each source group
        results = {}
        for source, source_entries in source_groups.items():
            source_prefix = f"{prefix}_{source.lower().replace(' ', '_')}"
            results[source] = LogExporter.to_json(source_entries, str(out / f"{source_prefix}.json"))

        return results

    @staticmethod
    def export_with_options(entries: List[LogEntry], output_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Export entries with custom options.

        Args:
            entries: List of log entries to export.
            output_path: Path to write the export file.
            options: Export options dictionary.

        Returns:
            Dictionary with export results.
        """
        if not entries:
            return {"success": False, "error": "No entries to export"}

        # Parse options
        format_type = options.get("format", "json")
        indent = options.get("indent", 2)
        encoding = options.get("encoding", "utf-8")
        include_metadata = options.get("include_metadata", True)
        filter_level = options.get("filter_level")
        filter_source = options.get("filter_source")

        # Apply filters
        filtered_entries = entries
        if filter_level:
            filtered_entries = [e for e in filtered_entries if e.level.value == filter_level]
        if filter_source:
            filtered_entries = [e for e in filtered_entries if e.source == filter_source]

        if not filtered_entries:
            return {"success": False, "error": "No entries match filters"}

        # Export based on format
        try:
            if format_type == "json":
                result_path = LogExporter.to_json(filtered_entries, output_path, indent, encoding)
            elif format_type == "csv":
                result_path = LogExporter.to_csv(filtered_entries, output_path, encoding)
            elif format_type == "text":
                result_path = LogExporter.to_text(filtered_entries, output_path, encoding)
            else:
                return {"success": False, "error": f"Unsupported format: {format_type}"}

            return {
                "success": True,
                "path": result_path,
                "format": format_type,
                "entries": len(filtered_entries),
                "original_entries": len(entries),
                "filtered": len(entries) - len(filtered_entries),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def export_summary(entries: List[LogEntry], output_path: str) -> Dict[str, Any]:
        """Export a summary report of the entries.

        Args:
            entries: List of log entries.
            output_path: Path to write the summary.

        Returns:
            Dictionary with export results.
        """
        if not entries:
            return {"success": False, "error": "No entries to summarize"}

        try:
            # Generate summary
            level_counts = {}
            source_counts = {}
            for entry in entries:
                level_counts[entry.level.value] = level_counts.get(entry.level.value, 0) + 1
                if entry.source:
                    source_counts[entry.source] = source_counts.get(entry.source, 0) + 1

            summary = {
                "total_entries": len(entries),
                "level_distribution": level_counts,
                "source_distribution": source_counts,
                "time_range": {
                    "start": min(e.timestamp for e in entries).isoformat(),
                    "end": max(e.timestamp for e in entries).isoformat(),
                },
                "error_rate": round(
                    level_counts.get("ERROR", 0) / len(entries) * 100, 2
                ) if entries else 0,
            }

            # Write summary
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(summary, f, indent=2)

            return {
                "success": True,
                "path": str(path),
                "summary": summary,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def export_filtered(entries: List[LogEntry], output_path: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Export entries with filters applied.

        Args:
            entries: List of log entries to export.
            output_path: Path to write the export file.
            filters: Filters to apply.

        Returns:
            Dictionary with export results.
        """
        if not entries:
            return {"success": False, "error": "No entries to export"}

        # Apply filters
        filtered = entries.copy()

        if "level" in filters:
            level = filters["level"]
            filtered = [e for e in filtered if e.level.value == level]

        if "source" in filters:
            source = filters["source"]
            filtered = [e for e in filtered if e.source == source]

        if "keyword" in filters:
            keyword = filters["keyword"].lower()
            filtered = [e for e in filtered if keyword in e.message.lower()]

        if "start_time" in filters:
            start_time = filters["start_time"]
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if "end_time" in filters:
            end_time = filters["end_time"]
            filtered = [e for e in filtered if e.timestamp <= end_time]

        if not filtered:
            return {"success": False, "error": "No entries match filters"}

        # Export filtered entries
        try:
            result_path = LogExporter.to_json(filtered, output_path)
            return {
                "success": True,
                "path": result_path,
                "entries": len(filtered),
                "original_entries": len(entries),
                "filters_applied": filters,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
