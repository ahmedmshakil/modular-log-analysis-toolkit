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
