.PHONY: help install install-dev test test-unit test-api run clean

help:
	@echo "Available commands:"
	@echo "  install     - Install the package"
	@echo "  install-dev - Install package with development dependencies"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-api    - Run API tests only"
	@echo "  run         - Start the server"
	@echo "  clean       - Clean build artifacts"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

run:
	python scripts/run_server.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete 