# ==========================================================
# Vidhi - Makefile
# Common developer commands
# ==========================================================

PYTHON=python
PIP=pip
VENV=.venv
ACTIVATE=. $(VENV)/bin/activate

.PHONY: help setup install freeze run-api run-ui ingest build-vector test lint format clean

help:
	@echo "Vidhi - Available Commands"
	@echo "--------------------------------------"
	@echo "make setup         -> Create virtual environment"
	@echo "make install       -> Install dependencies"
	@echo "make freeze        -> Freeze requirements.txt"
	@echo "make run-api       -> Run FastAPI server"
	@echo "make run-ui        -> Run Streamlit UI"
	@echo "make ingest        -> Run ingestion pipeline"
	@echo "make build-vector  -> Build vector store index"
	@echo "make test          -> Run unit tests"
	@echo "make lint          -> Run lint checks"
	@echo "make format        -> Auto format code"
	@echo "make clean         -> Remove caches and temp files"

setup:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at $(VENV)"

install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

freeze:
	@echo "Freezing installed packages into requirements.txt..."
	$(PIP) freeze > requirements.txt

run-api:
	@echo "Starting FastAPI server..."
	$(PYTHON) -m src.api.main

run-ui:
	@echo "Starting Streamlit UI..."
	streamlit run src/ui/streamlit_app.py

ingest:
	@echo "Running ingestion pipeline..."
	$(PYTHON) -m src.ingestion.pipelines.ingestion_runner

build-vector:
	@echo "Building vector store..."
	$(PYTHON) scripts/build_vectorstore.py

test:
	@echo "Running tests..."
	pytest -v

lint:
	@echo "Running lint checks..."
	ruff check src tests

format:
	@echo "Formatting code..."
	black src tests

clean:
	@echo "Cleaning caches and temporary files..."
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf src/__pycache__ tests/__pycache__
	rm -rf *.log logs/*.log
