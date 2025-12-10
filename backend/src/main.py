"""Agno Agent with LlamaCpp backend.

This example shows how to create an Agno Agent with a local llama.cpp server.
"""

import os

from agno.agent.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.models.openrouter import OpenRouter
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.tools import tool
from dotenv import load_dotenv

load_dotenv()


@tool
def change_background(background: str) -> str:  # pylint: disable=unused-argument
    """
    Change the background color of the chat. Can be anything that the CSS background attribute accepts. Regular colors, linear of radial gradients etc.

    Args:
        background: str: The background color to change to. Can be anything that the CSS background attribute accepts. Regular colors, linear of radial gradients etc.
    """  # pylint: disable=line-too-long


"""model=OpenAILike(
    id="local-model",
    base_url=os.getenv("LLAMACPP_BASE_URL", "http://127.0.0.1:8080/v1"),
),"""
agent = Agent(
    model=OpenRouter(
        id="mistralai/devstral-2512:free",
    ),
    tools=[
        change_background,
    ],
    description="You are a helpful AI assistant.",
    instructions="Format your response using markdown where appropriate.",
)

agent_os = AgentOS(agents=[agent], interfaces=[AGUI(agent=agent)])

app = agent_os.get_app()


if __name__ == "__main__":
    agent.print_response("Share a 2 sentence horror story.")
