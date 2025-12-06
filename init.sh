#!/bin/bash
# Agent Composer - Development Environment Setup Script
# This script is a user-friendly wrapper around the Makefile

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if make is available
check_make() {
    if ! command -v make &> /dev/null; then
        echo -e "${RED}Error: 'make' is required but not installed.${NC}"
        echo "Please install make and try again."
        exit 1
    fi
}

# Display banner
show_banner() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Agent Composer - Development Setup${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Check prerequisites with nice output
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
        echo -e "${YELLOW}⚠ Bun not found. Install from https://bun.sh${NC}"
        echo -e "${YELLOW}  Run: curl -fsSL https://bun.sh/install | bash${NC}"
        exit 1
    fi

    # Check make
    if command -v make &> /dev/null; then
        echo -e "${GREEN}✓ Make found${NC}"
    else
        echo -e "${RED}✗ Make not found. Please install make.${NC}"
        exit 1
    fi

    echo ""
}

# Show success message after dev servers start
show_dev_info() {
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
}

# Parse command line arguments
case "${1:-}" in
    "setup")
        show_banner
        check_prerequisites
        make setup-env
        make install
        echo -e "${GREEN}Setup complete! Run './init.sh' to start the servers.${NC}"
        ;;
    "install")
        show_banner
        check_prerequisites
        make install
        ;;
    "backend")
        show_banner
        make dev-backend
        ;;
    "frontend")
        show_banner
        make dev-frontend
        ;;
    "dev")
        show_banner
        show_dev_info
        make dev
        ;;
    "test")
        make test
        ;;
    "lint")
        make lint
        ;;
    "build")
        make build
        ;;
    "clean")
        echo -e "${YELLOW}Cleaning up...${NC}"
        make clean
        echo -e "${GREEN}Cleanup complete.${NC}"
        ;;
    "help"|"--help"|"-h")
        echo "Usage: ./init.sh [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Setup and start both backend and frontend"
        echo "  setup      Install dependencies and setup environment"
        echo "  install    Install dependencies only"
        echo "  dev        Start both servers (alias for no args)"
        echo "  backend    Start only the backend server"
        echo "  frontend   Start only the frontend server"
        echo "  test       Run all tests"
        echo "  lint       Lint all code"
        echo "  build      Build for production"
        echo "  clean      Remove generated files and dependencies"
        echo "  help       Show this help message"
        echo ""
        echo "Or use make directly:"
        echo "  make help  Show all available make targets"
        ;;
    *)
        show_banner
        check_prerequisites

        # Check if dependencies are installed
        if [ ! -d "backend/venv" ] || [ ! -d "frontend/node_modules" ]; then
            echo -e "${YELLOW}Dependencies not installed. Running setup...${NC}"
            echo ""
            make setup-env
            make install
        fi

        show_dev_info
        make dev
        ;;
esac
