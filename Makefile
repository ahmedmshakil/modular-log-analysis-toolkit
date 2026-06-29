.PHONY: test lint clean install help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install package in development mode
	pip install -e .

test: ## Run test suite
	pytest tests/ -v

lint: ## Run linter on source files
	python -m py_compile src/*.py

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run: ## Run analyzer on sample logs
	python -m src.cli config/settings.yaml --summary
