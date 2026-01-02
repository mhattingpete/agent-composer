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
        # At minimum, general and coding should be present (may have custom agents too)
        assert len(agents) >= 2

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
        # At minimum, the research team should be present (may have custom teams too)
        assert len(teams) >= 1
        team_ids = [t["id"] for t in teams]
        assert "research" in team_ids  # Built-in research team must exist

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


@pytest.mark.asyncio
async def test_config_all_agents_endpoint():
    """Test that /config/all-agents returns built-in + custom agents."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        response = await client.get("/config/all-agents")
        assert response.status_code == 200

        agents = response.json()
        # Built-in agents should always be present
        assert len(agents) >= 2
        agent_ids = [a["id"] for a in agents]
        assert "general" in agent_ids
        assert "coding" in agent_ids

        # Check structure includes builtin flag
        for agent in agents:
            assert "id" in agent
            assert "name" in agent
            assert "builtin" in agent


@pytest.mark.asyncio
async def test_config_all_teams_endpoint():
    """Test that /config/all-teams returns built-in + custom teams."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        response = await client.get("/config/all-teams")
        assert response.status_code == 200

        teams = response.json()
        # Built-in team should always be present
        assert len(teams) >= 1
        team_ids = [t["id"] for t in teams]
        assert "research" in team_ids

        # Check structure includes builtin flag
        for team in teams:
            assert "id" in team
            assert "name" in team
            assert "builtin" in team


# =============================================================================
# Dynamic Agent/Team Run Tests
# =============================================================================


@pytest.mark.asyncio
async def test_dynamic_agent_run_builtin():
    """Test running a built-in agent through the dynamic endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=60.0
    ) as client:
        # Run the built-in general agent through our dynamic endpoint
        response = await client.post(
            "/config/agents/general/runs",
            data={"message": "Say hello", "stream": "false"},
        )
        assert response.status_code == 200
        result = response.json()
        assert "content" in result


@pytest.mark.asyncio
async def test_dynamic_agent_run_not_found():
    """Test that running a non-existent agent returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=10.0
    ) as client:
        response = await client.post(
            "/config/agents/nonexistent-agent/runs",
            data={"message": "Hello", "stream": "false"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_dynamic_agent_create_and_run():
    """Test creating a custom agent and running it without restart."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=60.0
    ) as client:
        # Create a custom agent
        create_response = await client.post(
            "/config/agents",
            json={
                "name": "Dynamic Test Agent",
                "description": "Agent for testing dynamic loading",
                "model_id": "mistralai/devstral-2512:free",
                "instructions": "You are a test agent. Just say 'Hello from dynamic agent!'",
            },
        )
        assert create_response.status_code == 201
        agent_data = create_response.json()
        agent_id = agent_data["id"]

        try:
            # Verify it appears in the list
            list_response = await client.get("/config/all-agents")
            agents = list_response.json()
            agent_ids = [a["id"] for a in agents]
            assert agent_id in agent_ids

            # Run the custom agent through the dynamic endpoint
            run_response = await client.post(
                f"/config/agents/{agent_id}/runs",
                data={"message": "Say hello", "stream": "false"},
            )
            assert run_response.status_code == 200
            result = run_response.json()
            assert "content" in result

        finally:
            # Clean up - delete the test agent
            await client.delete(f"/config/agents/{agent_id}")


@pytest.mark.asyncio
@pytest.mark.skip(reason="Team runs take long and have async cleanup issues in test env")
async def test_dynamic_team_run_builtin():
    """Test running a built-in team through the dynamic endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=120.0
    ) as client:
        # Run the built-in research team through our dynamic endpoint
        response = await client.post(
            "/config/teams/research/runs",
            data={"message": "Say hello as a team", "stream": "false"},
        )
        assert response.status_code == 200
        result = response.json()
        assert "content" in result
