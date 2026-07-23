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


def get_package_info() -> dict:
    """Get package information.

    Returns:
        Dictionary with package metadata.
    """
    return {
        "name": "modular-log-analysis-toolkit",
        "version": __version__,
        "author": __author__,
        "modules": len(__all__),
    }


def get_version_info() -> dict:
    """Get version information.

    Returns:
        Dictionary with version details.
    """
    parts = __version__.split(".")
    return {
        "version": __version__,
        "major": int(parts[0]) if len(parts) > 0 else 0,
        "minor": int(parts[1]) if len(parts) > 1 else 0,
        "patch": parts[2] if len(parts) > 2 else "0",
    }


def is_dev_version() -> bool:
    """Check if this is a development version.

    Returns:
        True if version contains 'dev'.
    """
    return "dev" in __version__


def get_version_formatted() -> str:
    """Get formatted version string.

    Returns:
        Formatted version string.
    """
    return f"v{__version__}"


def get_modules_formatted() -> str:
    """Get formatted modules string.

    Returns:
        Formatted modules string.
    """
    return ", ".join(__all__)


def get_module_count_formatted() -> str:
    """Get formatted module count string.

    Returns:
        Formatted module count string.
    """
    return f"{len(__all__)} modules"


def get_package_info_formatted() -> str:
    """Get formatted package info string.

    Returns:
        Formatted package info string.
    """
    return f"modular-log-analysis-toolkit v{__version__} by {__author__}"


def get_version_info_formatted() -> str:
    """Get formatted version info string.

    Returns:
        Formatted version info string.
    """
    info = get_version_info()
    return f"v{info['version']} (major: {info['major']}, minor: {info['minor']}, patch: {info['patch']})"


def get_author() -> str:
    """Get package author.

    Returns:
        Author string.
    """
    return __author__


def get_author_formatted() -> str:
    """Get formatted author string.

    Returns:
        Formatted author string.
    """
    return f"Author: {__author__}"
