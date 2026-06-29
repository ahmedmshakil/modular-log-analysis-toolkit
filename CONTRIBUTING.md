# Contributing to sk-loganalyzer

Thank you for your interest in contributing to sk-loganalyzer!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-username>/sk-loganalyzer.git`
3. Create a branch: `git checkout -b feature/my-feature`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit and push
7. Open a Pull Request

## Development Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
pip install pytest
```

## Code Style

- Follow PEP 8 conventions
- Use type hints for function signatures
- Add docstrings to all public classes and methods
- Keep functions focused and small

## Testing

- Write unit tests for new features
- Ensure all existing tests pass before submitting
- Aim for meaningful coverage, not just line count

## Reporting Issues

- Use GitHub Issues for bug reports
- Include steps to reproduce
- Mention your Python version and OS

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
