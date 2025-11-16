.PHONY: install test clean format lint build publish help

# Default target
help:
	@echo "Available targets:"
	@echo "  install - Install package in development mode"
	@echo "  test    - Run tests"
	@echo "  clean   - Clean build artifacts"
	@echo "  format  - Format code with Black"
	@echo "  lint    - Lint code with Flake8"
	@echo "  build   - Build package"
	@echo "  publish - Publish to PyPI (maintainers only)"

install:
	pip install -e .[dev]

test:
	python -m pytest tests/ -v

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/

format:
	black src/ tests/ scripts/

lint:
	flake8 src/ tests/ scripts/

build:
	python -m build

publish: clean build
	twine upload dist/*