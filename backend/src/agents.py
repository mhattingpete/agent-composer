"""Agent configurations and factory for multi-agent support.

All agents use the same Python interpreter pattern - the LLM can only call
run_python_code, uv_add, and save_and_run_python_file directly. Nested tools
(web_search, fetch_url, etc.) are only accessible within the Python interpreter.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from agno.agent.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openrouter import OpenRouter
from agno.team import Team
from agno.tools.mcp import MCPTools
from agno.workflow import Workflow

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
CONFIG_DIR = Path(__file__).parent.parent / "config"
DATA_DIR.mkdir(exist_ok=True)

# Shared database for all agents - auto-creates tables for sessions and memory
db = SqliteDb(db_file=str(DATA_DIR / "agent_composer.db"))


def load_mcp_tools() -> list[MCPTools]:
    """Load MCP tools from config/mcp_servers.json.

    Config format:
    {
        "servers": [
            {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]},
            {"url": "http://localhost:3001/sse", "transport": "sse"}
        ]
    }
    """
    config_file = CONFIG_DIR / "mcp_servers.json"
    if not config_file.exists():
        return []

    try:
        config = json.loads(config_file.read_text())
        servers = config.get("servers", [])

        mcp_tools = []
        for server in servers:
            if not server.get("enabled", True):
                continue

            # Build command string if args provided
            command = server.get("command")
            if command and server.get("args"):
                command = f"{command} {' '.join(server['args'])}"

            try:
                tool = MCPTools(
                    command=command,
                    url=server.get("url"),
                    transport=server.get("transport", "stdio"),
                    env=server.get("env"),
                    tool_name_prefix=server.get("prefix"),
                )
                mcp_tools.append(tool)
                print(f"Loaded MCP server: {server.get('name', command or server.get('url'))}")
            except Exception as e:
                print(f"Failed to load MCP server {server}: {e}")

        return mcp_tools
    except Exception as e:
        print(f"Failed to load MCP config: {e}")
        return []


# Load MCP tools at module initialization
MCP_TOOLS = load_mcp_tools()


@dataclass
class AgentConfig:
    """Configuration for an agent."""

    id: str
    name: str
    description: str
    model_id: str
    instructions: str


# Built-in agent configurations - read-only, always available
BUILTIN_AGENT_CONFIGS: dict[str, AgentConfig] = {
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
}


def load_custom_agents() -> dict[str, AgentConfig]:
    """Load custom agent configurations from JSON file."""
    agents_file = CONFIG_DIR / "agents.json"
    if not agents_file.exists():
        return {}

    try:
        data = json.loads(agents_file.read_text())
        return {
            agent["id"]: AgentConfig(
                id=agent["id"],
                name=agent["name"],
                description=agent.get("description", ""),
                model_id=agent["model_id"],
                instructions=agent.get("instructions", "You are a helpful AI assistant."),
            )
            for agent in data
        }
    except (json.JSONDecodeError, KeyError, OSError) as e:
        print(f"Failed to load custom agents: {e}")
        return {}


def get_all_agent_configs() -> dict[str, AgentConfig]:
    """Get all agent configs (built-in + custom), with custom configs loaded fresh."""
    custom = load_custom_agents()
    return {**BUILTIN_AGENT_CONFIGS, **custom}


# Combined agent configs - use get_all_agent_configs() for fresh data
AGENT_CONFIGS: dict[str, AgentConfig] = get_all_agent_configs()


def reload_agent_configs() -> None:
    """Reload agent configs from JSON. Call after config changes."""
    global AGENT_CONFIGS
    AGENT_CONFIGS = get_all_agent_configs()


def get_agent_list() -> list[dict]:
    """Return list of available agents for the frontend dropdown."""
    # Use fresh configs to pick up any changes
    all_configs = get_all_agent_configs()
    return [
        {
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "builtin": config.id in BUILTIN_AGENT_CONFIGS,
        }
        for config in all_configs.values()
    ]


def create_agent(
    agent_id: str,
    tools: list[Callable],
    tool_docs: str,
    debug_mode: bool = True,
) -> Agent:
    """Create an agent instance with the given configuration.

    Args:
        agent_id: The agent ID (general, coding, or custom)
        tools: List of tool functions (run_python_code, uv_add, etc.)
        tool_docs: Generated documentation for nested Python tools
        debug_mode: Enable debug logging

    Returns:
        Configured Agent instance
    """
    # Use fresh configs to pick up custom agents
    all_configs = get_all_agent_configs()

    if agent_id not in all_configs:
        raise ValueError(f"Unknown agent: {agent_id}. Available: {list(all_configs.keys())}")

    config = all_configs[agent_id]

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

    # Combine explicit tools with MCP tools
    all_tools = list(tools) + MCP_TOOLS

    return Agent(
        model=OpenRouter(id=config.model_id),
        tools=all_tools,
        description=config.description,
        instructions=full_instructions,
        debug_mode=debug_mode,
        # Enable Agno persistence - sessions are stored in SQLite
        db=db,
        add_history_to_context=True,  # Load previous messages from session
        num_history_runs=5,  # Include last 5 conversation turns in context
    )


# =============================================================================
# Teams - Multi-agent collaboration
# =============================================================================

# Built-in team configurations - read-only, always available
BUILTIN_TEAM_CONFIGS = {
    "research": {
        "name": "research",
        "description": "A research team that gathers, analyzes, and presents information",
        "members": [
            {"name": "Researcher", "role": "Find and gather relevant information", "has_tools": True},
            {"name": "Analyst", "role": "Analyze and synthesize research findings", "has_tools": False},
            {"name": "Writer", "role": "Create clear, well-structured content", "has_tools": False},
        ],
    },
}


def load_custom_teams() -> dict[str, dict]:
    """Load custom team configurations from JSON file."""
    teams_file = CONFIG_DIR / "teams.json"
    if not teams_file.exists():
        return {}

    try:
        data = json.loads(teams_file.read_text())
        return {team["id"]: team for team in data}
    except (json.JSONDecodeError, KeyError, OSError) as e:
        print(f"Failed to load custom teams: {e}")
        return {}


def get_all_team_configs() -> dict[str, dict]:
    """Get all team configs (built-in + custom), with custom configs loaded fresh."""
    custom = load_custom_teams()
    return {**BUILTIN_TEAM_CONFIGS, **custom}


# Combined team configs
TEAM_CONFIGS = get_all_team_configs()


def create_team(
    team_id: str,
    tools: list[Callable],
    tool_docs: str,
) -> Team:
    """Create a team instance with the given configuration.

    Args:
        team_id: The team ID (research, or custom)
        tools: List of tool functions (run_python_code, etc.)
        tool_docs: Generated documentation for nested Python tools

    Returns:
        Configured Team instance
    """
    # Use fresh configs to pick up custom teams
    all_configs = get_all_team_configs()

    if team_id not in all_configs:
        raise ValueError(f"Unknown team: {team_id}. Available: {list(all_configs.keys())}")

    config = all_configs[team_id]

    # Build member agents with role-specific instructions
    ROLE_INSTRUCTIONS = {
        "Researcher": """You are the Researcher on a research team.
