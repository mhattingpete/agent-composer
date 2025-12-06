"""AG-UI protocol adapter for streaming agent communication.

Uses Agno's built-in AG-UI support for protocol compliance.
"""

import logging
from typing import Optional, Any

from ag_ui.core import RunAgentInput
from ag_ui.encoder import EventEncoder
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from agno.agent import Agent
from agno.os.interfaces.agui.router import run_agent

from src.database import get_db
from src.runtime.loader import AgentLoader

logger = logging.getLogger(__name__)


class DynamicAgentRegistry:
    """Registry for dynamically loading agents from the database."""

    def __init__(self):
        self._agents_cache: dict[str, Agent] = {}

    async def get_agent(self, agent_id: str, db: AsyncSession) -> Optional[Agent]:
        """Get or create an Agno Agent instance."""
        # Check cache first
        if agent_id in self._agents_cache:
            return self._agents_cache[agent_id]

        # Load from database using AgentLoader
        agent = await AgentLoader.load_from_db(agent_id, db)
        if agent:
            self._agents_cache[agent_id] = agent

        return agent

    def clear_cache(self, agent_id: Optional[str] = None) -> None:
        """Clear the agent cache."""
        if agent_id:
            self._agents_cache.pop(agent_id, None)
        else:
            self._agents_cache.clear()


# Global registry instance
registry = DynamicAgentRegistry()

# Create router
router = APIRouter()

# Event encoder for AG-UI format
encoder = EventEncoder()


class AgentNotFoundError(Exception):
    """Raised when agent is not found."""

    pass


@router.post("")
async def chat(
    run_input: RunAgentInput,
    db: AsyncSession = Depends(get_db),
):
    """AG-UI chat endpoint - streams events via SSE.

    Expects agent_id in forwarded_props to identify which agent to run.
    """
    # Get agent_id from forwarded_props (Pydantic uses snake_case internally)
    agent_id = None
    if run_input.forwarded_props and isinstance(run_input.forwarded_props, dict):
        agent_id = run_input.forwarded_props.get("agent_id")

    if not agent_id:
        # Return error response for missing agent_id
        from ag_ui.core import RunErrorEvent, EventType

        async def error_generator():
            yield encoder.encode(
                RunErrorEvent(
                    type=EventType.RUN_ERROR,
                    message="agent_id is required in forwarded_props",
                )
            )

        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Get the agent
    agent = await registry.get_agent(agent_id, db)

    if not agent:
        from ag_ui.core import RunErrorEvent, EventType

        async def error_generator():
            yield encoder.encode(
                RunErrorEvent(
                    type=EventType.RUN_ERROR,
                    message=f"Agent not found: {agent_id}",
                )
            )

        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Stream the agent's response using Agno's built-in AG-UI support
    async def event_generator():
        async for event in run_agent(agent, run_input):
            yield encoder.encode(event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
async def agui_health():
    """Health check for AG-UI endpoint."""
    return {"status": "healthy", "protocol": "AG-UI", "version": "1.0"}
