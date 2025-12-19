"""Built-in tools for the Python interpreter.

These tools are injected into the interpreter's namespace and can be
called directly from executed Python code.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

# Default workspace directory - can be overridden
WORKSPACE_DIR = Path(__file__).parent.parent.parent / "workspace"


def web_search(query: str, num_results: int = 5) -> str:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string
        num_results: Number of results to return (default 5)

    Returns:
        JSON string of search results with title, url, snippet
    """
    try:
        from ddgs import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                results.append({"title": r["title"], "url": r["href"], "snippet": r["body"]})
        return json.dumps(results, indent=2)
    except ImportError:
        return json.dumps({"error": "ddgs not installed. Run: uv add ddgs"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def fetch_url(url: str, extract_text: bool = True) -> str:
    """Fetch content from a URL.

    Args:
        url: The URL to fetch
        extract_text: If True, extract readable text from HTML (default True)

    Returns:
        Page content as text
    """
    try:
        response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")

        if extract_text and "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove non-content elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            return soup.get_text(separator="\n", strip=True)

        return response.text
    except Exception as e:
        return f"Error fetching URL: {e}"


def shell(command: str, cwd: str | None = None, timeout: int = 30) -> str:
    """Run a shell command.

    Args:
        command: Command to run
        cwd: Working directory (default: workspace)
        timeout: Timeout in seconds (default 30)

    Returns:
        Command output (stdout + stderr)
    """
    try:
        work_dir = Path(cwd) if cwd else WORKSPACE_DIR
        result = subprocess.run(
            command,
            shell=True,  # noqa: S602 - Intentional for interpreter tool
            capture_output=True,
            text=True,
            cwd=str(work_dir),
            timeout=timeout,
        )

        output = result.stdout
        if result.stderr:
            output += f"\n\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n\nExit code: {result.returncode}"

        return output if output.strip() else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error running command: {e}"


def http_get(url: str, headers: dict[str, str] | None = None) -> str:
    """Make an HTTP GET request.

    Args:
        url: The URL to request
        headers: Optional headers dict

    Returns:
        JSON string with status, headers, and body
    """
    try:
        response = requests.get(url, headers=headers, timeout=30)
        return json.dumps(
            {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:10000],  # Limit body size
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


def http_post(url: str, data: Any = None, json_data: dict | None = None, headers: dict[str, str] | None = None) -> str:
    """Make an HTTP POST request.

    Args:
        url: The URL to request
        data: Form data or string body
        json_data: JSON data (will set Content-Type automatically)
        headers: Optional headers dict

    Returns:
        JSON string with status, headers, and body
    """
    try:
        response = requests.post(url, data=data, json=json_data, headers=headers, timeout=30)
        return json.dumps(
            {
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:10000],  # Limit body size
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


def read_workspace_file(path: str) -> str:
    """Read a file from the workspace.

    Args:
        path: File path (relative to workspace)

    Returns:
        File contents
    """
    try:
        # Resolve the path and ensure it's within workspace (prevent path traversal)
        file_path = (WORKSPACE_DIR / path).resolve()
        workspace_resolved = WORKSPACE_DIR.resolve()

        if not file_path.is_relative_to(workspace_resolved):
            return f"Error: Path '{path}' is outside the workspace directory"

        if not file_path.exists():
            return f"File not found: {path}"

        return file_path.read_text()
    except Exception as e:
        return f"Error reading file: {e}"


def write_workspace_file(path: str, content: str) -> str:
    """Write content to a file in the workspace.

    Args:
        path: File path (relative to workspace)
        content: Content to write

    Returns:
        Success message or error
    """
    try:
        # Resolve the path and ensure it's within workspace (prevent path traversal)
        file_path = (WORKSPACE_DIR / path).resolve()
        workspace_resolved = WORKSPACE_DIR.resolve()

        if not file_path.is_relative_to(workspace_resolved):
            return f"Error: Path '{path}' is outside the workspace directory"

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

        return f"Successfully wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"


def list_workspace_files(pattern: str = "*") -> str:
    """List files in the workspace.

    Args:
        pattern: Glob pattern (default "*")

    Returns:
        Newline-separated list of file paths
    """
    try:
        files = list(WORKSPACE_DIR.glob(pattern))
        if not files:
            return f"No files matching '{pattern}' in workspace"
        return "\n".join(str(f.relative_to(WORKSPACE_DIR)) for f in sorted(files))
    except Exception as e:
        return f"Error listing files: {e}"


# Registry of all built-in tools with their descriptions
BUILTIN_TOOLS = {
    "web_search": (web_search, "Search the web using DuckDuckGo"),
    "fetch_url": (fetch_url, "Fetch content from a URL, optionally extracting text from HTML"),
    "shell": (shell, "Run a shell command"),
    "http_get": (http_get, "Make an HTTP GET request"),
    "http_post": (http_post, "Make an HTTP POST request"),
    "read_file": (read_workspace_file, "Read a file from the workspace"),
    "write_file": (write_workspace_file, "Write content to a file in the workspace"),
    "list_files": (list_workspace_files, "List files in the workspace"),
}
