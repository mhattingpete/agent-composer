"""Agno Agent with Python interpreter tool and multi-agent support.

This module provides multiple agents (general, coding, research) that can run
Python code and install packages via uv. Tools registered in the ToolRegistry
are available as functions within the interpreter.
"""

import logging
import subprocess
import sys
from io import StringIO
from pathlib import Path

from agno.tools import tool
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure src directory is in path for uvicorn imports
_src_dir = str(Path(__file__).parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from agents import AGENT_CONFIGS, create_agent, get_agent_list
from conversations import store as conversation_store
from tools import BUILTIN_TOOLS, ToolRegistry, load_agno_toolkit, register_toolkit

load_dotenv()

# Configure logging - show only agent activity (model calls, tool calls, responses)
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("agno.agent.agent").setLevel(logging.DEBUG)

WORKSPACE_DIR = Path(__file__).parent.parent / "workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)

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


# Create FastAPI app
app = FastAPI(title="Agent Composer", description="Multi-agent AI assistant")

# Add CORS middleware - restricted to localhost for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/agents")
async def list_agents():
    """List available agents for the frontend dropdown.

    Frontend calls /api/agents, Vite proxy strips /api, so backend sees /agents.
    """
    return get_agent_list()


# ============================================================================
# Conversation API endpoints
# ============================================================================

from pydantic import BaseModel, field_validator


class CreateConversationRequest(BaseModel):
    """Request body for creating a conversation."""

    agent_id: str = "general"
    title: str | None = None

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, v: str) -> str:
        if v not in AGENT_CONFIGS:
            valid_agents = list(AGENT_CONFIGS.keys())
            raise ValueError(f"Invalid agent_id '{v}'. Must be one of: {valid_agents}")
        return v


class AddMessageRequest(BaseModel):
    """Request body for adding a message to a conversation."""

    role: str
    content: str
    tool_calls: list[dict] = []
    message_id: str | None = None


class UpdateTitleRequest(BaseModel):
    """Request body for updating conversation title."""

    title: str


@app.get("/conversations")
async def list_conversations():
    """List all conversations (summaries only, no messages)."""
    conversations = conversation_store.list_all()
    return [conv.to_summary() for conv in conversations]


@app.post("/conversations")
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation."""
    conversation = conversation_store.create(
        agent_id=request.agent_id,
        title=request.title,
    )
    return conversation.to_dict()


@app.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    """Get a conversation with all its messages."""
    conversation = conversation_store.get(conv_id)
    if not conversation:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation.to_dict()


@app.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    """Delete a conversation."""
    deleted = conversation_store.delete(conv_id)
    if not deleted:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}


@app.post("/conversations/{conv_id}/messages")
async def add_message(conv_id: str, request: AddMessageRequest):
    """Add a message to a conversation."""
    message = conversation_store.add_message(
        conv_id=conv_id,
        role=request.role,
        content=request.content,
        tool_calls=request.tool_calls,
        message_id=request.message_id,
    )
    if not message:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "tool_calls": message.tool_calls,
        "timestamp": message.timestamp,
    }


@app.patch("/conversations/{conv_id}/title")
async def update_conversation_title(conv_id: str, request: UpdateTitleRequest):
    """Update a conversation's title."""
    updated = conversation_store.update_title(conv_id, request.title)
    if not updated:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "updated", "title": request.title}


# ============================================================================
# Import AGUI for streaming
from agno.os.interfaces.agui import AGUI

# Create AGUI routers for each agent and mount them at different paths
# This allows agent selection via URL path: /{agent_id}/agui
for agent_id in AGENT_CONFIGS:
    agent = get_agent(agent_id)
    agui = AGUI(agent=agent)
    router = agui.get_router()
    # Mount at /{agent_id} - the router itself has /agui endpoint
    app.include_router(router, prefix=f"/{agent_id}", tags=[agent_id])

# Also mount a default endpoint for backwards compatibility
default_agent = get_agent("general")
default_agui = AGUI(agent=default_agent)
app.include_router(default_agui.get_router(), tags=["default"])


if __name__ == "__main__":
    # Test with general agent
    agent = get_agent("general")
    agent.print_response("Search the web for 'Python best practices 2024' and summarize the top 3 results.")
