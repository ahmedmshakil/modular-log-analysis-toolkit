"""Export log analysis results to various formats."""

import csv
import json
from io import StringIO
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import LogEntry, AnalysisResult


class LogExporter:
    """Export log entries and analysis results."""

    @staticmethod
    def to_json(entries: List[LogEntry], output_path: str, indent: int = 2) -> str:
        """Export entries to JSON format."""
        data = [entry.to_dict() for entry in entries]
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=indent, default=str)
        return str(path)

    @staticmethod
    def to_csv(entries: List[LogEntry], output_path: str) -> str:
        """Export entries to CSV format."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
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
    def to_text(entries: List[LogEntry], output_path: str) -> str:
        """Export entries to plain text format."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
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
        }
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return str(path)
