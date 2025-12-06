# Agent Composer - MVP Task Breakdown

Each task is self-contained, requires ≤5 file changes, and can be implemented/reviewed independently.

---

## Phase 0: Project Scaffolding

### Task 0.1: Initialize Backend Project Structure
**Goal:** Create Python backend skeleton with Agno
**Files:**
- `backend/pyproject.toml`
- `backend/src/__init__.py`
- `backend/src/main.py`
- `.gitignore`

**Acceptance Criteria:**
- [x] Python 3.11+ project with uv/pip
- [x] Agno installed as dependency
- [x] Basic FastAPI app runs on `localhost:8000`

---

### Task 0.2: Initialize Frontend Project Structure
**Goal:** Create React frontend skeleton with Bun
**Files:**
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`

**Acceptance Criteria:**
- [x] Bun-based React 18 project
- [x] TypeScript configured
- [x] Dev server runs on `localhost:5173`

---

### Task 0.3: Configure Environment Management
**Goal:** Set up environment variable handling
**Files:**
- `.env.example`
- `backend/src/config.py`
- `frontend/.env.example`
- `frontend/src/config.ts`

**Acceptance Criteria:**
- [x] `.env.example` with all required keys documented
- [x] Backend reads env vars with validation
- [x] Frontend reads public env vars
- [ ] Clear error messages for missing keys

---

### Task 0.4: Add TailwindCSS to Frontend
**Goal:** Set up styling infrastructure
**Files:**
- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- `frontend/src/index.css`
- `frontend/src/App.tsx` (update)

**Acceptance Criteria:**
- [x] TailwindCSS configured and working
- [x] Base styles applied
- [x] Dark mode support ready

---

## Phase 1: Core Backend Infrastructure

### Task 1.1: Set Up SQLite Database Schema
**Goal:** Create database for agent/team persistence
**Files:**
- `backend/src/database/__init__.py`
- `backend/src/database/models.py`
- `backend/src/database/connection.py`
- `backend/src/database/migrations.py`

**Acceptance Criteria:**
- [x] SQLite database file created on startup
- [x] Agent table schema defined
- [x] Team table schema defined
- [x] Conversation/session table schema defined

---

### Task 1.2: Create Agent CRUD API
**Goal:** REST endpoints for agent management
**Files:**
- `backend/src/api/__init__.py`
- `backend/src/api/agents.py`
- `backend/src/main.py` (update to mount router)

**Acceptance Criteria:**
- [x] `GET /api/agents` - list all agents
- [x] `GET /api/agents/{id}` - get single agent
- [x] `POST /api/agents` - create agent
- [x] `PUT /api/agents/{id}` - update agent
- [x] `DELETE /api/agents/{id}` - delete agent

---

### Task 1.3: Integrate AG-UI Adapter
**Goal:** Set up AG-UI protocol for frontend communication
**Files:**
- `backend/src/agui/__init__.py`
- `backend/src/agui/adapter.py`
- `backend/src/agui/events.py`
- `backend/src/main.py` (update)

**Acceptance Criteria:**
- [x] AG-UI endpoint at `/api/agui`
- [x] SSE streaming configured
- [x] Event types defined (message, tool_call, state_update)

---

### Task 1.4: Create Agent Runtime Service
**Goal:** Load and execute Agno agents using built-in model classes
**Files:**
- `backend/src/runtime/__init__.py`
- `backend/src/runtime/executor.py`
- `backend/src/runtime/loader.py`

**Acceptance Criteria:**
- [x] Load agent definition from database
- [x] Instantiate Agno Agent with appropriate model (OpenAIChat, Claude, Ollama, OpenRouter)
- [x] Execute agent with user message
- [x] Stream response via AG-UI

*Note: Uses Agno's built-in model classes directly - no custom provider wrapper needed.*

---

## Phase 2: Frontend Shell

### Task 2.1: Create App Layout and Navigation
**Goal:** Basic app shell with sidebar navigation
**Files:**
- `frontend/src/components/Layout.tsx`
- `frontend/src/components/Sidebar.tsx`
- `frontend/src/components/Header.tsx`
- `frontend/src/App.tsx` (update)

**Acceptance Criteria:**
- [x] Sidebar with navigation links
- [x] Header with app title
- [x] Main content area
- [x] Responsive layout

---

### Task 2.2: Set Up React Router
**Goal:** Client-side routing for main views
**Files:**
- `frontend/src/router.tsx`
- `frontend/src/pages/ConversationPage.tsx`
- `frontend/src/pages/AgentStudioPage.tsx`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/App.tsx` (update)

