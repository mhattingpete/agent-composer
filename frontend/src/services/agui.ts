import { config } from '../config'

export interface AGUIMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AGUIEvent {
  type: string
  message?: string
  text_delta?: string
  run_id?: string
  error?: string
}

export interface RunAgentInput {
  messages: Array<{
    role: string
    content: string
  }>
  forwarded_props?: Record<string, unknown>
  state?: Record<string, unknown>
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
    const input: RunAgentInput = {
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
      })),
      forwarded_props: {
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
