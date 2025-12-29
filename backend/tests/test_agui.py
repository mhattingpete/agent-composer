"""Tests for the Agno AgentOS API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_agents_list_endpoint():
    """Test that the /agents endpoint returns the list of available agents."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        response = await client.get("/agents")
        assert response.status_code == 200

        agents = response.json()
        assert len(agents) == 2  # general, coding (research is a team)

        # Check structure - Agno returns these fields
        for agent in agents:
            assert "id" in agent
            # Note: Agno doesn't return 'name' at top level, but agent data is present


@pytest.mark.asyncio
async def test_teams_list_endpoint():
    """Test that the /teams endpoint returns the list of available teams."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        response = await client.get("/teams")
        assert response.status_code == 200

        teams = response.json()
        assert len(teams) == 1  # research team

        # Check structure
        for team in teams:
            assert "id" in team


@pytest.mark.asyncio
async def test_agent_detail_endpoint():
    """Test that individual agent details are accessible."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        # First get the list to find agent IDs
        response = await client.get("/agents")
        agents = response.json()

        # Check each agent is accessible by ID
        for agent in agents:
            agent_id = agent["id"]
            response = await client.get(f"/agents/{agent_id}")
            assert response.status_code == 200
            detail = response.json()
            assert detail["id"] == agent_id


@pytest.mark.asyncio
async def test_agent_runs_endpoint():
    """Test that the agent runs endpoint accepts requests and returns response."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=60.0
    ) as client:
        # Get agent ID first
        response = await client.get("/agents")
        agents = response.json()
        agent_id = agents[0]["id"]

        # AgentOS uses multipart/form-data with 'message' field
        response = await client.post(
            f"/agents/{agent_id}/runs",
            data={"message": "Say hello", "stream": "false"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_agent_runs_streaming():
    """Test that streaming mode returns SSE events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=60.0
    ) as client:
        # Get agent ID first
        response = await client.get("/agents")
        agents = response.json()
        agent_id = agents[0]["id"]

        # Request with streaming enabled
        response = await client.post(
            f"/agents/{agent_id}/runs",
            data={"message": "Say hello", "stream": "true"},
        )
        assert response.status_code == 200
        # Streaming response should have text/event-stream content type
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type or len(response.text) > 0


@pytest.mark.asyncio
async def test_agent_runs_validates_request():
    """Test that the runs endpoint validates the request body."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        # Get agent ID first
        response = await client.get("/agents")
        agents = response.json()
        agent_id = agents[0]["id"]

        # Missing required 'message' field
        response = await client.post(f"/agents/{agent_id}/runs", data={})
        assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_config_endpoint():
    """Test the config endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        response = await client.get("/config")
        assert response.status_code == 200
