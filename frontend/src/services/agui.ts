import { config } from '../config'

export interface AGUIMessage {
  role: 'user' | 'assistant'
  content: string
  id?: string
}

export interface AGUIEvent {
  type: string
  message?: string
  text_delta?: string
  run_id?: string
  error?: string
}

export interface RunAgentInput {
  threadId: string
  runId: string
  state: Record<string, unknown>
  messages: Array<{
    id: string
    role: string
    content: string
  }>
  tools: unknown[]
  context: unknown[]
  forwardedProps: Record<string, unknown>
}

export class AGUIClient {
  private baseUrl: string

  constructor(baseUrl: string = config.apiBaseUrl) {
    this.baseUrl = baseUrl
  }

  async *streamChat(
    agentId: string,
    messages: AGUIMessage[]
  ): AsyncGenerator<AGUIEvent, void, unknown> {
    const threadId = `thread-${Date.now()}`
    const runId = `run-${Date.now()}`

    const input: RunAgentInput = {
      threadId,
      runId,
      state: {},
      messages: messages.map((m, idx) => ({
        id: m.id || `msg-${idx}-${Date.now()}`,
        role: m.role,
        content: m.content,
      })),
      tools: [],
      context: [],
      forwardedProps: {
        agent_id: agentId,
      },
    }

    const response = await fetch(`${this.baseUrl}/api/agui`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(input),
    })

    if (!response.ok) {
      throw new Error(`AG-UI request failed: ${response.status} ${response.statusText}`)
    }

    if (!response.body) {
      throw new Error('No response body received')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (data && data !== '[DONE]') {
              try {
                const event: AGUIEvent = JSON.parse(data)
                yield event
              } catch (e) {
                console.warn('Failed to parse AG-UI event:', data, e)
              }
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }
}

export const aguiClient = new AGUIClient()
