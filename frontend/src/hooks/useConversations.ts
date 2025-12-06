import { useState, useCallback, useEffect } from 'react'
import type { Conversation } from '../components/chat/ConversationItem'
import type { Message } from '../components/chat/MessageBubble'

const STORAGE_KEY = 'agent_composer_conversations'

interface StoredConversation extends Omit<Conversation, 'updatedAt'> {
  updatedAt: string
  messages: Message[]
}

interface UseConversationsReturn {
  conversations: Conversation[]
  currentConversation: StoredConversation | null
  createConversation: (agentId: string | null, agentName?: string) => string
  selectConversation: (id: string) => void
  deleteConversation: (id: string) => void
  updateConversation: (id: string, messages: Message[], title?: string) => void
  selectedConversationId: string | null
}

export function useConversations(): UseConversationsReturn {
  const [conversations, setConversations] = useState<StoredConversation[]>([])
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)

  // Load conversations from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored) as StoredConversation[]
        setConversations(parsed)
        // Select the most recent conversation if any
        if (parsed.length > 0 && !selectedConversationId) {
          setSelectedConversationId(parsed[0].id)
        }
      }
    } catch (e) {
      console.error('Failed to load conversations:', e)
    }
  }, [])

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations))
    } catch (e) {
      console.error('Failed to save conversations:', e)
    }
  }, [conversations])

  const createConversation = useCallback((agentId: string | null, agentName?: string): string => {
    const id = `conv-${Date.now()}`
    const newConversation: StoredConversation = {
      id,
      title: 'New Conversation',
      agentId,
      agentName,
      lastMessage: undefined,
      updatedAt: new Date().toISOString(),
      messageCount: 0,
      messages: [],
    }

    setConversations(prev => [newConversation, ...prev])
    setSelectedConversationId(id)
    return id
  }, [])

  const selectConversation = useCallback((id: string) => {
    setSelectedConversationId(id)
  }, [])

  const deleteConversation = useCallback((id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id))
    if (selectedConversationId === id) {
      setSelectedConversationId(null)
    }
  }, [selectedConversationId])

  const updateConversation = useCallback((id: string, messages: Message[], title?: string) => {
    setConversations(prev =>
      prev.map(c => {
        if (c.id !== id) return c

        // Auto-generate title from first user message if not provided
        const autoTitle = title || (messages.length > 0
          ? messages.find(m => m.role === 'user')?.content.slice(0, 50) + (messages[0]?.content?.length > 50 ? '...' : '')
          : c.title) || 'New Conversation'

        const lastUserMessage = [...messages].reverse().find(m => m.role === 'user')

        return {
          ...c,
          title: autoTitle,
          lastMessage: lastUserMessage?.content,
          updatedAt: new Date().toISOString(),
          messageCount: messages.length,
          messages,
        }
      })
    )
  }, [])

  const currentConversation = conversations.find(c => c.id === selectedConversationId) || null

  // Transform to Conversation type (convert date strings back to Date objects)
  const conversationsWithDates: Conversation[] = conversations.map(c => ({
    ...c,
    updatedAt: new Date(c.updatedAt),
  }))

  return {
    conversations: conversationsWithDates,
    currentConversation,
    createConversation,
    selectConversation,
    deleteConversation,
    updateConversation,
    selectedConversationId,
  }
}
