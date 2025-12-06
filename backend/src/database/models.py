"""SQLAlchemy models for Agent Composer database."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


class TeamMode(str, Enum):
    """Team execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ROUTER = "router"


class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class Agent(Base):
    """Agent definition model."""
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Model configuration
    provider: Mapped[str] = mapped_column(SQLEnum(ModelProvider), default=ModelProvider.OPENAI)
    model_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Agent code (Python code for custom agents)
    code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Configuration stored as JSON
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    tools: Mapped[list] = mapped_column(JSON, default=list)

    # Metadata
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team_memberships: Mapped[List["TeamMember"]] = relationship(
        "TeamMember", back_populates="agent", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="agent", cascade="all, delete-orphan"
    )


class Team(Base):
    """Team configuration model."""
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Execution mode
    mode: Mapped[str] = mapped_column(SQLEnum(TeamMode), default=TeamMode.SEQUENTIAL)

    # Router configuration (for router mode)
    router_config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members: Mapped[List["TeamMember"]] = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan",
        order_by="TeamMember.position"
    )


class TeamMember(Base):
    """Association table for team membership with ordering."""
    __tablename__ = "team_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="members")
    agent: Mapped["Agent"] = relationship("Agent", back_populates="team_memberships")


class Conversation(Base):
    """Conversation/session model."""
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Associated agent or team (one must be set)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    team_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.created_at"
    )


class Message(Base):
    """Message in a conversation."""
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)

    # Message content
    role: Mapped[str] = mapped_column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # For tool messages
    tool_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tool_call_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # For agent attribution in teams
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    agent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Attachments stored as JSON (file paths, types, etc.)
    attachments: Mapped[list] = mapped_column(JSON, default=list)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")


class MCPServer(Base):
    """MCP server configuration model."""
    __tablename__ = "mcp_servers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)

    # Authentication configuration (stored encrypted in real app)
    auth_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    auth_config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Status
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Available tools from this server (cached)
    available_tools: Mapped[list] = mapped_column(JSON, default=list)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
