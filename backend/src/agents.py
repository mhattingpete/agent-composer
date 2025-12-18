"""Agent configurations and factory for multi-agent support.

All agents use the same Python interpreter pattern - the LLM can only call
run_python_code, uv_add, and save_and_run_python_file directly. Nested tools
(web_search, fetch_url, etc.) are only accessible within the Python interpreter.
"""

from dataclasses import dataclass
from typing import Callable

from agno.agent.agent import Agent
from agno.models.openrouter import OpenRouter


@dataclass
class AgentConfig:
    """Configuration for an agent."""

    id: str
    name: str
    description: str
    model_id: str
    instructions: str


# Agent configurations - all share the same tools, differ in instructions and models
AGENT_CONFIGS: dict[str, AgentConfig] = {
    "general": AgentConfig(
        id="general",
        name="General Assistant",
        description="General-purpose AI assistant for any task",
        model_id="mistralai/devstral-2512:free",
        instructions="""You are a helpful general-purpose AI assistant.

You have access to a Python interpreter with many useful tools. To accomplish tasks:

1. Write Python code using run_python_code
2. Install packages with uv_add if needed
3. Save and run files with save_and_run_python_file

Inside run_python_code, you have access to:
- web_search(query) - Search the web
- fetch_url(url) - Fetch and parse web pages
- shell(command) - Run shell commands
- read_file/write_file - File operations
- http_get/http_post - HTTP requests

Be helpful, accurate, and thorough. Format responses using markdown.""",
    ),
    "coding": AgentConfig(
        id="coding",
        name="Coding Assistant",
        description="Expert programming assistant for development tasks",
        model_id="mistralai/devstral-2512:free",
        instructions="""You are an expert coding assistant specializing in software development.

You excel at:
- Writing clean, efficient Python code
- Debugging and fixing errors
- Code review and optimization
- Explaining programming concepts

Use run_python_code to execute Python. Inside it, you have access to:
- shell(command) - Run shell commands (git, npm, etc.)
- read_file(path) - Read source files
- write_file(path, content) - Write/create files
- web_search(query) - Search for documentation
- fetch_url(url) - Fetch API docs or examples

Best practices:
- Write clean, readable code with clear variable names
- Handle errors gracefully
- Add comments for complex logic
- Test your code before presenting it

Format code blocks with syntax highlighting.""",
    ),
    "research": AgentConfig(
        id="research",
        name="Research Assistant",
        description="Information gathering specialist for research tasks",
        model_id="xiaomi/mimo-v2-flash:free",
        instructions="""You are a research specialist focused on finding and synthesizing information.

You excel at:
- Finding relevant information from multiple sources
- Summarizing complex topics clearly
- Fact-checking and verification
- Academic and technical research

Use run_python_code to search and gather information. Inside it, you have access to:
- web_search(query, num_results=5) - Search DuckDuckGo
- fetch_url(url) - Fetch and extract text from web pages
- arxiv_search(query) - Search academic papers (if available)
- hn_get_top_stories() - Get Hacker News stories (if available)

Research best practices:
- Use multiple sources to verify information
- Cite your sources with URLs
- Present findings in a clear, organized format
- Distinguish between facts and opinions

Format research findings with clear headings and bullet points.""",
    ),
}


def get_agent_list() -> list[dict]:
    """Return list of available agents for the frontend dropdown."""
    return [
        {"id": config.id, "name": config.name, "description": config.description}
        for config in AGENT_CONFIGS.values()
    ]


def create_agent(
    agent_id: str,
    tools: list[Callable],
    tool_docs: str,
    debug_mode: bool = True,
) -> Agent:
    """Create an agent instance with the given configuration.

    Args:
        agent_id: The agent ID (general, coding, research)
        tools: List of tool functions (run_python_code, uv_add, etc.)
        tool_docs: Generated documentation for nested Python tools
        debug_mode: Enable debug logging

    Returns:
        Configured Agent instance
    """
    if agent_id not in AGENT_CONFIGS:
        raise ValueError(f"Unknown agent: {agent_id}. Available: {list(AGENT_CONFIGS.keys())}")

    config = AGENT_CONFIGS[agent_id]

    # Build full instructions with tool documentation
    full_instructions = f"""{config.instructions}

{tool_docs}

IMPORTANT: You do NOT have web_search, fetch_url, shell, or other tools as direct function calls.
To use these capabilities, you MUST write Python code and use run_python_code.

### Example - To search the web:
```python
results = web_search("Python tutorials", num_results=3)
print(results)
```

NEVER call tools directly. ALWAYS wrap them in run_python_code."""

    return Agent(
        model=OpenRouter(id=config.model_id),
        tools=tools,
        description=config.description,
        instructions=full_instructions,
        debug_mode=debug_mode,
    )
