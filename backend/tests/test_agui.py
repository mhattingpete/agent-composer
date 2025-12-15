"""Tests for the AG-UI endpoint."""

import json
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


def parse_sse_events(body: str) -> list[dict]:
    """Parse Server-Sent Events format into a list of event dicts."""
    events = []
    for line in body.split("\n"):
        line = line.strip()
        if line.startswith("data: "):
            data = line[6:]  # Remove "data: " prefix
            try:
                event = json.loads(data)
                events.append(event)
            except json.JSONDecodeError:
                pass
    return events


@pytest.fixture
def agui_request():
    """Create a request payload similar to what the frontend sends."""
    return {
        "thread_id": "test-thread",
        "run_id": str(uuid.uuid4()),
        "messages": [
            {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": "Say hello",
            }
        ],
        "state": {},
        "tools": [],
        "context": [],
        "forwarded_props": {},
    }


@pytest.mark.asyncio
async def test_agui_endpoint_returns_streaming_response(agui_request):
    """Test that the /agui endpoint returns a streaming response with AG-UI events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        response = await client.post("/agui", json=agui_request)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        events = parse_sse_events(response.text)

        # Should have received at least one event
        assert len(events) > 0

        # Check for expected event types
        event_types = [e.get("type") for e in events]

        # Should have text message events (assistant response)
        assert "TEXT_MESSAGE_START" in event_types, f"Expected TEXT_MESSAGE_START, got: {event_types}"


@pytest.mark.asyncio
async def test_agui_endpoint_text_message_flow(agui_request):
    """Test the complete text message flow: start -> content -> end."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        response = await client.post("/agui", json=agui_request)
        assert response.status_code == 200

        events = parse_sse_events(response.text)

        # Find text message events
        text_starts = [e for e in events if e.get("type") == "TEXT_MESSAGE_START"]
        text_contents = [e for e in events if e.get("type") == "TEXT_MESSAGE_CONTENT"]
        text_ends = [e for e in events if e.get("type") == "TEXT_MESSAGE_END"]

        # Should have at least one text message start
        assert len(text_starts) > 0, "Should have TEXT_MESSAGE_START event"

        # Each start should have a messageId
        for start in text_starts:
            assert "messageId" in start, "TEXT_MESSAGE_START should have messageId"

        # Content events should have messageId and delta
        for content in text_contents:
            assert "messageId" in content, "TEXT_MESSAGE_CONTENT should have messageId"
            assert "delta" in content, "TEXT_MESSAGE_CONTENT should have delta"

        # End events should have messageId
        for end in text_ends:
            assert "messageId" in end, "TEXT_MESSAGE_END should have messageId"


@pytest.mark.asyncio
async def test_agui_endpoint_validates_request():
    """Test that the endpoint validates the request body."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=10.0) as client:
        # Missing required fields
        response = await client.post("/agui", json={"thread_id": "test"})
        assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_agui_endpoint_action_execution_flow():
    """Test that tool calls produce ActionExecution events."""
    request = {
        "thread_id": "test-thread",
        "run_id": str(uuid.uuid4()),
        "messages": [
            {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": "Run this Python code: print('hello from test')",
            }
        ],
        "state": {},
        "tools": [],
        "context": [],
        "forwarded_props": {},
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=90.0) as client:
        response = await client.post("/agui", json=request)
        assert response.status_code == 200

        events = parse_sse_events(response.text)
        event_types = [e.get("type") for e in events]

        # When the agent uses a tool, we should see ActionExecution events
        # Note: This depends on the model actually calling a tool
        if "ACTION_EXECUTION_START" in event_types:
            action_starts = [e for e in events if e.get("type") == "ACTION_EXECUTION_START"]
            for start in action_starts:
                assert "actionExecutionId" in start
                assert "actionName" in start
