"""Agno Agent with Python interpreter tool and multi-agent support.

This module provides multiple agents (general, coding, research) that can run
Python code and install packages via uv. Tools registered in the ToolRegistry
are available as functions within the interpreter.

Uses AgentOS for unified agent management and AG-UI protocol support.
Frontend: Use Agno's Agent UI (npx create-agent-ui@latest) connecting to port 7777.
"""

import sys
from pathlib import Path

from agno.agent.agent import Agent
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.team import Team
from dotenv import load_dotenv
from loguru import logger

# Ensure src directory is in path for uvicorn imports
_src_dir = str(Path(__file__).parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from agents import (
    AGENT_CONFIGS,
    BUILTIN_AGENT_CONFIGS,
    BUILTIN_TEAM_CONFIGS,
    TEAM_CONFIGS,
    TEAMS,
    create_agent,
    create_team,
    get_all_agent_configs,
    get_all_team_configs,
    load_custom_agents,
    load_custom_teams,
)
from code_tools import AGENT_TOOLS, set_tool_registry
from config_routes import router as config_router
from logging_config import setup_logging
from tools import BUILTIN_TOOLS, ToolRegistry, load_agno_toolkit, register_toolkit

load_dotenv()

# Configure logging
setup_logging()

# ============================================================================
# Tool Registry Setup
# ============================================================================

registry = ToolRegistry()
for name, (func, description) in BUILTIN_TOOLS.items():
    registry.register(name, func, description)

# Load Agno toolkits (no credentials required)
hackernews = load_agno_toolkit("hackernews")
if hackernews:
    registered = register_toolkit(registry, hackernews, prefix="hn_")
    print(f"Loaded HackerNews tools: {registered}")

arxiv = load_agno_toolkit("arxiv")
if arxiv:
    registered = register_toolkit(registry, arxiv, prefix="arxiv_")
    print(f"Loaded arXiv tools: {registered}")

# Load Google toolkits (requires GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_PROJECT_ID)
gmail = load_agno_toolkit("gmail")
if gmail:
    registered = register_toolkit(registry, gmail, prefix="gmail_")
    print(f"Loaded Gmail tools: {registered}")

calendar = load_agno_toolkit("calendar")
if calendar:
    registered = register_toolkit(registry, calendar, prefix="cal_")
    print(f"Loaded Calendar tools: {registered}")

# Connect registry to code tools
set_tool_registry(registry)

# Generate dynamic tool documentation for agent instructions
tool_docs = registry.generate_instructions()

# ============================================================================
# Dynamic Agent/Team Cache
# ============================================================================

# Cache for dynamically created agents and teams
_dynamic_agents: dict[str, Agent] = {}
_dynamic_teams: dict[str, Team] = {}


def get_or_create_agent(agent_id: str) -> Agent:
    """Get an agent by ID, creating it dynamically if needed.

    This enables hot-loading of custom agents without server restart.
    Built-in agents are created once and cached.
    Custom agents are created on first request and cached.
    """
    # Check cache first
    if agent_id in _dynamic_agents:
        return _dynamic_agents[agent_id]

    # Create the agent (works for both built-in and custom)
    agent = create_agent(
        agent_id=agent_id,
        tools=AGENT_TOOLS,
        tool_docs=tool_docs,
        debug_mode=True,
    )
    _dynamic_agents[agent_id] = agent
    return agent


def get_or_create_team(team_id: str) -> Team:
    """Get a team by ID, creating it dynamically if needed."""
    if team_id in _dynamic_teams:
        return _dynamic_teams[team_id]

    team = create_team(team_id, tools=AGENT_TOOLS, tool_docs=tool_docs)
    _dynamic_teams[team_id] = team
    return team


def is_custom_agent(agent_id: str) -> bool:
    """Check if an agent ID refers to a custom (non-built-in) agent."""
    return agent_id not in BUILTIN_AGENT_CONFIGS


def is_custom_team(team_id: str) -> bool:
    """Check if a team ID refers to a custom (non-built-in) team."""
    return team_id not in BUILTIN_TEAM_CONFIGS


# ============================================================================
# Agent and Team Creation (for AgentOS initialization)
# ============================================================================


def get_agent(agent_id: str):
    """Get or create an agent by ID."""
    return create_agent(
        agent_id=agent_id,
        tools=AGENT_TOOLS,
        tool_docs=tool_docs,
        debug_mode=True,
    )


# Create agent instances for built-in agents only (custom loaded dynamically)
agents = []
for agent_id in AGENT_CONFIGS:
    agent = get_agent(agent_id)
    agents.append(agent)
    _dynamic_agents[agent_id] = agent  # Cache using config ID

# Create team instances
teams = []
for team_id in TEAM_CONFIGS:
    team = create_team(team_id, tools=AGENT_TOOLS, tool_docs=tool_docs)
    TEAMS[team_id] = team
    _dynamic_teams[team_id] = team
    teams.append(team)

# Create AGUI interfaces for all agents and teams
interfaces = []
for agent in agents:
    interfaces.append(AGUI(agent=agent))
for team in teams:
    interfaces.append(AGUI(team=team))

# ============================================================================
# AgentOS Application
# ============================================================================

agent_os = AgentOS(
    agents=agents,
    teams=teams,
    interfaces=interfaces,
)

# Get the FastAPI app from AgentOS
app = agent_os.get_app()

# Add config routes for managing agents and teams
app.include_router(config_router)

logger.info(f"AgentOS initialized with {len(agents)} agents and {len(teams)} teams")
logger.info("Agent UI: npx create-agent-ui@latest (connects to localhost:7777)")


if __name__ == "__main__":
    # Serve with AgentOS on port 7777 (Agent UI default)
    agent_os.serve(app="main:app", port=7777, reload=True)
