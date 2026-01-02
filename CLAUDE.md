# Agent Composer

## Package Managers

- **Backend:** `uv` (Python package manager)
- **Frontend:** `bun` (JavaScript runtime and package manager)

**Startup Time:** Backend starts in under 5 seconds. No need to wait longer.

## Development

```bash
make dev          # Start both backend (7777) and frontend (3000)
make dev-backend  # Backend only
make test         # Run tests
```

## Model Provider

Uses **OpenRouter** for LLM access. Requires `OPENROUTER_API_KEY` in `.env`.

Default model: `mistralai/devstral-2512:free`

## Key Files

- `backend/src/main.py` - AgentOS entry point
- `backend/src/agents.py` - Agent/Team configurations
- `backend/src/config_routes.py` - Config API endpoints
- `backend/config/` - JSON configs (agents, teams, MCP servers)
