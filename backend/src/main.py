"""Agno Agent with Python interpreter tool and multi-agent support.

This module provides multiple agents (general, coding, research) that can run
Python code and install packages via uv. Tools registered in the ToolRegistry
are available as functions within the interpreter.

Uses AgentOS for unified agent management and AG-UI protocol support.
Frontend: Use Agno's Agent UI (npx create-agent-ui@latest) connecting to port 7777.
"""

import sys
from pathlib import Path

from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from dotenv import load_dotenv
from loguru import logger

# Ensure src directory is in path for uvicorn imports
_src_dir = str(Path(__file__).parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from agents import (
    AGENT_CONFIGS,
    TEAM_CONFIGS,
    TEAMS,
    create_agent,
    create_team,
)
from code_tools import AGENT_TOOLS, set_tool_registry
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
# Agent and Team Creation
# ============================================================================


def get_agent(agent_id: str):
    """Get or create an agent by ID."""
    return create_agent(
        agent_id=agent_id,
        tools=AGENT_TOOLS,
        tool_docs=tool_docs,
        debug_mode=True,
    )


# Create agent instances
agents = [get_agent(agent_id) for agent_id in AGENT_CONFIGS]

# Create team instances
teams = []
for team_id in TEAM_CONFIGS:
    team = create_team(team_id, tools=AGENT_TOOLS, tool_docs=tool_docs)
    TEAMS[team_id] = team
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

logger.info(f"AgentOS initialized with {len(agents)} agents and {len(teams)} teams")
logger.info("Agent UI: npx create-agent-ui@latest (connects to localhost:7777)")


if __name__ == "__main__":
    # Serve with AgentOS on port 7777 (Agent UI default)
    agent_os.serve(app="main:app", port=7777, reload=True)
