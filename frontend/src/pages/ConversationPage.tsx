import { useState, useEffect, useCallback } from 'react'
import ChatMessageList from '../components/chat/ChatMessageList'
import ChatInput from '../components/chat/ChatInput'
import AgentSelector from '../components/chat/AgentSelector'
import ConversationList from '../components/chat/ConversationList'
import { useChat } from '../hooks/useChat'
import { useConversations } from '../hooks/useConversations'
import type { AgentResponse } from '../services/api'
import type { Message } from '../components/chat/MessageBubble'

export default function ConversationPage() {
  const [selectedAgent, setSelectedAgent] = useState<AgentResponse | null>(null)
  const [showSidebar, setShowSidebar] = useState(true)

  const {
    conversations,
    currentConversation,
    createConversation,
    selectConversation,
    deleteConversation,
    updateConversation,
    selectedConversationId,
  } = useConversations()

  // Initialize messages from current conversation
  const [localMessages, setLocalMessages] = useState<Message[]>([])

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversation) {
      setLocalMessages(currentConversation.messages.map(m => ({
        ...m,
        timestamp: m.timestamp ? new Date(m.timestamp) : undefined,
      })))
      // Also restore the selected agent if stored
      if (currentConversation.agentId && !selectedAgent) {
        // Agent will be re-selected via the selector
      }
    } else {
      setLocalMessages([])
    }
  }, [currentConversation?.id])

  const { isLoading, error, sendMessage: sendToAgent } = useChat({
    agentId: selectedAgent?.id || null,
    onError: (err) => console.error('Chat error:', err),
  })

  const handleSendMessage = useCallback(async (content: string) => {
    if (!selectedAgent) return

    // Create a new conversation if needed
    let conversationId = selectedConversationId
    if (!conversationId) {
      conversationId = createConversation(selectedAgent.id, selectedAgent.name)
    }

    // Add user message immediately
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    }

    const updatedMessages = [...localMessages, userMessage]
    setLocalMessages(updatedMessages)
    updateConversation(conversationId, updatedMessages)

    // Send to agent and get response
    try {
      // The sendToAgent function handles the streaming internally
      // We need to manually track the response here
      await sendToAgent(content)

      // After successful send, we need to get the updated messages
      // For now, we'll add a placeholder that gets updated by the streaming
    } catch (err) {
      console.error('Failed to send message:', err)
    }
  }, [selectedAgent, selectedConversationId, localMessages, createConversation, updateConversation, sendToAgent])

  const handleNewConversation = useCallback(() => {
    createConversation(selectedAgent?.id || null, selectedAgent?.name)
    setLocalMessages([])
  }, [selectedAgent, createConversation])

  const handleSelectAgent = useCallback((agent: AgentResponse | null) => {
    setSelectedAgent(agent)
  }, [])

  const handleDeleteConversation = useCallback((id: string) => {
    if (confirm('Are you sure you want to delete this conversation?')) {
      deleteConversation(id)
    }
  }, [deleteConversation])

  return (
    <div className="flex h-full">
      {/* Conversation History Sidebar */}
      {showSidebar && (
        <div className="w-72 border-r border-gray-200 dark:border-dark-700 flex-shrink-0">
          <ConversationList
            conversations={conversations}
            selectedId={selectedConversationId}
            onSelectConversation={selectConversation}
            onDeleteConversation={handleDeleteConversation}
            onNewConversation={handleNewConversation}
          />
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat Header */}
        <div className="border-b border-gray-200 dark:border-dark-700 px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-dark-700 rounded-lg transition-colors"
            title={showSidebar ? 'Hide sidebar' : 'Show sidebar'}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <AgentSelector
            selectedAgentId={selectedAgent?.id || null}
            onSelectAgent={handleSelectAgent}
          />

          {selectedAgent && (
            <div className="ml-auto flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <span>Connected</span>
            </div>
          )}
        </div>

        {/* Error Banner */}
        {error && (
          <div className="px-4 py-2 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
            {error.message}
          </div>
        )}

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto">
          <ChatMessageList messages={localMessages} isLoading={isLoading} />
        </div>

        {/* Chat Input */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={!selectedAgent || isLoading}
          placeholder={
            selectedAgent
              ? `Message ${selectedAgent.name}...`
              : 'Select an agent to start chatting'
          }
        />
      </div>
    </div>
  )
}
