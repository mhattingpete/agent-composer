# Agent Composer - Product Requirements Document

## 1. Overview

### Vision
Agent Composer is a local-first platform for designing, composing, and interacting with multi-agent AI systems. It provides an intuitive interface for creating custom agents, combining them into collaborative teams, and extending their capabilities through tools and MCP servers.

### Goals
- Enable users to design custom AI agents through an in-browser code editor
- Provide pre-built domain agents for common use cases
- Support multi-agent collaboration (sequential and parallel)
- Integrate with the MCP ecosystem for extensible tool capabilities
- Deliver real-time, streaming agent interactions via AG-UI

### Target Users
- **Developers**: Build and customize agents with Python code
- **Power Users**: Configure pre-built agents and compose workflows
- **End Users**: Interact with agents through a polished chat interface

---

## 2. Technical Architecture

### Stack Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Agent Studio │  │ Team Builder │  │ Conversation UI    │  │
│  │ (Monaco)     │  │              │  │ (CopilotKit)       │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                         AG-UI Protocol
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Backend (Agno AgentOS)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Agent Runtime│  │ Team Orchestr│  │ MCP Gateway        │  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
         ┌────┴────┐    ┌─────┴─────┐   ┌─────┴─────┐
         │ OpenAI  │    │ Anthropic │   │  Ollama   │
         └─────────┘    └───────────┘   └───────────┘
```

### Core Technologies
- **Backend**: Python 3.11+, Agno framework, FastAPI
- **Frontend**: React 18+, TypeScript, CopilotKit, Monaco Editor
- **Protocol**: AG-UI for agent-frontend communication
- **Database**: SQLite (local persistence)
- **MCP**: Model Context Protocol for tool integration

---

## 3. MVP Features

### 3.1 Agent Studio
AI-assisted agent creation with an in-browser code editor for review and customization.

**Agent Generation Flow:**
1. User describes desired agent in natural language (e.g., "An agent that helps me analyze CSV files and create charts")
2. Built-in **Agent Generator** creates a complete agent definition
3. User reviews the generated code in Monaco editor
4. User can:
   - **Accept**: Save and deploy the agent
   - **Edit**: Modify the generated code manually
   - **Regenerate**: Provide feedback and generate a new version
   - **Delete**: Discard and start over

**Capabilities:**
- Natural language agent description input
- AI-powered agent code generation
- Monaco-based Python editor for review/editing
- Live validation and error feedback
- Save/load agent definitions locally
- Hot-reload agent changes

**Generated Agent Format:**
```python
from agno import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    name="Research Assistant",
    model=OpenAIChat(id="gpt-4o"),
    instructions=["You are a research assistant..."],
    tools=[...],
)
```

### 3.2 Built-in Domain Agents
Pre-configured agents for common tasks.

**MVP Agents:**
| Agent | Purpose |
|-------|---------|
| **Agent Generator** | Creates new agent definitions from natural language descriptions (system agent) |
| Research Assistant | Web search, summarization, fact-checking |
| Data Analyst | CSV/JSON analysis, visualization suggestions |
| Content Writer | Blog posts, documentation, copywriting |
| Code Assistant | Code review, explanation, refactoring |

### 3.3 Tool & MCP Manager
Interface for managing agent tools and MCP servers.

**Capabilities:**
- Connect to existing MCP servers (filesystem, GitHub, Slack, etc.)
- Create custom MCP server definitions
- Tool marketplace with community contributions
- Per-agent tool assignment
- MCP server health monitoring

### 3.4 Team Builder
Visual configuration for multi-agent workflows.

**Modes:**
- **Sequential Pipeline**: Agents process in order, passing context
- **Parallel Execution**: Multiple agents work simultaneously
- **Router Pattern**: Intelligent task distribution based on content

**Configuration:**
```python
from agno import Team

team = Team(
    name="Content Pipeline",
    members=[research_agent, writer_agent, editor_agent],
    mode="sequential",
)
```

### 3.5 Conversation UI
AG-UI powered chat interface for agent interaction.

**Features:**
- Real-time streaming responses
- Multi-turn conversation with memory
- File attachments (documents, images, code)
- Human-in-the-loop approvals for sensitive actions
- Conversation history and session management
- Switch between agents/teams mid-conversation

---

## 4. Non-Goals (MVP)

- Cloud/SaaS deployment (local-only for MVP)
- Visual drag-and-drop agent builder
- Mobile applications
- Multi-user collaboration
- Agent marketplace with monetization
- Voice interaction

---

## 5. User Flows

### 5.1 Create Custom Agent
1. Open Agent Studio
2. Describe desired agent in natural language
3. Agent Generator creates agent definition
4. Review generated code in editor
5. Choose action:
   - **Accept**: Proceed to configuration
   - **Edit**: Modify code manually, then accept
   - **Regenerate**: Provide feedback, get new version
   - **Delete**: Start over
6. Configure model provider (if not auto-selected)
7. Assign additional tools/MCP servers (optional)
8. Test in conversation UI
9. Save agent

### 5.2 Compose Agent Team
1. Open Team Builder
2. Select agents to include
3. Choose execution mode (sequential/parallel/router)
4. Configure handoff rules
5. Test team workflow
6. Save team configuration

### 5.3 Add MCP Server
1. Open Tool & MCP Manager
2. Click "Add MCP Server"
3. Enter server URL or select from catalog
4. Configure authentication if required
5. Test connection
6. Assign to agents

---

## 6. Technical Requirements

### 6.1 Backend Requirements
- Python 3.11+
- Agno framework with AgentOS
- FastAPI for API endpoints
- AG-UI adapter for frontend communication
- SQLite for local storage
- Support for multiple LLM providers:
  - OpenAI (GPT-4o, GPT-4o-mini, fine-tuned models)
  - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
  - Ollama (local models)
- Fine-tuned model support via custom model ID configuration

### 6.2 Frontend Requirements
- React 18+ with TypeScript
- Bun as package manager and runtime
- CopilotKit for AG-UI integration
- Monaco Editor for code editing
- TailwindCSS for styling
- React Query for state management
- Zustand for global state

### 6.3 Development Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m agno serve

# Frontend
cd frontend
bun install
bun run dev
```

### 6.4 API Key Management
- Environment variables via `.env` file (gitignored)
- `.env.example` template provided for required keys
- Settings UI for non-technical users (stored encrypted via `keyring`)
- Startup validation with clear error messages for missing keys

---

## 7. Success Metrics

### MVP Launch Criteria
- [ ] Agent Generator can create agents from natural language descriptions
- [ ] Users can review, edit, accept, or regenerate generated agents
- [ ] At least 4 built-in domain agents functional
- [ ] MCP server connection working (3+ servers)
- [ ] Sequential and parallel team execution working
- [ ] Conversation UI with streaming responses
- [ ] All 3 LLM providers integrated

### Quality Metrics
- Agent response latency < 500ms to first token
- UI renders at 60fps during streaming
- Zero data loss on conversation save
- Error recovery without full page reload

---

## 8. Decisions & Future Considerations

### Decided for MVP
- **Agent Versioning**: No - not needed for MVP
- **Fine-tuned Models**: Yes - support custom model IDs
- **API Key Management**: Environment variables + encrypted Settings UI

### Future Considerations
- Export/import agent configurations (post-MVP)

---

## 9. References

- [Agno Documentation](https://docs.agno.com)
- [AG-UI Protocol](https://docs.ag-ui.com)
- [CopilotKit](https://docs.copilotkit.ai)
- [Model Context Protocol](https://modelcontextprotocol.io)
