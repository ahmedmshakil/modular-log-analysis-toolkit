# Changelog

All notable changes to modular-log-analysis-toolkit will be documented in this file.

## [1.2.0] - 2026-06-30

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
- Input validation to `LogParser.parse_line` method
- Thread-safety lock to `LRUCache` get, put, and invalidate_pattern methods
- `reset_stats` method to `LRUCache` for statistics reset
- Timeout type validation to `WebhookSender.__init__`
- Validation for negative days in `RetentionPolicy`
- Input validation and password length check to `AuthManager.create_user`
- UTF-16 BOM detection to `detect_encoding` function
- Encoding parameter to CSV export method
- Missing type hints to `Alert.to_dict` method
- Missing docstring to `GeoLookup.stats` property

### Fixed

- Broken module name string in `__init__.py`
- Potential division by zero in `aggregator.error_rate` method
- Error handling in `GeoLookup._fetch_geo` method
- Empty input handling in search tokenization
- Empty entries list handling in `deduplicate` method
- Empty conditions handling in `TagRule.matches` method
- JSON serialization error handling in webhook POST
- Error messages in CLI for file reading errors
- Paused state reset when stopping stream to prevent hang
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
