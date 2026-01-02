import { toast } from 'sonner'

import { APIRoutes } from './routes'

import { AgentDetails, Sessions, TeamDetails } from '@/types/os'

// Helper function to create headers with optional auth token
const createHeaders = (authToken?: string): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json'
  }

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`
  }

  return headers
}

export const getAgentsAPI = async (
  endpoint: string,
  authToken?: string
): Promise<AgentDetails[]> => {
  const url = APIRoutes.GetAgents(endpoint)
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!response.ok) {
      toast.error(`Failed to fetch  agents: ${response.statusText}`)
      return []
    }
    const data = await response.json()
    return data
  } catch {
    toast.error('Error fetching  agents')
    return []
  }
}

export const getStatusAPI = async (
  base: string,
  authToken?: string
): Promise<number> => {
  const response = await fetch(APIRoutes.Status(base), {
    method: 'GET',
    headers: createHeaders(authToken)
  })
  return response.status
}

export const getAllSessionsAPI = async (
  base: string,
  type: 'agent' | 'team',
  componentId: string,
  dbId: string,
  authToken?: string
): Promise<Sessions | { data: [] }> => {
  try {
    const url = new URL(APIRoutes.GetSessions(base))
    url.searchParams.set('type', type)
    url.searchParams.set('component_id', componentId)
    url.searchParams.set('db_id', dbId)

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: createHeaders(authToken)
    })

    if (!response.ok) {
      if (response.status === 404) {
        return { data: [] }
      }
      throw new Error(`Failed to fetch sessions: ${response.statusText}`)
    }
    return response.json()
  } catch {
    return { data: [] }
  }
}

export const getSessionAPI = async (
  base: string,
  type: 'agent' | 'team',
  sessionId: string,
  dbId?: string,
  authToken?: string
) => {
  // build query string
  const queryParams = new URLSearchParams({ type })
  if (dbId) queryParams.append('db_id', dbId)

  const response = await fetch(
    `${APIRoutes.GetSession(base, sessionId)}?${queryParams.toString()}`,
    {
      method: 'GET',
      headers: createHeaders(authToken)
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch session: ${response.statusText}`)
  }

  return response.json()
}

export const deleteSessionAPI = async (
  base: string,
  dbId: string,
  sessionId: string,
  authToken?: string
) => {
  const queryParams = new URLSearchParams()
  if (dbId) queryParams.append('db_id', dbId)
  const response = await fetch(
    `${APIRoutes.DeleteSession(base, sessionId)}?${queryParams.toString()}`,
    {
      method: 'DELETE',
      headers: createHeaders(authToken)
    }
  )
  return response
}

export const getTeamsAPI = async (
  endpoint: string,
  authToken?: string
): Promise<TeamDetails[]> => {
  const url = APIRoutes.GetTeams(endpoint)
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!response.ok) {
      toast.error(`Failed to fetch  teams: ${response.statusText}`)
      return []
    }
    const data = await response.json()

    return data
  } catch {
    toast.error('Error fetching  teams')
    return []
  }
}

