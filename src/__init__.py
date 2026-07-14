# modular-log-analysis-toolkit: Core log analysis toolkit
# Version: 1.2.0-dev

__version__ = "1.2.0-dev"
__author__ = "modular-log-analysis-toolkit team"
__all__ = [
    "models",
    "parser",
    "filter",
    "aggregator",
    "exporter",
    "reader",
    "alerts",
    "cli",
    "web",
    "plugins",
    "dedup",
    "streaming",
    "search",
    "retention",
    "geolocation",
    "tags",
    "webhooks",
    "auth",
    "cache",
]


def get_version() -> str:
    """Get the current version string.

    Returns:
        Version string.
    """
    return __version__


def get_modules() -> list:
    """Get list of available modules.

    Returns:
        List of module names.
    """
    return __all__.copy()


def get_module_count() -> int:
    """Get number of available modules.

    Returns:
        Module count.
    """
    return len(__all__)
