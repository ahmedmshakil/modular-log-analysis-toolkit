.PHONY: test lint clean install venv activate dashboard help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	python3 -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate    (Linux/Mac)"
	@echo "  venv\\Scripts\\activate       (Windows)"

install: ## Install package in development mode (inside venv)
	pip install -e .

install-deps: ## Install optional dependencies (flask, pyyaml, requests, geoip2)
	pip install flask pyyaml requests geoip2

test: ## Run test suite
	pytest tests/ -v

lint: ## Run linter on source files
	python -m py_compile src/*.py

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run: ## Run analyzer on sample logs
	python -m src.cli test.log --summary

dashboard: ## Start web dashboard on port 8080
	python -c "from src.web import start_dashboard; from src.reader import read_log_lines; from src.parser import LogParser; p = LogParser(); e = p.parse_lines(list(read_log_lines('test.log'))); start_dashboard(port=8080, entries=e)"
