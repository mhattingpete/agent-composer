"""Agent CRUD API endpoints."""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.database.models import Agent, ModelProvider


# Pydantic schemas for API request/response
class AgentConfig(BaseModel):
    """Agent configuration options."""
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)


class AgentCreate(BaseModel):
    """Request schema for creating an agent."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    provider: ModelProvider = ModelProvider.OPENAI
    model_id: Optional[str] = None
    code: Optional[str] = None
    config: AgentConfig = Field(default_factory=AgentConfig)
    tools: List[str] = Field(default_factory=list)


class AgentUpdate(BaseModel):
    """Request schema for updating an agent."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    provider: Optional[ModelProvider] = None
    model_id: Optional[str] = None
    code: Optional[str] = None
    config: Optional[AgentConfig] = None
    tools: Optional[List[str]] = None


class AgentResponse(BaseModel):
    """Response schema for agent data."""
    id: str
    name: str
    description: Optional[str]
    instructions: Optional[str]
    provider: ModelProvider
    model_id: Optional[str]
    code: Optional[str]
    config: dict
    tools: List[str]
    is_builtin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    include_builtin: bool = True,
) -> List[Agent]:
    """List all agents."""
    query = select(Agent)
    if not include_builtin:
        query = query.where(Agent.is_builtin == False)  # noqa: E712
    query = query.order_by(Agent.created_at.desc())

    result = await db.execute(query)
    agents = result.scalars().all()
    return list(agents)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
) -> Agent:
    """Get a specific agent by ID."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id '{agent_id}' not found"
        )

    return agent


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db),
) -> Agent:
    """Create a new agent."""
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        instructions=agent_data.instructions,
        provider=agent_data.provider,
        model_id=agent_data.model_id,
        code=agent_data.code,
        config=agent_data.config.model_dump() if agent_data.config else {},
        tools=agent_data.tools,
        is_builtin=False,
    )

    db.add(agent)
    await db.flush()
    await db.refresh(agent)

    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
) -> Agent:
    """Update an existing agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id '{agent_id}' not found"
        )

    # Don't allow modifying built-in agents
    if agent.is_builtin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify built-in agents"
        )

    # Update only provided fields
    update_data = agent_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "config" and value is not None:
            setattr(agent, field, value)
        elif value is not None:
            setattr(agent, field, value)

    agent.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(agent)

    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an agent."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id '{agent_id}' not found"
        )

    # Don't allow deleting built-in agents
    if agent.is_builtin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete built-in agents"
        )

    await db.delete(agent)