export const deleteTeamSessionAPI = async (
  base: string,
  teamId: string,
  sessionId: string,
  authToken?: string
) => {
  const response = await fetch(
    APIRoutes.DeleteTeamSession(base, teamId, sessionId),
    {
      method: 'DELETE',
      headers: createHeaders(authToken)
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to delete team session: ${response.statusText}`)
  }
  return response
}

// =============================================================================
// Config API - for managing custom agents and teams
// =============================================================================

export interface ModelInfo {
  id: string
  name: string
  provider: string
}

export interface AgentConfigCreate {
  name: string
  description: string
  model_id: string
  instructions: string
}

export interface AgentConfigResponse extends AgentConfigCreate {
  id: string
  builtin: boolean
}

export interface TeamMember {
  name: string
  role: string
  has_tools: boolean
}

export interface TeamConfigCreate {
  name: string
  description: string
  members: TeamMember[]
}

export interface TeamConfigResponse extends TeamConfigCreate {
  id: string
  builtin: boolean
}

export const getModelsAPI = async (
  endpoint: string,
  authToken?: string
): Promise<ModelInfo[]> => {
  try {
    const response = await fetch(APIRoutes.GetModels(endpoint), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!response.ok) {
      toast.error(`Failed to fetch models: ${response.statusText}`)
      return []
    }
    return response.json()
  } catch {
    toast.error('Error fetching models')
    return []
  }
}

export const getCustomAgentsAPI = async (
  endpoint: string,
  authToken?: string
): Promise<AgentConfigResponse[]> => {
  try {
    const response = await fetch(APIRoutes.GetCustomAgents(endpoint), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!response.ok) {
      toast.error(`Failed to fetch custom agents: ${response.statusText}`)
      return []
    }
    return response.json()
  } catch {
    toast.error('Error fetching custom agents')
    return []
  }
}

export const createAgentAPI = async (
  endpoint: string,
  agent: AgentConfigCreate,
  authToken?: string
): Promise<AgentConfigResponse | null> => {
  try {
    const response = await fetch(APIRoutes.CreateAgent(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify(agent)
    })
    if (!response.ok) {
      const error = await response.json()
      toast.error(`Failed to create agent: ${error.detail || response.statusText}`)
      return null
    }
    toast.success('Agent created successfully')
    return response.json()
  } catch {
    toast.error('Error creating agent')
    return null
  }
}

export const updateAgentAPI = async (
  endpoint: string,
  agentId: string,
  updates: Partial<AgentConfigCreate>,
  authToken?: string
): Promise<AgentConfigResponse | null> => {
  try {
    const response = await fetch(APIRoutes.UpdateAgent(endpoint, agentId), {
      method: 'PUT',
      headers: createHeaders(authToken),
      body: JSON.stringify(updates)
    })
    if (!response.ok) {
      toast.error(`Failed to update agent: ${response.statusText}`)
      return null
    }
    toast.success('Agent updated successfully')
    return response.json()
  } catch {
    toast.error('Error updating agent')
    return null
  }
}

export const deleteAgentAPI = async (
  endpoint: string,
  agentId: string,
  authToken?: string
): Promise<boolean> => {
  try {
    const response = await fetch(APIRoutes.DeleteAgent(endpoint, agentId), {
      method: 'DELETE',
      headers: createHeaders(authToken)
    })
    if (!response.ok) {
      toast.error(`Failed to delete agent: ${response.statusText}`)
      return false
    }
    toast.success('Agent deleted successfully')
    return true
  } catch {
    toast.error('Error deleting agent')
    return false
  }
}

export const getCustomTeamsAPI = async (
  endpoint: string,
  authToken?: string
): Promise<TeamConfigResponse[]> => {
  try {
    const response = await fetch(APIRoutes.GetCustomTeams(endpoint), {
      method: 'GET',
      headers: createHeaders(authToken)
    })
    if (!response.ok) {
      toast.error(`Failed to fetch custom teams: ${response.statusText}`)
      return []
    }
    return response.json()
  } catch {
    toast.error('Error fetching custom teams')
    return []
  }
}

export const createTeamAPI = async (
  endpoint: string,
  team: TeamConfigCreate,
  authToken?: string
): Promise<TeamConfigResponse | null> => {
  try {
    const response = await fetch(APIRoutes.CreateTeam(endpoint), {
      method: 'POST',
      headers: createHeaders(authToken),
      body: JSON.stringify(team)
    })
    if (!response.ok) {
      const error = await response.json()
      toast.error(`Failed to create team: ${error.detail || response.statusText}`)
      return null
    }
    toast.success('Team created successfully')
    return response.json()
  } catch {
    toast.error('Error creating team')
    return null
  }
}

export const deleteTeamConfigAPI = async (
  endpoint: string,
  teamId: string,
  authToken?: string
): Promise<boolean> => {
  try {
    const response = await fetch(APIRoutes.DeleteTeam(endpoint, teamId), {
      method: 'DELETE',
      headers: createHeaders(authToken)
    })
    if (!response.ok) {
      toast.error(`Failed to delete team: ${response.statusText}`)
      return false
    }
    toast.success('Team deleted successfully')
    return true
  } catch {
    toast.error('Error deleting team')
    return false
  }
}
