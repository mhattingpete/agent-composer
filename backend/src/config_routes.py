"""Configuration API routes for managing agents and teams.

Provides CRUD operations for custom agent and team configurations,
stored in JSON files. Built-in agents/teams are read-only.

Also provides dynamic run endpoints for custom agents/teams that
bypass AgentOS and create agents on-the-fly.
"""

import json
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Config directory
CONFIG_DIR = Path(__file__).parent.parent / "config"
AGENTS_FILE = CONFIG_DIR / "agents.json"
TEAMS_FILE = CONFIG_DIR / "teams.json"

router = APIRouter(prefix="/config", tags=["config"])


# =============================================================================
# Pydantic Models
# =============================================================================


class AgentConfigCreate(BaseModel):
    """Request model for creating an agent."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    model_id: str = Field(..., min_length=1)
    instructions: str = Field(default="You are a helpful AI assistant.")


class AgentConfigUpdate(BaseModel):
    """Request model for updating an agent."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    model_id: str | None = Field(default=None, min_length=1)
    instructions: str | None = None


class AgentConfigResponse(BaseModel):
    """Response model for an agent config."""

    id: str
    name: str
    description: str
    model_id: str
    instructions: str
    builtin: bool = False


class TeamMember(BaseModel):
    """A member of a team."""

    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1)
    has_tools: bool = False


class TeamConfigCreate(BaseModel):
    """Request model for creating a team."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    members: list[TeamMember] = Field(..., min_length=1)


class TeamConfigUpdate(BaseModel):
    """Request model for updating a team."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    members: list[TeamMember] | None = None


class TeamConfigResponse(BaseModel):
    """Response model for a team config."""

    id: str
    name: str
    description: str
    members: list[TeamMember]
    builtin: bool = False


class ModelInfo(BaseModel):
    """Information about an available model."""

    id: str
    name: str
    provider: str


# =============================================================================
# Helper Functions
# =============================================================================


