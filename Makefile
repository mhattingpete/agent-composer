.PHONY: install install-backend install-frontend dev dev-backend dev-frontend build lint test test-backend test-e2e clean \
       model model-deepseek model-qwen

# Install all dependencies
install: install-backend install-frontend

install-backend:
	cd backend && uv sync

install-frontend:
	cd frontend && bun install

# Development servers (run both concurrently)
dev:
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend:
	cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && bun run dev

# Build
build:
	cd frontend && bun run build

# Linting
lint:
	cd backend && uv run ruff check src
	cd frontend && bun run lint

lint-fix:
	cd backend && uv run ruff check --fix src

# Testing
test: test-backend

test-backend:
	cd backend && uv run pytest tests/test_agui.py -v

test-e2e:
	@echo "Running E2E tests (requires both backend on :8000 and frontend on :3001)..."
	cd backend && uv run pytest tests/test_e2e.py -v --browser chromium

test-e2e-headed:
	cd backend && uv run pytest tests/test_e2e.py -v --browser chromium --headed

test-all: test-backend test-e2e

# Clean
clean:
	rm -rf frontend/dist frontend/node_modules
	rm -rf backend/.venv backend/__pycache__ backend/src/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# =============================================================================
# LLM Model Management
# =============================================================================

model-deepseek:
	@echo "Starting DeepSeek R1 Distill 7B... Logs: backend/logs/llama-server.log"
	llama-server --jinja -hf unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF:Q4_K_M 2>&1 | tee logs/llama-server.log
	#cd backend && uv run python scripts/run_model.py unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf 2>&1 | tee logs/llama-server.log

model-gpt-oss:
	@echo "Starting GPT-OSS 20B... Logs: backend/logs/llama-server.log"
	llama-server --jinja -hf unsloth/gpt-oss-20b-GGUF:Q4_K_M 2>&1 | tee logs/llama-server.log

# Generic model runner - usage: make model MODEL=<hf-model-path>
MODEL ?= unsloth/DeepSeek-R1-Distill-Qwen-14B-GGUF:Q4_K_M
model:
	@echo "Starting $(MODEL)... Logs: backend/logs/llama-server.log"
	llama-server --jinja -hf $(MODEL) 2>&1 | tee logs/llama-server.log