**Acceptance Criteria:**
- [x] Routes: `/`, `/studio`, `/settings`
- [x] Placeholder pages for each route
- [x] Navigation updates URL

---

### Task 2.3: Add Zustand State Management
**Goal:** Global state for agents and settings
**Files:**
- `frontend/src/stores/agentStore.ts`
- `frontend/src/stores/settingsStore.ts`
- `frontend/src/stores/index.ts`

**Acceptance Criteria:**
- [x] Agent store: list, selected agent
- [x] Settings store: API keys, preferences
- [x] Persistence to localStorage

---

### Task 2.4: Add React Query for API Calls
**Goal:** Data fetching and caching layer
**Files:**
- `frontend/src/services/api.ts`
- `frontend/src/services/queryClient.ts`
- `frontend/src/hooks/useAgents.ts`
- `frontend/src/main.tsx` (update)

**Acceptance Criteria:**
- [x] API client configured
- [x] Query client provider set up
- [x] `useAgents` hook for fetching agents
- [x] Loading and error states handled

---

## Phase 3: Conversation UI

### Task 3.1: Create Chat Message Components
**Goal:** Display chat messages
**Files:**
- `frontend/src/components/chat/ChatMessage.tsx`
- `frontend/src/components/chat/ChatMessageList.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`

**Acceptance Criteria:**
- [ ] User message bubble (right-aligned)
- [ ] Agent message bubble (left-aligned)
- [ ] Markdown rendering support
- [ ] Code block syntax highlighting

---

### Task 3.2: Create Chat Input Component
**Goal:** Text input for sending messages
**Files:**
- `frontend/src/components/chat/ChatInput.tsx`
- `frontend/src/components/chat/FileAttachment.tsx`

**Acceptance Criteria:**
- [ ] Multi-line text input
- [ ] Send button and Enter key support
- [ ] File attachment button (UI only)
- [ ] Disabled state while agent responding

---

### Task 3.3: Integrate CopilotKit for AG-UI
**Goal:** Connect frontend to AG-UI backend
**Files:**
- `frontend/src/lib/agui.ts`
- `frontend/src/hooks/useChat.ts`
- `frontend/src/pages/ConversationPage.tsx` (update)

**Acceptance Criteria:**
- [ ] CopilotKit provider configured
- [ ] `useChat` hook connects to backend
- [ ] Messages stream in real-time
- [ ] Conversation state persisted

---

### Task 3.4: Add Agent Selector to Chat
**Goal:** Switch between agents in conversation
**Files:**
- `frontend/src/components/chat/AgentSelector.tsx`
- `frontend/src/pages/ConversationPage.tsx` (update)

**Acceptance Criteria:**
- [ ] Dropdown to select agent
- [ ] Shows agent name and description
- [ ] Switching agent updates chat context
- [ ] Current agent indicator

---