def _load_json(file_path: Path) -> list[dict]:
    """Load JSON array from file, returning empty list if missing."""
    if not file_path.exists():
        return []
    try:
        return json.loads(file_path.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save_json(file_path: Path, data: list[dict]) -> None:
    """Save JSON array to file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2))


def _generate_id(name: str) -> str:
    """Generate a URL-safe ID from a name."""
    # Create slug from name, append short UUID for uniqueness
    slug = name.lower().replace(" ", "-")[:20]
    short_id = str(uuid.uuid4())[:8]
    return f"{slug}-{short_id}"


# =============================================================================
# Agent CRUD Endpoints
# =============================================================================


@router.get("/agents", response_model=list[AgentConfigResponse])
async def list_custom_agents() -> list[dict[str, Any]]:
    """List all custom agent configurations."""
    agents = _load_json(AGENTS_FILE)
    return [{"builtin": False, **agent} for agent in agents]


@router.post("/agents", response_model=AgentConfigResponse, status_code=201)
async def create_agent(agent: AgentConfigCreate) -> dict[str, Any]:
    """Create a new custom agent."""
    agents = _load_json(AGENTS_FILE)

    # Check for duplicate names
    if any(a["name"].lower() == agent.name.lower() for a in agents):
        raise HTTPException(status_code=400, detail="Agent with this name already exists")

    new_agent = {
        "id": _generate_id(agent.name),
        "name": agent.name,
        "description": agent.description,
        "model_id": agent.model_id,
        "instructions": agent.instructions,
    }

    agents.append(new_agent)
    _save_json(AGENTS_FILE, agents)

    return {"builtin": False, **new_agent}


@router.get("/agents/{agent_id}", response_model=AgentConfigResponse)
async def get_agent(agent_id: str) -> dict[str, Any]:
    """Get a custom agent by ID."""
    agents = _load_json(AGENTS_FILE)

    for agent in agents:
        if agent["id"] == agent_id:
            return {"builtin": False, **agent}

    raise HTTPException(status_code=404, detail="Agent not found")


@router.put("/agents/{agent_id}", response_model=AgentConfigResponse)
async def update_agent(agent_id: str, updates: AgentConfigUpdate) -> dict[str, Any]:
    """Update a custom agent."""
    agents = _load_json(AGENTS_FILE)

    for i, agent in enumerate(agents):
        if agent["id"] == agent_id:
            # Apply updates
            update_data = updates.model_dump(exclude_unset=True)
            agents[i] = {**agent, **update_data}
            _save_json(AGENTS_FILE, agents)
            return {"builtin": False, **agents[i]}

    raise HTTPException(status_code=404, detail="Agent not found")


@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(agent_id: str) -> None:
    """Delete a custom agent."""
    agents = _load_json(AGENTS_FILE)

    for i, agent in enumerate(agents):
        if agent["id"] == agent_id:
            agents.pop(i)
            _save_json(AGENTS_FILE, agents)
            return

    raise HTTPException(status_code=404, detail="Agent not found")


# =============================================================================
# Team CRUD Endpoints
# =============================================================================


@router.get("/teams", response_model=list[TeamConfigResponse])
async def list_custom_teams() -> list[dict[str, Any]]:
    """List all custom team configurations."""
    teams = _load_json(TEAMS_FILE)
    return [{"builtin": False, **team} for team in teams]


@router.post("/teams", response_model=TeamConfigResponse, status_code=201)
async def create_team(team: TeamConfigCreate) -> dict[str, Any]:
    """Create a new custom team."""
    teams = _load_json(TEAMS_FILE)

    # Check for duplicate names
    if any(t["name"].lower() == team.name.lower() for t in teams):
        raise HTTPException(status_code=400, detail="Team with this name already exists")

    new_team = {
        "id": _generate_id(team.name),
        "name": team.name,
        "description": team.description,
        "members": [m.model_dump() for m in team.members],
    }

    teams.append(new_team)
    _save_json(TEAMS_FILE, teams)

    return {"builtin": False, **new_team}


@router.get("/teams/{team_id}", response_model=TeamConfigResponse)
async def get_team(team_id: str) -> dict[str, Any]:
    """Get a custom team by ID."""
    teams = _load_json(TEAMS_FILE)

    for team in teams:
        if team["id"] == team_id:
            return {"builtin": False, **team}

    raise HTTPException(status_code=404, detail="Team not found")


@router.put("/teams/{team_id}", response_model=TeamConfigResponse)
async def update_team(team_id: str, updates: TeamConfigUpdate) -> dict[str, Any]:
    """Update a custom team."""
    teams = _load_json(TEAMS_FILE)

    for i, team in enumerate(teams):
        if team["id"] == team_id:
            # Apply updates
            update_data = updates.model_dump(exclude_unset=True)
            if "members" in update_data:
                update_data["members"] = [m.model_dump() if hasattr(m, "model_dump") else m for m in update_data["members"]]
            teams[i] = {**team, **update_data}
            _save_json(TEAMS_FILE, teams)
            return {"builtin": False, **teams[i]}

    raise HTTPException(status_code=404, detail="Team not found")


@router.delete("/teams/{team_id}", status_code=204)
async def delete_team(team_id: str) -> None:
    """Delete a custom team."""
    teams = _load_json(TEAMS_FILE)

    for i, team in enumerate(teams):
        if team["id"] == team_id:
            teams.pop(i)
            _save_json(TEAMS_FILE, teams)
            return

    raise HTTPException(status_code=404, detail="Team not found")


# =============================================================================
# Models Endpoint
# =============================================================================

# Available models for the dropdown
# These are OpenRouter model IDs
AVAILABLE_MODELS = [
    ModelInfo(id="mistralai/devstral-2512:free", name="Devstral (Free)", provider="Mistral"),
    ModelInfo(id="mistralai/mistral-small-3.1-24b-instruct:free", name="Mistral Small 3.1 (Free)", provider="Mistral"),
    ModelInfo(id="meta-llama/llama-3.3-70b-instruct:free", name="Llama 3.3 70B (Free)", provider="Meta"),
    ModelInfo(id="google/gemini-2.0-flash-exp:free", name="Gemini 2.0 Flash (Free)", provider="Google"),
    ModelInfo(id="openai/gpt-4o-mini", name="GPT-4o Mini", provider="OpenAI"),
    ModelInfo(id="openai/gpt-4o", name="GPT-4o", provider="OpenAI"),
    ModelInfo(id="anthropic/claude-3.5-sonnet", name="Claude 3.5 Sonnet", provider="Anthropic"),
    ModelInfo(id="anthropic/claude-3-opus", name="Claude 3 Opus", provider="Anthropic"),
]


@router.get("/models", response_model=list[ModelInfo])
async def list_models() -> list[ModelInfo]:
    """List available models for agent configuration."""
    return AVAILABLE_MODELS


# =============================================================================
# Combined List Endpoints (Built-in + Custom)
# =============================================================================


@router.get("/all-agents")
async def list_all_agents() -> list[dict[str, Any]]:
    """List ALL agents (built-in + custom) for the frontend dropdown.

    This shadows the AgentOS /agents endpoint which only knows about
    agents created at startup. Our endpoint reads from JSON files
    to include dynamically created agents.
    """
    from agents import BUILTIN_AGENT_CONFIGS, load_custom_agents

    # Built-in agents
    result = [
        {
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "model": config.model_id,
            "builtin": True,
        }
        for config in BUILTIN_AGENT_CONFIGS.values()
    ]

    # Custom agents from JSON
    custom = load_custom_agents()
    for config in custom.values():
        result.append({
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "model": config.model_id,
            "builtin": False,
        })

    return result


@router.get("/all-teams")
async def list_all_teams() -> list[dict[str, Any]]:
    """List ALL teams (built-in + custom) for the frontend dropdown.

    This shadows the AgentOS /teams endpoint which only knows about
    teams created at startup.
    """
    from agents import BUILTIN_TEAM_CONFIGS, load_custom_teams

    # Built-in teams
    result = [
        {
            "id": team_id,
            "name": config["name"],
            "description": config["description"],
            "type": "team",
            "builtin": True,
        }
        for team_id, config in BUILTIN_TEAM_CONFIGS.items()
    ]

    # Custom teams from JSON
    custom = load_custom_teams()
    for team_id, config in custom.items():
        result.append({
            "id": team_id,
            "name": config["name"],
            "description": config.get("description", ""),
            "type": "team",
            "builtin": False,
        })

    return result


# =============================================================================
# Dynamic Run Endpoints (for custom agents/teams)
# =============================================================================


@router.post("/agents/{agent_id}/runs")
async def run_dynamic_agent(
    agent_id: str,
    message: str = Form(...),
    stream: str = Form(default="true"),
    session_id: str = Form(default=None),
):
    """Run a custom agent dynamically.

    This endpoint creates agents on-the-fly for custom agents,
    enabling hot-loading without server restart.
    """
    from agents import get_all_agent_configs
    from main import get_or_create_agent

    # Check if agent exists
    all_configs = get_all_agent_configs()
    if agent_id not in all_configs:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Get or create the agent
    agent = get_or_create_agent(agent_id)

    # Run the agent
    should_stream = stream.lower() == "true"

    if should_stream:
        # Streaming response - arun with stream=True returns an async generator directly
        # Frontend expects cumulative content in each chunk (not deltas)
        async def generate():
            accumulated_content = ""
            async for chunk in agent.arun(message, stream=True, session_id=session_id):
                # Agno RunResponse objects have model_dump() for serialization
                if hasattr(chunk, "model_dump"):
                    chunk_data = chunk.model_dump(exclude_none=True)
                    # Accumulate content for cumulative streaming
                    if chunk_data.get("content"):
                        accumulated_content += chunk_data["content"]
                        chunk_data["content"] = accumulated_content
                    # Map Agno event names to frontend expected names
                    if chunk_data.get("event") == "RunResponse":
                        chunk_data["event"] = "RunContent"
                    yield json.dumps(chunk_data) + "\n"
                elif hasattr(chunk, "content") and chunk.content:
                    # Fallback for simple content - accumulate and use RunContent event
                    accumulated_content += chunk.content
                    yield json.dumps({
                        "event": "RunContent",
                        "content": accumulated_content,
                        "content_type": "str",
                        "created_at": 0,
                    }) + "\n"
            # Send completion event with full content
            yield json.dumps({
                "event": "RunCompleted",
                "content": accumulated_content,
                "content_type": "str",
                "created_at": 0,
            }) + "\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        # Non-streaming response
        run_response = await agent.arun(message, stream=False, session_id=session_id)
        return {
            "content": run_response.content,
            "session_id": run_response.session_id,
        }


@router.post("/teams/{team_id}/runs")
async def run_dynamic_team(
    team_id: str,
    message: str = Form(...),
    stream: str = Form(default="true"),
    session_id: str = Form(default=None),
):
    """Run a custom team dynamically.

    This endpoint creates teams on-the-fly for custom teams,
    enabling hot-loading without server restart.
    """
    from agents import get_all_team_configs
    from main import get_or_create_team

    # Check if team exists
    all_configs = get_all_team_configs()
    if team_id not in all_configs:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")

    # Get or create the team
    team = get_or_create_team(team_id)

    # Run the team
    should_stream = stream.lower() == "true"

    if should_stream:
        # Streaming response - arun with stream=True returns an async generator directly
        # Frontend expects cumulative content in each chunk (not deltas)
        async def generate():
            accumulated_content = ""
            async for chunk in team.arun(message, stream=True, session_id=session_id):
                # Agno RunResponse objects have model_dump() for serialization
                if hasattr(chunk, "model_dump"):
                    chunk_data = chunk.model_dump(exclude_none=True)
                    # Accumulate content for cumulative streaming
                    if chunk_data.get("content"):
                        accumulated_content += chunk_data["content"]
                        chunk_data["content"] = accumulated_content
                    # Map Agno event names to frontend expected names for teams
                    if chunk_data.get("event") == "RunResponse":
                        chunk_data["event"] = "TeamRunContent"
                    yield json.dumps(chunk_data) + "\n"
                elif hasattr(chunk, "content") and chunk.content:
                    # Fallback for simple content - accumulate and use TeamRunContent event
                    accumulated_content += chunk.content
                    yield json.dumps({
                        "event": "TeamRunContent",
                        "content": accumulated_content,
                        "content_type": "str",
                        "created_at": 0,
                    }) + "\n"
            # Send completion event with full content
            yield json.dumps({
                "event": "TeamRunCompleted",
                "content": accumulated_content,
                "content_type": "str",
                "created_at": 0,
            }) + "\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        run_response = await team.arun(message, stream=False, session_id=session_id)
        return {
            "content": run_response.content,
            "session_id": run_response.session_id,
        }
