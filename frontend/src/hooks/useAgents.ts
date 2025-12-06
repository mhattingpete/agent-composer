/**
 * React Query hooks for agent management.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentsApi, AgentResponse, CreateAgentRequest, UpdateAgentRequest } from '../services/api'

const AGENTS_QUERY_KEY = ['agents'] as const

/**
 * Hook to fetch all agents
 */
export function useAgents() {
  return useQuery({
    queryKey: AGENTS_QUERY_KEY,
    queryFn: agentsApi.list,
  })
}

/**
 * Hook to fetch a single agent by ID
 */
export function useAgent(id: string | null) {
  return useQuery({
    queryKey: [...AGENTS_QUERY_KEY, id],
    queryFn: () => agentsApi.get(id!),
    enabled: !!id,
  })
}

/**
 * Hook to create a new agent
 */
export function useCreateAgent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateAgentRequest) => agentsApi.create(data),
    onSuccess: (newAgent) => {
      queryClient.setQueryData<AgentResponse[]>(AGENTS_QUERY_KEY, (old) =>
        old ? [...old, newAgent] : [newAgent]
      )
    },
  })
}

/**
 * Hook to update an existing agent
 */
export function useUpdateAgent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateAgentRequest }) =>
      agentsApi.update(id, data),
    onSuccess: (updatedAgent) => {
      queryClient.setQueryData<AgentResponse[]>(AGENTS_QUERY_KEY, (old) =>
        old?.map((agent) => (agent.id === updatedAgent.id ? updatedAgent : agent)) ?? []
      )
      queryClient.setQueryData([...AGENTS_QUERY_KEY, updatedAgent.id], updatedAgent)
    },
  })
}

/**
 * Hook to delete an agent
 */
export function useDeleteAgent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => agentsApi.delete(id),
    onSuccess: (_, deletedId) => {
      queryClient.setQueryData<AgentResponse[]>(AGENTS_QUERY_KEY, (old) =>
        old?.filter((agent) => agent.id !== deletedId) ?? []
      )
      queryClient.removeQueries({ queryKey: [...AGENTS_QUERY_KEY, deletedId] })
    },
  })
}
