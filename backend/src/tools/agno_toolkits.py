"""Loader for Agno toolkits (Gmail, Google Calendar, etc.)

These are native Python toolkits from the Agno framework that wrap various APIs.
They require appropriate credentials to be set up (e.g., Google OAuth for Gmail/Calendar).
"""

import functools
from typing import TYPE_CHECKING, Any, Callable

from agno.tools import Toolkit

if TYPE_CHECKING:
    from tools.registry import ToolRegistry


def extract_toolkit_functions(toolkit: Toolkit) -> dict[str, tuple[Callable, str]]:
    """Extract callable functions from an Agno toolkit.

    Args:
        toolkit: An initialized Agno Toolkit instance

    Returns:
        Dict mapping function names to (callable, description) tuples
    """
    functions = {}
    for name, func in toolkit.functions.items():
        # Get the actual callable method from the toolkit
        if hasattr(func, "entrypoint"):
            callable_func = func.entrypoint
            description = func.description or f"{name} from {toolkit.name}"
        else:
            callable_func = func
            description = getattr(func, "__doc__", "") or f"{name} from {toolkit.name}"

        functions[name] = (callable_func, description)

    return functions


def register_toolkit(registry: "ToolRegistry", toolkit: Toolkit, prefix: str = "") -> list[str]:
    """Register all functions from an Agno toolkit into the registry.

    Args:
        registry: The ToolRegistry to register tools into
        toolkit: An initialized Agno Toolkit instance
        prefix: Optional prefix to add to tool names (e.g., "gmail_")

    Returns:
        List of registered tool names
    """
    registered = []
    functions = extract_toolkit_functions(toolkit)

    for name, (func, description) in functions.items():
        tool_name = f"{prefix}{name}" if prefix else name
        registry.register(tool_name, func, description)
        registered.append(tool_name)

    return registered


def create_gmail_tools(
    credentials_path: str | None = None,
    token_path: str | None = None,
) -> Toolkit | None:
    """Create Gmail toolkit if credentials are available.

    Requires environment variables:
    - GOOGLE_CLIENT_ID
    - GOOGLE_CLIENT_SECRET
    - GOOGLE_PROJECT_ID

    Args:
        credentials_path: Optional path to credentials.json file
        token_path: Optional path to store/load OAuth token

    Returns:
        GmailTools instance or None if dependencies not available
    """
    try:
        from agno.tools.gmail import GmailTools

        return GmailTools(
            credentials_path=credentials_path,
            token_path=token_path or "gmail_token.json",
        )
    except ImportError as e:
        print(f"Gmail tools not available: {e}")
        return None
    except Exception as e:
        print(f"Failed to create Gmail tools: {e}")
        return None


def create_calendar_tools(
    credentials_path: str | None = None,
    token_path: str | None = None,
    allow_update: bool = True,
) -> Toolkit | None:
    """Create Google Calendar toolkit if credentials are available.

    Requires environment variables:
    - GOOGLE_CLIENT_ID
    - GOOGLE_CLIENT_SECRET
    - GOOGLE_PROJECT_ID

    Args:
        credentials_path: Optional path to credentials.json file
        token_path: Optional path to store/load OAuth token
        allow_update: Whether to allow creating/updating/deleting events

    Returns:
        GoogleCalendarTools instance or None if dependencies not available
    """
    try:
        from agno.tools.googlecalendar import GoogleCalendarTools

        return GoogleCalendarTools(
            credentials_path=credentials_path,
            token_path=token_path or "calendar_token.json",
            allow_update=allow_update,
        )
    except ImportError as e:
        print(f"Google Calendar tools not available: {e}")
        return None
    except Exception as e:
        print(f"Failed to create Google Calendar tools: {e}")
        return None


def create_hackernews_tools() -> Toolkit | None:
    """Create Hacker News toolkit (no credentials needed).

    Returns:
        HackerNewsTools instance or None if not available
    """
    try:
        from agno.tools.hackernews import HackerNewsTools

        return HackerNewsTools()
    except ImportError as e:
        print(f"HackerNews tools not available: {e}")
        return None
    except Exception as e:
        print(f"Failed to create HackerNews tools: {e}")
        return None


def create_arxiv_tools() -> Toolkit | None:
    """Create arXiv toolkit for searching academic papers (no credentials needed).

    Returns:
        ArxivTools instance or None if not available
    """
    try:
        from agno.tools.arxiv import ArxivTools

        return ArxivTools()
    except ImportError as e:
        print(f"arXiv tools not available: {e}")
        return None
    except Exception as e:
        print(f"Failed to create arXiv tools: {e}")
        return None


# Map of toolkit names to their factory functions
AVAILABLE_TOOLKITS = {
    "gmail": create_gmail_tools,
    "calendar": create_calendar_tools,
    "hackernews": create_hackernews_tools,
    "arxiv": create_arxiv_tools,
}


def load_agno_toolkit(name: str, **kwargs: Any) -> Toolkit | None:
    """Load an Agno toolkit by name.

    Args:
        name: Name of the toolkit (gmail, calendar, hackernews, arxiv)
        **kwargs: Additional arguments to pass to the toolkit factory

    Returns:
        Toolkit instance or None if not available
    """
    factory = AVAILABLE_TOOLKITS.get(name)
    if factory is None:
        print(f"Unknown toolkit: {name}. Available: {list(AVAILABLE_TOOLKITS.keys())}")
        return None
    return factory(**kwargs)
