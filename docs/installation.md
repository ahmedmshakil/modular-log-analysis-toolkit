# Installation Guide

This guide covers how to install the Modular Log Analysis Toolkit on different platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [From Source (Recommended)](#from-source-recommended)
  - [Using pip](#using-pip)
  - [Development Installation](#development-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
  - [Linux](#linux)
  - [macOS](#macos)
  - [Windows](#windows)
- [Virtual Environment Setup](#virtual-environment-setup)
- [Dependencies](#dependencies)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing, ensure you have the following:

### Required

- **Python 3.8 or higher** - Check with `python3 --version`
- **pip** - Python package installer (usually comes with Python)
- **git** - For cloning the repository

### Optional

- **virtualenv** or **venv** - For isolated Python environments
- **flask** - For enhanced web dashboard features
- **pyyaml** - For YAML configuration support

## Installation Methods

### From Source (Recommended)

This is the recommended method for most users.

```bash
# 1. Clone the repository
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git

# 2. Navigate to the project directory
cd modular-log-analysis-toolkit

# 3. Create a virtual environment (recommended)
python3 -m venv venv

# 4. Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 5. Install the package in development mode
pip install -e .

# 6. (Optional) Install additional dependencies
pip install flask pyyaml requests
```

### Using pip

If the package is published to PyPI:

```bash
pip install modular-log-analysis-toolkit
```

### Development Installation

For developers who want to contribute:

```bash
# 1. Clone and navigate
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git
cd modular-log-analysis-toolkit

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS

# 3. Install in development mode with test dependencies
pip install -e ".[dev]"

# 4. Install pre-commit hooks (optional)
pre-commit install
```

## Platform-Specific Instructions

### Linux

#### Ubuntu/Debian

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Clone and install
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git
cd modular-log-analysis-toolkit
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

#### CentOS/RHEL/Fedora

```bash
# Install Python and pip
sudo dnf install python3 python3-pip git

# Or for older versions:
sudo yum install python3 python3-pip git

# Clone and install
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git
cd modular-log-analysis-toolkit
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### macOS

#### Using Homebrew

```bash
# Install Python and git
brew install python git

# Clone and install
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git
cd modular-log-analysis-toolkit
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

#### Using MacPorts

```bash
# Install Python
sudo port install python310 py310-pip

# Clone and install
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git
cd modular-log-analysis-toolkit
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Windows

#### Using Python.org Installer

1. Download Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Open Command Prompt or PowerShell

```powershell
# Clone repository
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git
cd modular-log-analysis-toolkit

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install package
pip install -e .
```

#### Using Windows Subsystem for Linux (WSL)

```bash
# Follow Linux instructions above
sudo apt update
sudo apt install python3 python3-pip python3-venv git
git clone https://github.com/ahmedmshakil/modular-log-analysis-toolkit.git
cd modular-log-analysis-toolkit
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Virtual Environment Setup

Using a virtual environment is **strongly recommended** to avoid dependency conflicts.

### Why Use a Virtual Environment?

- Isolates project dependencies from system Python
- Prevents version conflicts between projects
- Makes it easy to reproduce the environment
- Keeps your system Python clean

### Creating a Virtual Environment

```bash
# Standard venv (Python 3.3+)
python3 -m venv venv

# Or using virtualenv
pip install virtualenv
virtualenv venv

# Activate
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Deactivate when done
deactivate
```

### Managing Virtual Environments

```bash
# List installed packages
pip list

# Save dependencies
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Remove virtual environment
rm -rf venv  # Linux/macOS
rmdir /s /q venv  # Windows
```

## Dependencies

### Required Dependencies

The toolkit uses only Python standard library modules:

- `re` - Regular expressions
- `json` - JSON handling
- `csv` - CSV file operations
- `datetime` - Date and time handling
- `pathlib` - Path operations
- `collections` - Data structures
- `hashlib` - Hashing functions
- `threading` - Thread support
- `http.server` - HTTP server
- `argparse` - CLI argument parsing

### Optional Dependencies

For enhanced features:

```bash
# Web dashboard enhancements
pip install flask

# YAML configuration support
pip install pyyaml

# HTTP requests (alternative to urllib)
pip install requests

# IP geolocation database
pip install geoip2
```

### Development Dependencies

For testing and development:

```bash
pip install pytest pytest-cov flake8 mypy black isort
```

## Verification

After installation, verify everything works:

```bash
# Check Python version
python --version

# Check if package is installed
pip show modular-log-analysis-toolkit

# Run basic test
python -c "from src.parser import LogParser; print('Installation successful!')"

# Run CLI help
python -m src.cli --help

# Run tests
pytest tests/
```

## Troubleshooting

### Common Issues

#### Python not found

```
'python' is not recognized as an internal or external command
```

**Solution:**
- Ensure Python is installed and added to PATH
- Try using `python3` instead of `python`
- On Windows, reinstall Python with "Add to PATH" checked

#### Permission denied

```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
- Use virtual environment (recommended)
- Or use `pip install --user -e .`
- Or run with `sudo` (not recommended)

#### Module not found

```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
- Ensure you're in the project directory
- Activate the virtual environment
- Reinstall with `pip install -e .`

#### pip version outdated

```
WARNING: pip is configured with locations that require TLS/SSL
```

**Solution:**
```bash
pip install --upgrade pip
```

#### Virtual environment issues

```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Getting Help

If you encounter issues:

1. Check the [FAQ](faq.md)
2. Search [GitHub Issues](https://github.com/ahmedmshakil/modular-log-analysis-toolkit/issues)
3. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Error message
   - Steps to reproduce

## Next Steps

After installation:

1. Read the [Quick Start Guide](quickstart.md)
2. Try the [CLI Usage](cli-usage.md)
3. Explore the [Python API](python-api.md)
4. Set up the [Web Dashboard](dashboard.md)
