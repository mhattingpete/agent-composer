import { useState, useCallback, useRef } from 'react'
import { aguiClient, type AGUIMessage } from '../services/agui'
import type { Message } from '../components/chat/MessageBubble'

interface UseChatOptions {
  agentId: string | null
  onError?: (error: Error) => void
}

interface UseChatReturn {
  messages: Message[]
  isLoading: boolean
  error: Error | null
  sendMessage: (content: string) => Promise<void>
  clearMessages: () => void
}

export function useChat({ agentId, onError }: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const sendMessage = useCallback(async (content: string) => {
    if (!agentId) {
      const err = new Error('No agent selected')
      setError(err)
      onError?.(err)
      return
    }

    // Cancel any ongoing request
    abortControllerRef.current?.abort()
    abortControllerRef.current = new AbortController()

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      // Build message history for the API
      const messageHistory: AGUIMessage[] = [
        ...messages.map(m => ({ role: m.role, content: m.content })),
        { role: 'user' as const, content },
      ]

      // Create placeholder for assistant response
      const assistantMessageId = `assistant-${Date.now()}`
      let assistantContent = ''

      setMessages(prev => [
        ...prev,
        {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
        },
      ])

      // Stream the response
      for await (const event of aguiClient.streamChat(agentId, messageHistory)) {
        if (event.type === 'RUN_ERROR') {
          throw new Error(event.message || 'Agent error occurred')
        }

        if (event.type === 'TEXT_MESSAGE_DELTA' && event.text_delta) {
          assistantContent += event.text_delta
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantMessageId
                ? { ...m, content: assistantContent }
                : m
            )
          )
        }

        if (event.type === 'TEXT_MESSAGE_CONTENT' && event.message) {
          assistantContent = event.message
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantMessageId
                ? { ...m, content: assistantContent }
                : m
            )
          )
        }
      }

      // If no content was received, show a fallback
      if (!assistantContent) {
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMessageId
              ? { ...m, content: 'No response received from agent.' }
              : m
          )
        )
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      onError?.(error)

      // Remove the empty assistant message on error
      setMessages(prev => prev.filter(m => m.content !== ''))
    } finally {
      setIsLoading(false)
    }
  }, [agentId, messages, onError])

  const clearMessages = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
  }
}
