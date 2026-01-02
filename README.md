# Agent Composer

A local-first platform for designing, composing, and interacting with multi-agent AI systems using the Agno framework.

## Features

- **Built-in Agents**: Pre-configured General Assistant and Coding Assistant
- **Custom Agents**: Create your own agents via the API with custom models and instructions
- **Team Collaboration**: Multi-agent teams with role-based member configurations
- **Python Interpreter**: Agents can run Python code with access to web search, HTTP, shell, and file operations
- **MCP Integration**: Connect to Model Context Protocol servers for extensible tool capabilities
- **Session Persistence**: SQLite-backed conversation history with automatic session management
- **AG-UI Protocol**: Real-time streaming agent interactions via AgentOS

## Tech Stack

### Backend
- Python 3.12+
- [Agno](https://docs.agno.com) framework with AgentOS
- FastAPI
- SQLite (auto-managed by Agno)
- OpenRouter for LLM access

### Frontend
- [Agno Agent UI](https://github.com/agno-ai/agent-ui) (Next.js)
- React 18+ with TypeScript
- Bun package manager
- TailwindCSS

## Quick Start

### Prerequisites
- [uv](https://docs.astral.sh/uv/) - Python package manager
- [Bun](https://bun.sh/) - JavaScript runtime
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd agent-composer
```

2. Configure your OpenRouter API key:
```bash
# Create .env file in the root directory
echo "OPENROUTER_API_KEY=your-key-here" > .env
```

3. Install dependencies:
```bash
make install
```

4. Start both servers:
```bash
make dev
```

This starts:
- **Backend**: http://localhost:7777 (AgentOS API)
- **Frontend**: http://localhost:3000 (Agent UI)

## Architecture

```
agent-composer/
├── backend/
│   ├── config/                 # Configuration files
│   │   ├── agents.json         # Custom agent definitions
│   │   ├── teams.json          # Custom team definitions
│   │   └── mcp_servers.json    # MCP server configurations
│   ├── data/                   # SQLite database (auto-created)
│   ├── src/
│   │   ├── main.py             # AgentOS application entry point
│   │   ├── agents.py           # Agent/Team configurations and factory
│   │   ├── config_routes.py    # Config API for managing agents/teams
│   │   ├── code_tools.py       # Python interpreter tools
│   │   ├── logging_config.py   # Structured logging setup
│   │   └── tools/              # Built-in and Agno toolkit integrations
│   ├── tests/                  # Backend tests
│   └── pyproject.toml
├── frontend/                   # Agno Agent UI (Next.js)
│   ├── src/
│   └── package.json
├── Makefile                    # Build and development commands
└── README.md
```

## Available Commands

```bash
# Install dependencies
make install              # Install both backend and frontend
make install-backend      # Install backend only
make install-frontend     # Install frontend only

# Development
make dev                  # Start both servers
make dev-backend          # Start backend only (port 7777)
make dev-frontend         # Start frontend only (port 3000)

# Testing
make test                 # Run backend tests
make test-e2e             # Run end-to-end tests (requires both servers)

# Code quality
make lint                 # Lint both backend and frontend
make lint-fix             # Fix linting issues

# Cleanup
make clean                # Remove generated files

# Local LLM (optional)
make model                # Start llama-server with default model
make model MODEL=<hf-path> # Start specific model
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM access | Yes |

### Custom Agents

Create custom agents by adding entries to `backend/config/agents.json`:

```json
[
  {
    "id": "my-agent-abc123",
    "name": "My Custom Agent",
    "description": "Does specific things",
    "model_id": "mistralai/devstral-2512:free",
    "instructions": "You are a specialized assistant..."
  }
]
```

Or use the API:
```bash
curl -X POST http://localhost:7777/config/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "My Agent", "model_id": "mistralai/devstral-2512:free", "instructions": "..."}'
```

### MCP Servers

Configure MCP servers in `backend/config/mcp_servers.json`:

```json
{
  "servers": [
    {
      "name": "filesystem",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "enabled": true
    }
  ]
}
```

## API Endpoints

### Agents
- `GET /agents` - List all agents
- `GET /agents/{id}` - Get agent details
- `POST /agents/{id}/runs` - Run agent (streaming)
- `GET /config/all-agents` - List all agents with builtin flag
- `POST /config/agents` - Create custom agent
- `PUT /config/agents/{id}` - Update custom agent
- `DELETE /config/agents/{id}` - Delete custom agent

### Teams
- `GET /teams` - List all teams
- `POST /teams/{id}/runs` - Run team (streaming)
- `GET /config/all-teams` - List all teams with builtin flag
- `POST /config/teams` - Create custom team

### Sessions
- `GET /agents/{id}/sessions` - List agent sessions
- `GET /agents/{id}/sessions/{session_id}` - Get session messages

### Utilities
- `GET /health` - Health check
- `GET /config/models` - List available models

## License

MIT
