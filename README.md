# Agent Composer

A local-first platform for designing, composing, and interacting with multi-agent AI systems.

## Features

- **Agent Studio**: AI-assisted agent creation with an in-browser code editor
- **Built-in Domain Agents**: Pre-configured agents for research, data analysis, writing, and coding
- **Team Builder**: Visual configuration for multi-agent workflows (sequential, parallel, router)
- **MCP Integration**: Connect to Model Context Protocol servers for extensible tool capabilities
- **Conversation UI**: Real-time streaming agent interactions via AG-UI

## Tech Stack

### Backend
- Python 3.11+
- Agno framework
- FastAPI
- SQLite

### Frontend
- React 18+ with TypeScript
- Bun package manager
- TailwindCSS
- Monaco Editor
- CopilotKit (AG-UI)

## Quick Start

### Prerequisites
- Python 3.11+
- Bun (or Node.js)
- At least one LLM API key (OpenAI, Anthropic) or Ollama running locally

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd agent-composer
```

2. Copy environment template and configure your API keys:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Run the setup script:
```bash
./init.sh
```

This will:
- Install backend Python dependencies
- Install frontend Node dependencies
- Start both development servers

### Manual Setup

If you prefer manual setup:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
bun install
bun run dev
```

## Development

### Project Structure

```
agent-composer/
├── backend/
│   ├── src/
│   │   ├── api/          # REST API endpoints
│   │   ├── agents/       # Agent definitions and registry
│   │   ├── agui/         # AG-UI protocol adapter
│   │   ├── database/     # SQLite models and migrations
│   │   ├── mcp/          # MCP client integration
│   │   └── runtime/      # Agent execution runtime
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Route pages
│   │   ├── stores/       # Zustand state stores
│   │   ├── hooks/        # Custom React hooks
│   │   └── lib/          # Utilities and API client
│   └── package.json
├── init.sh               # Development setup script
├── feature_list.json     # Feature test cases
└── README.md
```

### Available Scripts

```bash
# Start both servers
./init.sh

# Start only backend
./init.sh backend

# Start only frontend
./init.sh frontend

# Clean up (remove venvs and node_modules)
./init.sh clean
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `DEFAULT_OPENAI_MODEL` | Default OpenAI model | `gpt-4o` |
| `DEFAULT_ANTHROPIC_MODEL` | Default Anthropic model | `claude-3-5-sonnet-20241022` |
| `DEFAULT_OLLAMA_MODEL` | Default Ollama model | `llama3.2` |

## License

MIT
