/**
 * API client for Agent Composer backend.
 */
import { config } from '../config'

const API_BASE = config.apiBaseUrl

/**
 * Agent types matching backend schema
 */
export interface AgentResponse {
  id: string
  name: string
  description: string | null
  instructions: string | null
  provider: 'openai' | 'anthropic' | 'openrouter' | 'ollama'
  model_id: string
  code: string | null
  config: {
    temperature?: number
    max_tokens?: number | null
    top_p?: number | null
  }
  tools: string[]
  is_builtin: boolean
  created_at: string
  updated_at: string
}

export interface CreateAgentRequest {
  name: string
  description?: string
  instructions?: string
  provider: 'openai' | 'anthropic' | 'openrouter' | 'ollama'
  model_id?: string
  code?: string
  config?: {
    temperature?: number
    max_tokens?: number
    top_p?: number
  }
  tools?: string[]
}

export interface UpdateAgentRequest {
  name?: string
  description?: string
  instructions?: string
  provider?: 'openai' | 'anthropic' | 'openrouter' | 'ollama'
  model_id?: string
  code?: string
  config?: {
    temperature?: number
    max_tokens?: number
    top_p?: number
  }
  tools?: string[]
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text()
    let message = `Request failed with status ${response.status}`
    try {
      const errorJson = JSON.parse(errorText)
      message = errorJson.detail || errorJson.message || message
    } catch {
      if (errorText) message = errorText
    }
    throw new ApiError(response.status, message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

/**
 * Agent API endpoints
 */
export const agentsApi = {
  /**
   * List all agents
   */
  list: async (): Promise<AgentResponse[]> => {
    const response = await fetch(`${API_BASE}/api/agents`)
    return handleResponse<AgentResponse[]>(response)
  },

  /**
   * Get a single agent by ID
   */
  get: async (id: string): Promise<AgentResponse> => {
    const response = await fetch(`${API_BASE}/api/agents/${id}`)
    return handleResponse<AgentResponse>(response)
  },

  /**
   * Create a new agent
   */
  create: async (data: CreateAgentRequest): Promise<AgentResponse> => {
    const response = await fetch(`${API_BASE}/api/agents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return handleResponse<AgentResponse>(response)
  },

  /**
   * Update an existing agent
   */
  update: async (id: string, data: UpdateAgentRequest): Promise<AgentResponse> => {
    const response = await fetch(`${API_BASE}/api/agents/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return handleResponse<AgentResponse>(response)
  },

  /**
   * Delete an agent
   */
  delete: async (id: string): Promise<void> => {
    const response = await fetch(`${API_BASE}/api/agents/${id}`, {
      method: 'DELETE',
    })
    return handleResponse<void>(response)
  },
}

/**
 * Health check endpoint
 */
export const healthApi = {
  check: async (): Promise<{ status: string; service: string }> => {
    const response = await fetch(`${API_BASE}/health`)
    return handleResponse<{ status: string; service: string }>(response)
  },
}
