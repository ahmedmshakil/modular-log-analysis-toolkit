"""Command-line interface for sk-loganalyzer."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .parser import LogParser
from .reader import read_log_lines, read_compressed_log
from .filter import LogFilter
from .aggregator import LogAggregator
from .exporter import LogExporter
from .models import LogLevel


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    p = argparse.ArgumentParser(
        prog="sk-loganalyzer",
        description="Analyze and process log files efficiently.",
    )
    p.add_argument("input", nargs="+", help="Log file(s) to analyze")
    p.add_argument("-o", "--output", help="Output file path")
    p.add_argument("-f", "--format", choices=["json", "csv", "text"], default="json")
    p.add_argument("-p", "--pattern", default="standard", help="Log format pattern")
    p.add_argument("-l", "--level", action="append", help="Filter by log level")
    p.add_argument("-s", "--source", help="Filter by log source")
    p.add_argument("-k", "--keyword", help="Filter by keyword")
    p.add_argument("--since", help="Start time filter (YYYY-MM-DD HH:MM:SS)")
    p.add_argument("--until", help="End time filter (YYYY-MM-DD HH:MM:SS)")
    p.add_argument("--summary", action="store_true", help="Show summary statistics")
    p.add_argument("--top-errors", type=int, default=10, help="Number of top errors")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_argument("-q", "--quiet", action="store_true", help="Suppress non-essential output")
    p.add_argument("--version", action="version", version="%(prog)s 1.2.0")
    return p


def main(argv: Optional[List[str]] = None):
    """Main entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Read log files
    entries = []
    log_parser = LogParser(pattern_name=args.pattern)

    for file_path in args.input:
        if file_path.endswith(".gz"):
            lines = list(read_compressed_log(file_path))
        else:
            lines = list(read_log_lines(file_path))
        entries.extend(log_parser.parse_lines(lines))

    if not entries:
        print("No log entries found.", file=sys.stderr)
        sys.exit(1)

    # Apply filters
    log_filter = LogFilter(entries)
    if args.level:
        levels = [LogLevel[l.upper()] for l in args.level]
        log_filter.by_level(*levels)
    if args.source:
        log_filter.by_source(args.source)
    if args.keyword:
        log_filter.by_keyword(args.keyword)
    filtered = log_filter.apply()

    # Generate summary
    if args.summary:
        agg = LogAggregator(filtered)
        result = agg.summary()
        print(f"Total entries: {result.total_entries}")
        print(f"Level counts: {result.level_counts}")
        print(f"Error rate: {agg.error_rate():.2f}%")
        print(f"Top sources: {agg.top_sources()}")
        return

    # Export results
    if args.output:
        exporter = LogExporter()
        if args.format == "json":
            path = exporter.to_json(filtered, args.output)
        elif args.format == "csv":
            path = exporter.to_csv(filtered, args.output)
        else:
            path = exporter.to_text(filtered, args.output)
        print(f"Exported {len(filtered)} entries to {path}")
    else:
        for entry in filtered:
            print(f"[{entry.level.value}] {entry.timestamp} - {entry.message}")


if __name__ == "__main__":
    main()
