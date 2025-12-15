"""Agno Agent with Python interpreter tool.

This agent can execute Python code and install packages via uv to accomplish tasks.
"""

import logging
import subprocess
import sys
from io import StringIO
from pathlib import Path

from agno.agent.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.tools import tool
from dotenv import load_dotenv

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


@tool
def uv_add(package: str) -> str:
    """
    Install a Python package using uv.

    Args:
        package: The package name to install (e.g., "yfinance", "pandas>=2.0")
    """
    result = subprocess.run(
        ["uv", "add", package],
        capture_output=True,
        text=True,
        cwd="/Users/map/Documents/Repos/agent-composer/backend",
    )
    if result.returncode == 0:
        return f"Successfully installed {package}"
    return f"Failed to install {package}: {result.stderr}"


@tool
def run_python_code(code: str) -> str:
    """
    Execute Python code and return the output.

    Args:
        code: The Python code to execute.
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = StringIO()
    redirected_error = StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_error

    try:
        exec(code, {"__builtins__": __builtins__})  # noqa: S102
        output = redirected_output.getvalue()
        error = redirected_error.getvalue()
        if error:
            return f"Output:\n{output}\n\nErrors:\n{error}"
        return output if output else "Code executed successfully (no output)"
    except Exception as e:
        return f"Error executing code: {e}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


@tool
def save_and_run_python_file(file_name: str, code: str) -> str:
    """
    Save Python code to a file in the workspace and run it.

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
    return output if output else f"{file_name} executed successfully (no output)"


@tool
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file (relative to workspace or absolute).
    """
    path = Path(file_path)
    if not path.is_absolute():
        path = WORKSPACE_DIR / path

    if not path.exists():
        return f"File not found: {file_path}"
    return path.read_text()


@tool
def list_files() -> str:
    """
    List files in the workspace directory.
    """
    files = list(WORKSPACE_DIR.glob("*"))
    if not files:
        return "Workspace is empty"
    return "\n".join(f.name for f in files)


agent = Agent(
    model=OpenRouter(id="mistralai/devstral-2512:free"),
    tools=[uv_add, run_python_code, save_and_run_python_file, read_file, list_files],
    description="You are a helpful AI assistant that executes tasks using Python scripts.",
    instructions="""Execute all tasks by writing and running Python scripts.

Use uv_add to install any needed packages first.
Use run_python_code to execute Python code directly.
Use save_and_run_python_file to save and run scripts that need to persist.

You can install and use any Python library, including Agno toolkits:
- agno.tools.yfinance.YFinanceTools for financial data
- agno.tools.googlesheets.GoogleSheetsTools for Google Sheets
- Any standard Python library (pandas, requests, etc.)

Format your response using markdown where appropriate.""",
    debug_mode=True,  # Enable Agno debug logging
)

agent_os = AgentOS(agents=[agent], interfaces=[AGUI(agent=agent)])

app = agent_os.get_app()


if __name__ == "__main__":
    agent.print_response("Share a 2 sentence horror story.")
