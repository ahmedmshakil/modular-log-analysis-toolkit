# Changelog

All notable changes to sk-loganalyzer will be documented in this file.

## [1.2.0] - 2026-06-29

### Added
- `__all__` exports list to core package `__init__.py`
- `__str__` method to `AnalysisResult` for readable output
- `__repr__` methods to `LogFilter` and `QueryCache`
- `CONTRIBUTING.md` with development guidelines
- `SECURITY.md` with vulnerability reporting policy
- `CODE_OF_CONDUCT.md` for community standards
- `LICENSE` (MIT) file
- `.editorconfig` for consistent code style
- `requirements.txt` with optional dependencies
- `pyproject.toml` with build system configuration
- `Makefile` with common development targets
- `py.typed` marker for PEP 561 support
- Documentation: `ARCHITECTURE.md`, `CONFIGURATION.md`, `TROUBLESHOOTING.md`, `EXAMPLES.md`

### Fixed
- Removed redundant zero-check in `aggregator.error_rate` method
- Moved `import re` to module level in `filter.py`

## [1.1.0] - 2026-06-01

### Added
- Full-text search indexing with word tokenization
- Log retention policy module with compression and rotation
- IP geolocation lookup for network log entries
- Custom tag and label system for log categorization
- User authentication with role-based access control
- LRU caching layer for query performance

## [1.0.0] - 2026-05-01

### Added
- Initial release with core log analysis pipeline
- Multi-format log parsing (standard, syslog, Apache)
- Filtering engine with level, time, source, and keyword support
- Aggregation and statistics module
- JSON, CSV, and text export formats
- CLI interface
- Web dashboard for real-time monitoring
- Plugin system for custom processors
- Streaming mode for large file processing
- Deduplication by hash comparison
- Alert system with webhook notifications
