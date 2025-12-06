import { useState } from 'react'
import { useAgents, useCreateAgent, useDeleteAgent } from '../hooks/useAgents'
import type { AgentResponse } from '../services/api'

export default function AgentStudioPage() {
  const { data: agents, isLoading, error } = useAgents()
  const createAgent = useCreateAgent()
  const deleteAgent = useDeleteAgent()
  const [selectedAgent, setSelectedAgent] = useState<AgentResponse | null>(null)
  const [agentDescription, setAgentDescription] = useState('')

  const handleCreateAgent = () => {
    if (!agentDescription.trim()) return

    createAgent.mutate(
      {
        name: 'New Agent',
        description: agentDescription,
        provider: 'openai',
        model_id: 'gpt-4o',
      },
      {
        onSuccess: (newAgent) => {
          setSelectedAgent(newAgent)
          setAgentDescription('')
        },
      }
    )
  }

  const handleDeleteAgent = (id: string) => {
    if (!confirm('Are you sure you want to delete this agent?')) return

    deleteAgent.mutate(id, {
      onSuccess: () => {
        if (selectedAgent?.id === id) {
          setSelectedAgent(null)
        }
      },
    })
  }

  return (
    <div className="flex h-full gap-6">
      {/* Agent Library Sidebar */}
      <div className="w-64 flex-shrink-0">
        <div className="card h-full overflow-hidden flex flex-col">
          <h2 className="text-lg font-semibold mb-4">Agent Library</h2>

          {isLoading && (
            <div className="flex-1 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
              Failed to load agents: {error.message}
            </div>
          )}

          {!isLoading && !error && agents && (
            <div className="flex-1 overflow-y-auto space-y-2">
              {agents.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  No agents yet. Create one below!
                </p>
              ) : (
                agents.map((agent) => (
                  <div
                    key={agent.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedAgent?.id === agent.id
                        ? 'bg-primary-100 dark:bg-primary-900/20 border border-primary-500'
                        : 'bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600'
                    }`}
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium truncate">{agent.name}</h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                          {agent.description || 'No description'}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs px-2 py-0.5 bg-gray-200 dark:bg-dark-600 rounded">
                            {agent.provider}
                          </span>
                          {agent.is_builtin && (
                            <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                              Built-in
                            </span>
                          )}
                        </div>
                      </div>
                      {!agent.is_builtin && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteAgent(agent.id)
                          }}
                          className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                          title="Delete agent"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Editor Area */}
      <div className="flex-1 flex flex-col gap-4">
        {/* Agent Description Input */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Create New Agent</h2>
          <textarea
            value={agentDescription}
            onChange={(e) => setAgentDescription(e.target.value)}
            placeholder="Describe the agent you want to create... (e.g., 'An agent that helps me analyze CSV files and create charts')"
            className="input min-h-[100px] resize-none mb-4"
          />
          <button
            onClick={handleCreateAgent}
            disabled={!agentDescription.trim() || createAgent.isPending}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createAgent.isPending ? 'Creating...' : 'Generate Agent'}
          </button>
          {createAgent.isError && (
            <p className="mt-2 text-sm text-red-500">
              Failed to create agent: {createAgent.error.message}
            </p>
          )}
        </div>

        {/* Code Editor / Agent Details */}
        <div className="card flex-1">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">
              {selectedAgent ? selectedAgent.name : 'Agent Code'}
            </h2>
            <div className="flex gap-2">
              <button className="btn-secondary" disabled={!selectedAgent}>
                Accept
              </button>
              <button className="btn-secondary" disabled={!selectedAgent}>
                Edit
              </button>
              <button className="btn-secondary" disabled={!selectedAgent}>
                Regenerate
              </button>
              <button
                className="btn-danger"
                disabled={!selectedAgent || selectedAgent.is_builtin}
                onClick={() => selectedAgent && handleDeleteAgent(selectedAgent.id)}
              >
                Delete
              </button>
            </div>
          </div>

          {selectedAgent ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Provider:</span>
                  <span className="ml-2 font-medium">{selectedAgent.provider}</span>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Model:</span>
                  <span className="ml-2 font-medium">{selectedAgent.model_id}</span>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Created:</span>
                  <span className="ml-2 font-medium">
                    {new Date(selectedAgent.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Tools:</span>
                  <span className="ml-2 font-medium">
                    {selectedAgent.tools.length || 'None'}
                  </span>
                </div>
              </div>

              {selectedAgent.instructions && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    Instructions
                  </h3>
                  <p className="text-sm bg-gray-50 dark:bg-dark-700 p-3 rounded-lg">
                    {selectedAgent.instructions}
                  </p>
                </div>
              )}

              <div className="h-48 rounded-lg bg-gray-100 dark:bg-dark-700 flex items-center justify-center text-gray-500">
                Monaco Editor will be integrated here
              </div>
            </div>
          ) : (
            <div className="h-64 rounded-lg bg-gray-100 dark:bg-dark-700 flex items-center justify-center text-gray-500">
              Select an agent or create a new one
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
