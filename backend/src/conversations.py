"""Conversation storage and management.

Provides in-memory storage for conversations with API for CRUD operations.
Can be upgraded to persistent storage (SQLite, Redis) later.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class Message:
    """A message in a conversation."""

    id: str
    role: str  # "user" or "assistant"
    content: str
    tool_calls: list[dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Conversation:
    """A conversation with messages."""

    id: str
    title: str
    agent_id: str
    messages: list[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "agent_id": self.agent_id,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "tool_calls": m.tool_calls,
                    "timestamp": m.timestamp,
                }
                for m in self.messages
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_summary(self) -> dict[str, Any]:
        """Convert to summary dict (without messages) for list view."""
        return {
            "id": self.id,
            "title": self.title,
            "agent_id": self.agent_id,
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ConversationStore:
    """In-memory conversation storage.

    Thread-safe for single-process use. For multi-process deployments,
    replace with Redis or database backend.
    """

    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}

    def create(self, agent_id: str, title: str | None = None) -> Conversation:
        """Create a new conversation."""
        conv_id = str(uuid.uuid4())
        conversation = Conversation(
            id=conv_id,
            title=title or "New conversation",
            agent_id=agent_id,
        )
        self._conversations[conv_id] = conversation
        return conversation

    def get(self, conv_id: str) -> Conversation | None:
        """Get a conversation by ID."""
        return self._conversations.get(conv_id)

    def list_all(self) -> list[Conversation]:
        """List all conversations, sorted by updated_at descending."""
        return sorted(
            self._conversations.values(),
            key=lambda c: c.updated_at,
            reverse=True,
        )

    def delete(self, conv_id: str) -> bool:
        """Delete a conversation. Returns True if deleted, False if not found."""
        if conv_id in self._conversations:
            del self._conversations[conv_id]
            return True
        return False

    def add_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        tool_calls: list[dict] | None = None,
        message_id: str | None = None,
    ) -> Message | None:
        """Add a message to a conversation."""
        conversation = self._conversations.get(conv_id)
        if not conversation:
            return None

        message = Message(
            id=message_id or str(uuid.uuid4()),
            role=role,
            content=content,
            tool_calls=tool_calls or [],
        )
        conversation.messages.append(message)
        conversation.updated_at = datetime.now().isoformat()

        # Auto-update title from first user message
        if len(conversation.messages) == 1 and role == "user":
            # Truncate to 50 chars for title
            title = content[:50]
            if len(content) > 50:
                title += "..."
            conversation.title = title

        return message

    def update_title(self, conv_id: str, title: str) -> bool:
        """Update conversation title."""
        conversation = self._conversations.get(conv_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.now().isoformat()
            return True
        return False

    def clear_messages(self, conv_id: str) -> bool:
        """Clear all messages from a conversation."""
        conversation = self._conversations.get(conv_id)
        if conversation:
            conversation.messages = []
            conversation.updated_at = datetime.now().isoformat()
            return True
        return False


# Global store instance
store = ConversationStore()
