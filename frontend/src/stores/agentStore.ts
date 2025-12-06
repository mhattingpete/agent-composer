import { create } from 'zustand'

export interface Agent {
  id: string
  name: string
  description: string
  code: string
  model: string
  provider: 'openai' | 'anthropic' | 'openrouter' | 'ollama'
  isBuiltin: boolean
  tools: string[]
  createdAt: string
  updatedAt: string
}

interface AgentState {
  agents: Agent[]
  selectedAgentId: string | null
  isLoading: boolean
  error: string | null

  setAgents: (agents: Agent[]) => void
  setSelectedAgentId: (id: string | null) => void
  addAgent: (agent: Agent) => void
  updateAgent: (id: string, updates: Partial<Agent>) => void
  removeAgent: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  getSelectedAgent: () => Agent | undefined
}

export const useAgentStore = create<AgentState>((set, get) => ({
  agents: [],
  selectedAgentId: null,
  isLoading: false,
  error: null,

  setAgents: (agents) => set({ agents }),
  setSelectedAgentId: (id) => set({ selectedAgentId: id }),

  addAgent: (agent) =>
    set((state) => ({
      agents: [...state.agents, agent],
    })),

  updateAgent: (id, updates) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, ...updates, updatedAt: new Date().toISOString() } : agent
      ),
    })),

  removeAgent: (id) =>
    set((state) => ({
      agents: state.agents.filter((agent) => agent.id !== id),
      selectedAgentId: state.selectedAgentId === id ? null : state.selectedAgentId,
    })),

  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  getSelectedAgent: () => {
    const state = get()
    return state.agents.find((agent) => agent.id === state.selectedAgentId)
  },
}))
