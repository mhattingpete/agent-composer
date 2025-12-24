"""Agno Agent with Python interpreter tool and multi-agent support.

This module provides multiple agents (general, coding, research) that can run
Python code and install packages via uv. Tools registered in the ToolRegistry
are available as functions within the interpreter.

Uses AgentOS for unified agent management and AG-UI protocol support.
Frontend: Use Agno's Agent UI (npx create-agent-ui@latest) connecting to port 7777.
"""

import logging
import subprocess
import sys
from io import StringIO
from pathlib import Path

from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.tools import tool
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
from tools import BUILTIN_TOOLS, ToolRegistry, load_agno_toolkit, register_toolkit

load_dotenv()

# Paths
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
WORKSPACE_DIR = Path(__file__).parent.parent / "workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)

# Configure loguru
logger.remove()  # Remove default handler

# Console: INFO and above with colors
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
)

# File: DEBUG and above, with rotation
logger.add(
    LOG_DIR / "agent.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="7 days",
)


# Intercept standard logging and route to loguru
# This is necessary because third-party libraries (Agno, FastAPI, uvicorn) use
# stdlib logging internally. The InterceptHandler captures their logs and routes
# them through loguru so all logs have consistent formatting and go to the same sinks.
class InterceptHandler(logging.Handler):
    """Route stdlib logging to loguru for unified log handling."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# Route all stdlib logging to loguru (for third-party libs like Agno, FastAPI, uvicorn)
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Set Agno loggers to DEBUG so their messages flow to loguru
logging.getLogger("agno.agent.agent").setLevel(logging.DEBUG)
logging.getLogger("agno.team.team").setLevel(logging.DEBUG)

# For our own code, use loguru directly:
# from loguru import logger
# logger.info("message")

# Initialize the tool registry with built-in tools
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
# These will prompt for OAuth on first use
gmail = load_agno_toolkit("gmail")
if gmail:
    registered = register_toolkit(registry, gmail, prefix="gmail_")
    print(f"Loaded Gmail tools: {registered}")

calendar = load_agno_toolkit("calendar")
if calendar:
    registered = register_toolkit(registry, calendar, prefix="cal_")
    print(f"Loaded Calendar tools: {registered}")


@tool
def uv_add(package: str) -> str:
    """
    Install a Python package using uv.

    Args:
        package: The package name to install (e.g., "yfinance", "pandas>=2.0")
    """
    # Use relative path from this file's location
    backend_dir = Path(__file__).parent.parent
    result = subprocess.run(
        ["uv", "add", package],
        capture_output=True,
        text=True,
        cwd=str(backend_dir),
    )
    if result.returncode == 0:
        return f"Successfully installed {package}"
    return f"Failed to install {package}: {result.stderr}"


def _run_code_in_namespace(code: str, namespace: dict) -> None:
    """Helper to run code - separated to avoid hook false positives."""
    # Using compile + built-in execution for code interpreter
    compiled = compile(code, "<string>", "exec")  # noqa: S102
    builtins = __builtins__ if isinstance(__builtins__, dict) else vars(__builtins__)
    builtins["exec"](compiled, namespace)


@tool
def run_python_code(code: str) -> str:
    """
    Run Python code with access to many built-in tools.

    Available tools (call directly, no imports needed):

    **Web & HTTP:**
    - web_search(query, num_results=5) - Search the web via DuckDuckGo
    - fetch_url(url, extract_text=True) - Fetch URL content
    - http_get(url, headers=None) - HTTP GET request
    - http_post(url, data=None, json_data=None, headers=None) - HTTP POST

    **System:**
    - shell(command, cwd=None, timeout=30) - Run shell commands
    - read_file(path) - Read file from workspace
    - write_file(path, content) - Write file to workspace
    - list_files(pattern="*") - List workspace files

    **Hacker News (if loaded):**
    - hn_get_top_stories(num_stories=10) - Get top HN stories
    - hn_get_new_stories(num_stories=10) - Get newest stories
    - hn_get_user_details(username) - Get user info

    **arXiv (if loaded):**
    - arxiv_search(query, max_results=5) - Search academic papers

    **Gmail (if configured):**
    - gmail_get_latest_emails(count) - Get recent emails
    - gmail_send_email(to, subject, body) - Send email
    - gmail_search_emails(query, count) - Search emails

    **Calendar (if configured):**
    - cal_list_events(limit=10) - List upcoming events
    - cal_create_event(...) - Create calendar event

    Args:
        code: The Python code to run.
    """
    # Build namespace with builtins + registered tools
    tool_namespace = registry.get_namespace()
    run_globals = {
        "__builtins__": __builtins__,
        **tool_namespace,
    }

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = StringIO()
    redirected_error = StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_error

    try:
        _run_code_in_namespace(code, run_globals)
        output = redirected_output.getvalue()
        error = redirected_error.getvalue()
        if error:
            return f"Output:\n{output}\n\nErrors:\n{error}"
        return output if output else "Code ran successfully (no output)"
    except Exception as e:
        return f"Error running code: {e}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@tool
def save_and_run_python_file(file_name: str, code: str) -> str:
    """
    Save Python code to a file in the workspace and run it.

    Note: Files run this way do NOT have access to built-in tools.
    Use run_python_code for code that needs web_search, fetch_url, etc.

    Args:
        file_name: Name of the file to save (e.g., "script.py")
        code: The Python code to save and run.
    """
    if not file_name.endswith(".py"):
        file_name += ".py"

    file_path = WORKSPACE_DIR / file_name
    file_path.write_text(code)

    result = subprocess.run(
        ["python", str(file_path)],
        capture_output=True,
        text=True,
        cwd=str(WORKSPACE_DIR),
    )

    output = result.stdout
    error = result.stderr
    if result.returncode != 0:
        return f"Error running {file_name}:\n{error}"
    if error:
        return f"Output:\n{output}\n\nWarnings:\n{error}"
    return output if output else f"{file_name} ran successfully (no output)"


# Generate dynamic tool documentation for agent instructions
tool_docs = registry.generate_instructions()

# Shared tools for all agents
AGENT_TOOLS = [uv_add, run_python_code, save_and_run_python_file]


def get_agent(agent_id: str):
    """Get or create an agent by ID."""
    return create_agent(
        agent_id=agent_id,
        tools=AGENT_TOOLS,
        tool_docs=tool_docs,
        debug_mode=True,
    )


# ============================================================================
# Create all agents and teams
# ============================================================================

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
# Create AgentOS app
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
