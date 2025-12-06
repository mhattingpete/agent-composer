import { useState, useRef, useEffect } from 'react'
import { useAgents } from '../../hooks/useAgents'
import type { AgentResponse } from '../../services/api'

interface AgentSelectorProps {
  selectedAgentId: string | null
  onSelectAgent: (agent: AgentResponse | null) => void
}

export default function AgentSelector({ selectedAgentId, onSelectAgent }: AgentSelectorProps) {
  const { data: agents, isLoading, error } = useAgents()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const selectedAgent = agents?.find(a => a.id === selectedAgentId)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (agent: AgentResponse | null) => {
    onSelectAgent(agent)
    setIsOpen(false)
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-dark-700 rounded-lg">
        <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-gray-500">Loading agents...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-3 py-2 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
        Failed to load agents
      </div>
    )
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 rounded-lg transition-colors min-w-[200px]"
      >
        {selectedAgent ? (
          <>
            <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-sm font-medium">
              {selectedAgent.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 text-left">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {selectedAgent.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[150px]">
                {selectedAgent.provider} - {selectedAgent.model_id}
              </p>
            </div>
          </>
        ) : (
          <span className="text-sm text-gray-500 dark:text-gray-400">Select an agent...</span>
        )}
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-full min-w-[280px] bg-white dark:bg-dark-800 rounded-lg shadow-lg border border-gray-200 dark:border-dark-700 z-50 max-h-[300px] overflow-y-auto">
          {agents && agents.length === 0 ? (
            <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
              No agents available. Create one in Agent Studio.
            </div>
          ) : (
            <>
              {selectedAgent && (
                <button
                  onClick={() => handleSelect(null)}
                  className="w-full px-4 py-2 text-left text-sm text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-700 border-b border-gray-200 dark:border-dark-700"
                >
                  Clear selection
                </button>
              )}
              {agents?.map((agent) => (
                <button
                  key={agent.id}
                  onClick={() => handleSelect(agent)}
                  className={`w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-100 dark:hover:bg-dark-700 transition-colors ${
                    agent.id === selectedAgentId ? 'bg-primary-50 dark:bg-primary-900/20' : ''
                  }`}
                >
                  <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                    {agent.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 text-left overflow-hidden">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                        {agent.name}
                      </p>
                      {agent.is_builtin && (
                        <span className="text-xs px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                          Built-in
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {agent.description || `${agent.provider} - ${agent.model_id}`}
                    </p>
                  </div>
                  {agent.id === selectedAgentId && (
                    <svg className="w-5 h-5 text-primary-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  )
}
