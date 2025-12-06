.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend clean clean-backend clean-frontend test test-backend test-frontend lint lint-backend lint-frontend build check-prereqs setup-env

# Default target
help:
	@echo "Agent Composer - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install all dependencies"
	@echo "  make install-backend  Install backend dependencies only"
	@echo "  make install-frontend Install frontend dependencies only"
	@echo "  make setup-env        Create .env files from templates"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start both backend and frontend"
	@echo "  make dev-backend      Start backend server only"
	@echo "  make dev-frontend     Start frontend server only"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-backend     Run backend tests only"
	@echo "  make test-frontend    Run frontend tests only"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Lint all code"
	@echo "  make lint-backend     Lint backend code"
	@echo "  make lint-frontend    Lint frontend code"
	@echo ""
	@echo "Build:"
	@echo "  make build            Build for production"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove all generated files"
	@echo "  make clean-backend    Remove backend generated files"
	@echo "  make clean-frontend   Remove frontend generated files"

# =============================================================================
# Prerequisites
# =============================================================================

check-prereqs:
	@echo "Checking prerequisites..."
	@command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed."; exit 1; }
	@command -v bun >/dev/null 2>&1 || { echo "Bun is required but not installed. Install from https://bun.sh"; exit 1; }
	@echo "All prerequisites satisfied."

# =============================================================================
# Environment Setup
# =============================================================================

setup-env:
	@echo "Setting up environment files..."
	@test -f .env || (test -f .env.example && cp .env.example .env && echo "Created .env from template")
	@test -f backend/.env || (test -f backend/.env.example && cp backend/.env.example backend/.env && echo "Created backend/.env from template")
	@test -f frontend/.env || (test -f frontend/.env.example && cp frontend/.env.example frontend/.env && echo "Created frontend/.env from template")
	@echo "Environment files ready. Edit .env to add your API keys."

# =============================================================================
# Installation
# =============================================================================

install: install-backend install-frontend
	@echo "All dependencies installed."

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && \
	python3 -m venv venv && \
	. venv/bin/activate && \
	pip install --upgrade pip setuptools wheel && \
	pip install -e ".[dev]"
	@echo "Backend dependencies installed."

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && bun install
	@echo "Frontend dependencies installed."

# =============================================================================
# Development Servers
# =============================================================================

dev:
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@$(MAKE) -j2 dev-backend dev-frontend

dev-backend:
	@echo "Starting backend server..."
	cd backend && \
	. venv/bin/activate && \
	python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend server..."
	cd frontend && bun run dev

# =============================================================================
# Testing
# =============================================================================

test: test-backend test-frontend
	@echo "All tests complete."

test-backend:
	@echo "Running backend tests..."
	cd backend && \
	. venv/bin/activate && \
	python -m pytest tests/ -v --cov=src

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && bun test

# =============================================================================
# Linting
# =============================================================================

lint: lint-backend lint-frontend
	@echo "Linting complete."

lint-backend:
	@echo "Linting backend..."
	cd backend && \
	. venv/bin/activate && \
	ruff check src/ && \
	ruff format --check src/

lint-frontend:
	@echo "Linting frontend..."
	cd frontend && bun run lint

# =============================================================================
# Build
# =============================================================================

build: build-frontend
	@echo "Build complete."

build-frontend:
	@echo "Building frontend..."
	cd frontend && bun run build

# =============================================================================
# Cleanup
# =============================================================================

clean: clean-backend clean-frontend
	@echo "Cleanup complete."
	rm -rf .tmp

clean-backend:
	@echo "Cleaning backend..."
	rm -rf backend/venv
	rm -rf backend/.venv
	rm -rf backend/__pycache__
	rm -rf backend/src/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf backend/.ruff_cache
	rm -rf backend/*.egg-info
	rm -rf backend/dist
	rm -rf backend/build
	rm -f backend/*.db

clean-frontend:
	@echo "Cleaning frontend..."
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf frontend/.cache
