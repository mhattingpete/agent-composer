"""Agent loader - creates Agno Agent instances from database definitions."""

from typing import Optional, Any

from agno.agent import Agent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.models import Agent as AgentModel, ModelProvider


class AgentLoader:
    """Loads and instantiates Agno agents from database definitions."""

    @staticmethod
    def get_model(provider: ModelProvider, model_id: Optional[str] = None) -> Any:
        """Create the appropriate model instance based on provider."""
        if provider == ModelProvider.OPENAI:
            from agno.models.openai import OpenAIChat

            return OpenAIChat(
                id=model_id or settings.default_openai_model,
                api_key=settings.openai_api_key,
            )
        elif provider == ModelProvider.ANTHROPIC:
            from agno.models.anthropic import Claude

            return Claude(
                id=model_id or settings.default_anthropic_model,
                api_key=settings.anthropic_api_key,
            )
        elif provider == ModelProvider.OPENROUTER:
            from agno.models.openrouter import OpenRouter

            return OpenRouter(
                id=model_id or settings.default_openrouter_model,
                api_key=settings.openrouter_api_key,
            )
        elif provider == ModelProvider.OLLAMA:
            from agno.models.ollama import Ollama

            return Ollama(
                id=model_id or settings.default_ollama_model,
                host=settings.ollama_base_url,
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

    @classmethod
    async def load_from_db(cls, agent_id: str, db: AsyncSession) -> Optional[Agent]:
        """Load an agent from the database and create an Agno Agent instance."""
        result = await db.execute(
            select(AgentModel).where(AgentModel.id == agent_id)
        )
        agent_model = result.scalar_one_or_none()

        if not agent_model:
            return None

        return cls.load_from_model(agent_model)

    @classmethod
    def load_from_model(cls, agent_model: AgentModel) -> Agent:
        """Create an Agno Agent from a database model."""
        # Get the appropriate LLM model
        model = cls.get_model(
            ModelProvider(agent_model.provider),
            agent_model.model_id,
        )

        # Build instructions list
        instructions = []
        if agent_model.instructions:
            instructions = [agent_model.instructions]

        # Create the Agno Agent
        agent = Agent(
            name=agent_model.name,
            model=model,
            instructions=instructions if instructions else None,
            description=agent_model.description or "",
            markdown=True,
        )

        return agent

    @classmethod
    def create_default_agent(cls, provider: ModelProvider = ModelProvider.OPENAI) -> Agent:
        """Create a default agent with sensible defaults."""
        model = cls.get_model(provider)

        return Agent(
            name="Assistant",
            model=model,
            instructions=["You are a helpful AI assistant."],
            markdown=True,
        )
