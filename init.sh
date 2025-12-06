#!/bin/bash
# Agent Composer - Development Environment Setup Script
# This script initializes and starts the development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Agent Composer - Development Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
    else
        echo -e "${RED}✗ Python 3 not found. Please install Python 3.11+${NC}"
        exit 1
    fi

    # Check Bun
    if command -v bun &> /dev/null; then
        BUN_VERSION=$(bun --version)
        echo -e "${GREEN}✓ Bun ${BUN_VERSION} found${NC}"
    else
        echo -e "${RED}✗ Bun not found. Installing Bun...${NC}"
        curl -fsSL https://bun.sh/install | bash
        source ~/.bashrc 2>/dev/null || source ~/.zshrc 2>/dev/null
    fi

    # Check uv (Python package manager)
    if command -v uv &> /dev/null; then
        echo -e "${GREEN}✓ uv package manager found${NC}"
    else
        echo -e "${YELLOW}Installing uv package manager...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    echo ""
}

# Setup environment files
setup_env() {
    echo -e "${YELLOW}Setting up environment files...${NC}"

    # Backend .env
    if [ ! -f "backend/.env" ]; then
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            echo -e "${GREEN}✓ Created backend/.env from template${NC}"
        fi
    else
        echo -e "${GREEN}✓ backend/.env already exists${NC}"
    fi

    # Frontend .env
    if [ ! -f "frontend/.env" ]; then
        if [ -f "frontend/.env.example" ]; then
            cp frontend/.env.example frontend/.env
            echo -e "${GREEN}✓ Created frontend/.env from template${NC}"
        fi
    else
        echo -e "${GREEN}✓ frontend/.env already exists${NC}"
    fi

    # Root .env
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${GREEN}✓ Created .env from template${NC}"
            echo -e "${YELLOW}⚠ Please edit .env and add your API keys${NC}"
        fi
    else
        echo -e "${GREEN}✓ .env already exists${NC}"
    fi

    echo ""
}

# Setup backend
setup_backend() {
    echo -e "${YELLOW}Setting up backend...${NC}"

    cd backend

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi

    # Install dependencies
    if [ -f "pyproject.toml" ]; then
        echo "Installing Python dependencies with uv..."
        uv pip install -e ".[dev]" 2>/dev/null || pip install -e ".[dev]" 2>/dev/null || pip install -r requirements.txt
    elif [ -f "requirements.txt" ]; then
        echo "Installing Python dependencies..."
        pip install -r requirements.txt
    fi

    echo -e "${GREEN}✓ Backend setup complete${NC}"
    cd ..
    echo ""
}

# Setup frontend
setup_frontend() {
    echo -e "${YELLOW}Setting up frontend...${NC}"

    cd frontend

    # Install dependencies
    if [ -f "package.json" ]; then
        echo "Installing Node dependencies with Bun..."
        bun install
    fi

    echo -e "${GREEN}✓ Frontend setup complete${NC}"
    cd ..
    echo ""
}

# Start services
start_services() {
    echo -e "${YELLOW}Starting development servers...${NC}"
    echo ""

    # Create a temporary directory for PIDs
    mkdir -p .tmp

    # Start backend
    echo -e "${BLUE}Starting backend server...${NC}"
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi

    # Start backend in background
    if [ -f "src/main.py" ]; then
        python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
        echo $! > ../.tmp/backend.pid
    else
        echo -e "${RED}Backend main.py not found. Skipping backend start.${NC}"
    fi
    cd ..

    # Start frontend
    echo -e "${BLUE}Starting frontend server...${NC}"
    cd frontend
    if [ -f "package.json" ]; then
        bun run dev &
        echo $! > ../.tmp/frontend.pid
    else
        echo -e "${RED}Frontend package.json not found. Skipping frontend start.${NC}"
    fi
    cd ..

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Development Environment Ready!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "  ${BLUE}Backend:${NC}  http://localhost:8000"
    echo -e "  ${BLUE}Frontend:${NC} http://localhost:5173"
    echo -e "  ${BLUE}API Docs:${NC} http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
    echo ""

    # Wait for interrupt
    trap cleanup INT
    wait
}

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"

    if [ -f ".tmp/backend.pid" ]; then
        kill $(cat .tmp/backend.pid) 2>/dev/null
        rm .tmp/backend.pid
    fi

    if [ -f ".tmp/frontend.pid" ]; then
        kill $(cat .tmp/frontend.pid) 2>/dev/null
        rm .tmp/frontend.pid
    fi

    echo -e "${GREEN}Servers stopped.${NC}"
    exit 0
}

# Parse command line arguments
case "${1:-}" in
    "setup")
        check_prerequisites
        setup_env
        setup_backend
        setup_frontend
        echo -e "${GREEN}Setup complete! Run './init.sh' to start the servers.${NC}"
        ;;
    "backend")
        setup_backend
        cd backend
        source venv/bin/activate 2>/dev/null || source .venv/bin/activate
        python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    "frontend")
        setup_frontend
        cd frontend
        bun run dev
        ;;
    "clean")
        echo -e "${YELLOW}Cleaning up...${NC}"
        rm -rf backend/venv backend/.venv
        rm -rf frontend/node_modules
        rm -rf .tmp
        echo -e "${GREEN}Cleanup complete.${NC}"
        ;;
    "help"|"--help"|"-h")
        echo "Usage: ./init.sh [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Setup and start both backend and frontend"
        echo "  setup      Only run setup without starting servers"
        echo "  backend    Start only the backend server"
        echo "  frontend   Start only the frontend server"
        echo "  clean      Remove virtual environments and node_modules"
        echo "  help       Show this help message"
        ;;
    *)
        check_prerequisites
        setup_env
        setup_backend
        setup_frontend
        start_services
        ;;
esac
