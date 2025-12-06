"""FastAPI application entry point for Agent Composer."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown."""
    # Startup: Initialize database, load built-in agents
    print("Starting Agent Composer backend...")
    # TODO: Initialize database connection
    # TODO: Load built-in agents
    yield
    # Shutdown: Cleanup resources
    print("Shutting down Agent Composer backend...")


app = FastAPI(
    title="Agent Composer",
    description="A local-first platform for designing, composing, and interacting with multi-agent AI systems",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "agent-composer"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": "Agent Composer API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# API routers will be mounted here as they are implemented
# app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
# app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
# app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp"])
# app.include_router(generate.router, prefix="/api/generate", tags=["generate"])
