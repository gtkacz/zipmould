.PHONY: help be fe dev install dev-stop paper paper-verify paper-smoke paper-run paper-restore-test paper-analyze paper-reproduce paper-figures paper-build paper-check paper-journal paper-package

SHELL := /bin/bash
BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 5173
PYTHON ?= .venv/bin/python
TYPST ?= typst
TYPST_CREATION_TIMESTAMP ?= 1784251538
PAPER_ANALYSIS_OUT ?= /tmp/zipmould-confirmatory-analysis

help:
	@echo "Available targets:"
	@echo "  make be          - Run backend only (FastAPI server with auto-reload)"
	@echo "  make fe          - Run frontend only (Vite dev server)"
	@echo "  make dev         - Run both backend and frontend concurrently"
	@echo "  make dev-stop    - Stop any lingering background processes"
	@echo "  make install     - Install dependencies for both BE and FE"
	@echo "  make paper-verify - Verify frozen Challenge v1 protocol without opening test"
	@echo "  make paper-smoke  - Run both confirmatory arms on a tiny public-dev subset"
	@echo "  make paper-run    - FINAL ONLY: execute the tagged, unlocked confirmatory grid"
	@echo "  make paper-restore-test - Restore released test files to the ignored runtime path"
	@echo "  make paper-analyze - Analyze the complete frozen confirmatory result"
	@echo "  make paper-reproduce - Independently regenerate and compare frozen analysis"
	@echo "  make paper        - Regenerate, compile, and audit the manuscript package"
	@echo ""
	@echo "Environment variables:"
	@echo "  BACKEND_HOST     - Backend host (default: 127.0.0.1)"
	@echo "  BACKEND_PORT     - Backend port (default: 8000)"
	@echo "  FRONTEND_PORT    - Frontend port (default: 5173)"
	@echo ""
	@echo "Example usage:"
	@echo "  make install     # First time: install dependencies"
	@echo "  make dev         # Run both backend and frontend"

# Run backend only (with uv venv activated)
be:
	@. "$$(uv venv)" && uv run zipmould viz serve --host $(BACKEND_HOST) --port $(BACKEND_PORT) --reload

# Run frontend only
fe:
	@cd viz-web && bun run dev -- --port $(FRONTEND_PORT)

# Run both backend and frontend concurrently
dev:
	@echo "Starting backend on http://$(BACKEND_HOST):$(BACKEND_PORT)"
	@echo "Starting frontend on http://localhost:$(FRONTEND_PORT)"
	@echo "Press Ctrl+C to stop both services"
	@echo ""
	@(. "$$(uv venv)" && uv run zipmould viz serve --host $(BACKEND_HOST) --port $(BACKEND_PORT) --reload) & \
	(cd viz-web && bun run dev -- --port $(FRONTEND_PORT)) & \
	wait

# Stop any lingering background processes
dev-stop:
	@pkill -f "uvicorn" || true
	@pkill -f "vite" || true
	@echo "Stopped backend and frontend processes"

# Install dependencies for both backend and frontend
install:
	@echo "Installing backend dependencies..."
	uv sync --extra viz
	@echo "Installing frontend dependencies..."
	cd viz-web && bun install
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Run 'make dev' to start both backend and frontend"

paper-verify:
	$(PYTHON) -m experiments.challenge_v1.run verify

paper-smoke:
	$(PYTHON) -m experiments.challenge_v1.run smoke --workers 2

paper-run:
	$(PYTHON) -m experiments.challenge_v1.run run

paper-restore-test:
	$(PYTHON) paper/scripts/restore_test_release.py

paper-analyze: paper-restore-test
	$(PYTHON) -m experiments.challenge_v1.analyze --results paper/results/challenge-v1/results.parquet --out-dir $(PAPER_ANALYSIS_OUT)

paper-reproduce: paper-analyze
	cmp paper/results/challenge-v1/report.json $(PAPER_ANALYSIS_OUT)/report.json
	cmp paper/results/challenge-v1/report.md $(PAPER_ANALYSIS_OUT)/report.md
	cmp paper/results/challenge-v1/puzzle_effects.parquet $(PAPER_ANALYSIS_OUT)/puzzle_effects.parquet
	cmp paper/results/challenge-v1/primary_bootstrap.parquet $(PAPER_ANALYSIS_OUT)/primary_bootstrap.parquet

paper-figures:
	$(PYTHON) paper/scripts/make_figures.py

paper-build: paper-figures
	$(TYPST) compile --creation-timestamp $(TYPST_CREATION_TIMESTAMP) paper/main.typ paper/main.pdf

paper-check: paper-build paper-reproduce
	$(PYTHON) paper/scripts/check_manuscript.py

paper: paper-check

paper-journal: paper-check
	$(PYTHON) paper/scripts/secondary_analysis.py
	$(PYTHON) paper/scripts/export_natural_computing.py
	cd paper/natural-computing && latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
	cp paper/natural-computing/build/main.pdf paper/natural-computing/main.pdf
	$(PYTHON) paper/scripts/check_journal.py

paper-package: paper-journal
	$(PYTHON) paper/scripts/package_submission.py