Your role: Find and gather relevant information using web search.

CRITICAL: You MUST use run_python_code with web_search() for EVERY research task.
NEVER make up information. NEVER guess. ONLY report what you find from searches.

Example - searching for information:
```python
results = web_search("Kuatro Group founders Denmark", num_results=5)
print(results)
```

Example - fetching a specific URL for more details:
```python
content = fetch_url("https://example.com/about")
print(content)
```

Always search first, then report the ACTUAL results you found. Include source URLs.""",

        "Analyst": """You are the Analyst on a research team.
Your role: Analyze and synthesize the research findings provided to you.
Identify key patterns, verify consistency across sources, and highlight important insights.
Be critical - note if information seems incomplete or contradictory.""",

        "Writer": """You are the Writer on a research team.
Your role: Create clear, well-structured content based on the analysis.
Use markdown formatting. Cite sources when available.
Only include information that was actually found - never add made-up details.""",
    }

    members = []
    for member_config in config["members"]:
        member_tools = tools if member_config.get("has_tools") else []

        # Use role-specific instructions or fall back to generic
        base_instructions = ROLE_INSTRUCTIONS.get(
            member_config["name"],
            f"You are the {member_config['name']}. Your role: {member_config['role']}"
        )

        # Add tool docs for members with tools
        member_instructions = base_instructions
        if member_config.get("has_tools"):
            member_instructions += f"\n\n{tool_docs}"

        members.append(Agent(
            name=member_config["name"],
            role=member_config["role"],
            model=OpenRouter(id="mistralai/devstral-2512:free"),
            tools=member_tools,
            instructions=member_instructions,
            debug_mode=True,
        ))

    return Team(
        name=config["name"],
        model=OpenRouter(id="mistralai/devstral-2512:free"),
        description=config["description"],
        members=members,
        db=db,
        add_history_to_context=True,
        debug_mode=True,
    )


# Teams dict - populated by main.py after tools are defined
TEAMS: dict[str, Team] = {}


# =============================================================================
# Workflows - Deterministic pipelines
# =============================================================================

# Content Workflow: Research → Write (sequential steps)
content_workflow = Workflow(
    name="content",
    description="Create content by researching a topic and writing about it",
    steps=[
        Agent(
            name="Researcher",
            model=OpenRouter(id="mistralai/devstral-2512:free"),
            instructions="Research the given topic thoroughly. Return your findings.",
        ),
        Agent(
            name="Writer",
            model=OpenRouter(id="mistralai/devstral-2512:free"),
            instructions="Based on the research provided, write a clear and engaging article. Use markdown.",
        ),
    ],
    db=db,
)

# Export workflows dict for main.py
WORKFLOWS: dict[str, Workflow] = {
    "content": content_workflow,
}


def get_teams_list() -> list[dict]:
    """Return list of available teams for the frontend."""
    # Use fresh configs to pick up any changes
    all_configs = get_all_team_configs()
    return [
        {
            "id": team_id,
            "name": config["name"],
            "description": config["description"],
            "type": "team",
            "builtin": team_id in BUILTIN_TEAM_CONFIGS,
        }
        for team_id, config in all_configs.items()
    ]


def get_workflows_list() -> list[dict]:
    """Return list of available workflows for the frontend."""
    return [
        {"id": name, "name": workflow.name, "description": workflow.description, "type": "workflow"}
        for name, workflow in WORKFLOWS.items()
    ]
