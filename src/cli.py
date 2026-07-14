"""Command-line interface for modular-log-analysis-toolkit."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .parser import LogParser
from .reader import read_log_lines, read_compressed_log
from .filter import LogFilter
from .aggregator import LogAggregator
from .exporter import LogExporter
from .models import LogLevel
from . import __version__


def _parse_cli_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("expected YYYY-MM-DD HH:MM:SS")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    p = argparse.ArgumentParser(
        prog="modular-log-analysis-toolkit",
        description="Analyze, filter, and export log files with powerful pattern matching.",
        epilog=(
            "examples:\n"
            "  %(prog)s app.log --summary\n"
            "  %(prog)s app.log -l ERROR -l CRITICAL -f json -o errors.json\n"
            "  %(prog)s app.log -k timeout --since '2024-01-01 00:00:00'\n"
            "  %(prog)s app.log.gz -p syslog -f csv -o output.csv\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    return p


def main(argv: Optional[List[str]] = None):
    """Main entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Validate mutually exclusive options
    if args.verbose and args.quiet:
        print("Error: verbose and quiet flags are mutually exclusive", file=sys.stderr)
        sys.exit(1)

    # Read log files
    entries = []
    log_parser = LogParser(pattern_name=args.pattern)

    for file_path in args.input:
        try:
            if file_path.endswith(".gz"):
                lines = list(read_compressed_log(file_path))
            else:
                lines = list(read_log_lines(file_path))
            entries.extend(log_parser.parse_lines(lines))
        except FileNotFoundError:
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        except PermissionError:
            print(f"Error: permission denied: {file_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: failed to read {file_path}: {e}", file=sys.stderr)
            sys.exit(1)

    if not entries:
        print("No log entries found in the specified file(s).", file=sys.stderr)
        sys.exit(1)

    # Apply filters
    log_filter = LogFilter(entries)
    if args.level:
        try:
            levels = [LogLevel[l.upper()] for l in args.level]
        except KeyError as e:
            print(f"Error: invalid log level: {e.args[0]}", file=sys.stderr)
            sys.exit(1)
        log_filter.by_level(*levels)
    if args.source:
        log_filter.by_source(args.source)
    if args.keyword:
        log_filter.by_keyword(args.keyword)
    if args.since or args.until:
        try:
            start = _parse_cli_datetime(args.since) if args.since else datetime.min
            end = _parse_cli_datetime(args.until) if args.until else datetime.max
        except ValueError as e:
            print(f"Error: invalid datetime for --since/--until: {e}", file=sys.stderr)
            sys.exit(1)
        log_filter.by_time_range(start, end)
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