### Task 3.5: Add Conversation History Sidebar
**Goal:** List and manage past conversations
**Files:**
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/components/chat/ConversationItem.tsx`
- `frontend/src/hooks/useConversations.ts`
- `frontend/src/pages/ConversationPage.tsx` (update)

**Acceptance Criteria:**
- [ ] List of past conversations
- [ ] Create new conversation button
- [ ] Delete conversation option
- [ ] Conversation titles (auto-generated or editable)

---

## Phase 4: Built-in Agents

### Task 4.1: Create Agent Definition Schema
**Goal:** Define structure for agent configurations
**Files:**
- `backend/src/agents/__init__.py`
- `backend/src/agents/schema.py`
- `backend/src/agents/validator.py`

**Acceptance Criteria:**
- [ ] Pydantic schema for agent definition
- [ ] Validation for required fields
- [ ] Support for tools, instructions, model config

---

### Task 4.2: Implement Research Assistant Agent
**Goal:** First built-in domain agent
**Files:**
- `backend/src/agents/builtin/__init__.py`
- `backend/src/agents/builtin/research_assistant.py`
- `backend/src/agents/registry.py`

**Acceptance Criteria:**
- [ ] Web search tool integration
- [ ] Summarization instructions
- [ ] Registered as built-in agent
- [ ] Works in conversation UI

---

### Task 4.3: Implement Data Analyst Agent
**Goal:** Agent for data analysis tasks
**Files:**
- `backend/src/agents/builtin/data_analyst.py`
- `backend/src/agents/registry.py` (update)

**Acceptance Criteria:**
- [ ] CSV/JSON parsing capability
- [ ] Analysis instructions
- [ ] Visualization suggestions in responses

---

### Task 4.4: Implement Content Writer Agent
**Goal:** Agent for content creation
**Files:**
- `backend/src/agents/builtin/content_writer.py`
- `backend/src/agents/registry.py` (update)

**Acceptance Criteria:**
- [ ] Writing style instructions
- [ ] Multiple content types supported
- [ ] Editing/revision capability

---

### Task 4.5: Implement Code Assistant Agent
**Goal:** Agent for code-related tasks
**Files:**
- `backend/src/agents/builtin/code_assistant.py`
- `backend/src/agents/registry.py` (update)

**Acceptance Criteria:**
- [ ] Code review instructions
- [ ] Multiple language support
- [ ] Refactoring suggestions

---

## Phase 5: Agent Studio

### Task 5.1: Add Monaco Editor Component
**Goal:** Code editor for agent definitions
**Files:**
- `frontend/src/components/editor/MonacoEditor.tsx`
- `frontend/src/components/editor/EditorToolbar.tsx`
- `frontend/src/pages/AgentStudioPage.tsx` (update)

**Acceptance Criteria:**
- [ ] Monaco editor renders Python code
- [ ] Syntax highlighting for Python
- [ ] Editor toolbar with save button
- [ ] Resizable editor panel

---

### Task 5.2: Create Agent Description Input
**Goal:** Natural language input for agent generation
**Files:**
- `frontend/src/components/studio/AgentDescriptionInput.tsx`
- `frontend/src/components/studio/GenerateButton.tsx`
- `frontend/src/pages/AgentStudioPage.tsx` (update)

**Acceptance Criteria:**
- [ ] Text area for agent description
- [ ] "Generate Agent" button
- [ ] Loading state during generation
- [ ] Example prompts/suggestions

---

### Task 5.3: Implement Agent Generator Backend
**Goal:** AI agent that generates agent definitions
**Files:**
- `backend/src/agents/builtin/agent_generator.py`
- `backend/src/api/generate.py`
- `backend/src/main.py` (update)

**Acceptance Criteria:**
- [ ] `POST /api/generate` endpoint
- [ ] Takes description, returns agent code
- [ ] Uses structured prompts for valid output
- [ ] Includes appropriate tools based on description

---

### Task 5.4: Add Agent Review Actions
**Goal:** Accept/Edit/Regenerate/Delete workflow
**Files:**
- `frontend/src/components/studio/ReviewActions.tsx`
- `frontend/src/components/studio/RegenerateDialog.tsx`
- `frontend/src/pages/AgentStudioPage.tsx` (update)

**Acceptance Criteria:**
- [ ] Accept button saves agent
- [ ] Edit mode enables Monaco editor
- [ ] Regenerate opens feedback dialog
- [ ] Delete clears and resets

---

### Task 5.5: Add Agent Validation and Testing
**Goal:** Validate and test agent before saving
**Files:**
- `backend/src/api/validate.py`
- `frontend/src/components/studio/ValidationPanel.tsx`
- `frontend/src/components/studio/TestChat.tsx`
- `frontend/src/pages/AgentStudioPage.tsx` (update)

**Acceptance Criteria:**
- [ ] `POST /api/validate` checks agent code
- [ ] Validation errors displayed inline
- [ ] Mini chat panel for testing
- [ ] Test before save workflow

---

### Task 5.6: Add Agent Library Sidebar
**Goal:** List and manage saved agents
**Files:**
- `frontend/src/components/studio/AgentLibrary.tsx`
- `frontend/src/components/studio/AgentCard.tsx`
- `frontend/src/pages/AgentStudioPage.tsx` (update)

**Acceptance Criteria:**
- [ ] List of saved agents
- [ ] Built-in agents marked distinctly
- [ ] Click to load in editor
- [ ] Delete custom agents

---

## Phase 6: MCP Integration

### Task 6.1: Create MCP Client Wrapper
**Goal:** Client for connecting to MCP servers
**Files:**
- `backend/src/mcp/__init__.py`
- `backend/src/mcp/client.py`
- `backend/src/mcp/types.py`

**Acceptance Criteria:**
- [ ] Connect to MCP server by URL
- [ ] List available tools from server
- [ ] Execute tool calls
- [ ] Handle connection errors

---

### Task 6.2: Add MCP Server Database Model
**Goal:** Persist MCP server configurations
**Files:**
- `backend/src/database/models.py` (update)
- `backend/src/api/mcp.py`
- `backend/src/main.py` (update)

**Acceptance Criteria:**
- [ ] MCP server table schema
- [ ] CRUD endpoints for MCP servers
- [ ] Store URL, auth config, status

---

### Task 6.3: Create MCP Manager UI
**Goal:** Frontend for managing MCP servers
**Files:**
- `frontend/src/pages/MCPManagerPage.tsx`
- `frontend/src/components/mcp/MCPServerList.tsx`
- `frontend/src/components/mcp/AddServerDialog.tsx`
- `frontend/src/router.tsx` (update)

**Acceptance Criteria:**
- [ ] List connected MCP servers
- [ ] Add server dialog with URL input
- [ ] Connection status indicator
- [ ] Remove server option

---

### Task 6.4: Add Tool Assignment to Agents
**Goal:** Assign MCP tools to agents
**Files:**
- `frontend/src/components/studio/ToolAssignment.tsx`
- `backend/src/agents/schema.py` (update)
- `backend/src/runtime/executor.py` (update)

**Acceptance Criteria:**
- [ ] UI to select tools for agent
- [ ] Tools from connected MCP servers listed
- [ ] Selected tools saved with agent
- [ ] Agent runtime loads assigned tools

---

### Task 6.5: Add MCP Server Health Monitoring
**Goal:** Monitor MCP server status
**Files:**
- `backend/src/mcp/health.py`
- `backend/src/api/mcp.py` (update)
- `frontend/src/components/mcp/ServerStatus.tsx`

**Acceptance Criteria:**
- [ ] Health check endpoint
- [ ] Periodic status polling
- [ ] Visual status indicators
- [ ] Reconnection on failure

---

## Phase 7: Team Builder

### Task 7.1: Create Team Database Model
**Goal:** Persist team configurations
**Files:**
- `backend/src/database/models.py` (update)
- `backend/src/api/teams.py`
- `backend/src/main.py` (update)

**Acceptance Criteria:**
- [ ] Team table with members, mode
- [ ] CRUD endpoints for teams
- [ ] Link agents to teams

---

### Task 7.2: Create Team Builder Page
**Goal:** UI for composing agent teams
**Files:**
- `frontend/src/pages/TeamBuilderPage.tsx`
- `frontend/src/components/teams/TeamCanvas.tsx`
- `frontend/src/router.tsx` (update)

**Acceptance Criteria:**
- [ ] Page for team configuration
- [ ] Visual canvas for team layout
- [ ] Navigation link added

---

### Task 7.3: Add Agent Selection for Teams
**Goal:** Select agents to include in team
**Files:**
- `frontend/src/components/teams/AgentPicker.tsx`
- `frontend/src/components/teams/TeamMemberCard.tsx`
- `frontend/src/pages/TeamBuilderPage.tsx` (update)

**Acceptance Criteria:**
- [ ] List available agents
- [ ] Drag or click to add to team
- [ ] Reorder team members
- [ ] Remove from team

---

### Task 7.4: Add Execution Mode Selection
**Goal:** Configure team execution pattern
**Files:**
- `frontend/src/components/teams/ExecutionModeSelector.tsx`
- `frontend/src/components/teams/ModeDescription.tsx`
- `frontend/src/pages/TeamBuilderPage.tsx` (update)

**Acceptance Criteria:**
- [ ] Sequential mode option
- [ ] Parallel mode option
- [ ] Router mode option
- [ ] Mode descriptions displayed

---

### Task 7.5: Implement Team Runtime Service
**Goal:** Load and execute Agno Teams (leverages built-in modes)
**Files:**
- `backend/src/runtime/team_executor.py`
- `backend/src/agui/adapter.py` (update)

**Acceptance Criteria:**
- [ ] Load team configuration from database
- [ ] Instantiate Agno Team with configured mode (sequential/parallel/router)
- [ ] Stream team responses via AG-UI
- [ ] Handle agent failures gracefully

*Note: Agno's Team class natively supports sequential, parallel, and router modes - no custom implementation needed.*

---

### Task 7.6: Add Team to Conversation UI
**Goal:** Select teams in chat interface
**Files:**
- `frontend/src/components/chat/AgentSelector.tsx` (update)
- `frontend/src/hooks/useTeams.ts`
- `frontend/src/pages/ConversationPage.tsx` (update)

**Acceptance Criteria:**
- [ ] Teams appear in agent selector
- [ ] Team indicator shows members
- [ ] Chat works with teams
- [ ] Team responses attributed correctly

---

## Phase 8: Settings & Polish

### Task 8.1: Create Settings Page
**Goal:** Configure API keys and preferences
**Files:**
- `frontend/src/pages/SettingsPage.tsx` (update)
- `frontend/src/components/settings/APIKeyForm.tsx`
- `frontend/src/components/settings/ProviderSection.tsx`

**Acceptance Criteria:**
- [ ] API key input for each provider
- [ ] Keys masked by default
- [ ] Save to local storage (encrypted)
- [ ] Connection test button

---

### Task 8.2: Add Model Selection
**Goal:** Configure default models per provider
**Files:**
- `frontend/src/components/settings/ModelSelector.tsx`
- `frontend/src/stores/settingsStore.ts` (update)
- `frontend/src/pages/SettingsPage.tsx` (update)

**Acceptance Criteria:**
- [ ] Dropdown for each provider
- [ ] List available models
- [ ] Custom model ID input
- [ ] Default model per provider

---

### Task 8.3: Add Error Handling and Notifications
**Goal:** User-friendly error messages
**Files:**
- `frontend/src/components/common/Toast.tsx`
- `frontend/src/components/common/ErrorBoundary.tsx`
- `frontend/src/lib/notifications.ts`
- `frontend/src/App.tsx` (update)

**Acceptance Criteria:**
- [ ] Toast notification system
- [ ] Error boundary catches crashes
- [ ] Graceful degradation
- [ ] Retry options where applicable

---

### Task 8.4: Add Loading States and Skeletons
**Goal:** Polish loading experience
**Files:**
- `frontend/src/components/common/Skeleton.tsx`
- `frontend/src/components/common/LoadingSpinner.tsx`
- `frontend/src/components/chat/ChatMessageList.tsx` (update)
- `frontend/src/components/studio/AgentLibrary.tsx` (update)

**Acceptance Criteria:**
- [ ] Skeleton loaders for lists
- [ ] Spinner for actions
- [ ] Consistent loading patterns
- [ ] No layout shift

---

### Task 8.5: Add Keyboard Shortcuts
**Goal:** Power user productivity
**Files:**
- `frontend/src/hooks/useKeyboardShortcuts.ts`
- `frontend/src/components/common/ShortcutHelp.tsx`
- `frontend/src/App.tsx` (update)

**Acceptance Criteria:**
- [ ] `Cmd+Enter` to send message
- [ ] `Cmd+N` for new conversation
- [ ] `Cmd+/` for shortcut help
- [ ] `Escape` to close dialogs

---

## Summary

| Phase | Tasks | Focus Area |
|-------|-------|------------|
| 0 | 4 | Project scaffolding |
| 1 | 4 | Backend infrastructure |
| 2 | 4 | Frontend shell |
| 3 | 5 | Conversation UI |
| 4 | 5 | Built-in agents |
| 5 | 6 | Agent Studio |
| 6 | 5 | MCP integration |
| 7 | 6 | Team Builder |
| 8 | 5 | Settings & polish |

**Total: 44 tasks**

*Note: LLM provider tasks removed (Agno provides OpenAIChat, Claude, Ollama). Team execution simplified (Agno's Team class handles modes natively).*

Each task is designed to be:
- Completable in a single PR
- Reviewable by examining ≤5 files
- Testable independently
- Building toward the MVP incrementally
