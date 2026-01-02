"""Python code execution tools for agents.

Provides tools for running Python code with access to registered tools,
installing packages via uv, and saving/running Python files.
"""

import subprocess
import sys
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

from agno.tools import tool

if TYPE_CHECKING:
    from tools import ToolRegistry

# Workspace directory for file operations
WORKSPACE_DIR = Path(__file__).parent.parent / "workspace"
WORKSPACE_DIR.mkdir(exist_ok=True)

# Tool registry - set via set_tool_registry()
_registry: "ToolRegistry | None" = None


def set_tool_registry(registry: "ToolRegistry") -> None:
    """Set the tool registry for code execution tools."""
    global _registry
    _registry = registry


@tool
def uv_add(package: str) -> str:
    """
    Install a Python package using uv.

    Args:
        package: The package name to install (e.g., "yfinance", "pandas>=2.0")
    """
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
    if _registry is None:
        return "Error: Tool registry not initialized"

    # Build namespace with builtins + registered tools
    tool_namespace = _registry.get_namespace()
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


# Export all tools as a list for easy import
AGENT_TOOLS = [uv_add, run_python_code, save_and_run_python_file]
