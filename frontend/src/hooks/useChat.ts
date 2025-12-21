import { useState, useCallback, useRef } from "react";
import type { Message, ToolCall, AGUIEvent } from "../types/agui";

// Base URL for agent endpoints
// Backend mounts AGUI routers at /{agent_id}/agui
// Frontend proxy strips /api, so /api/{agent_id}/agui -> /{agent_id}/agui
const BACKEND_BASE_URL = "/api";

export function useChat(agentId: string = "general", sessionId?: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string): Promise<Message | undefined> => {
    if (!content.trim()) return undefined;

    // Add user message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: content.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    // Abort any previous request
    abortControllerRef.current?.abort();
    abortControllerRef.current = new AbortController();

    // Track the single assistant message for this response
    // All tool calls and text content accumulate into this one message
    const assistantMessageId = crypto.randomUUID();
    let assistantMessageCreated = false;
    let currentMessageContent = "";
    const toolCalls = new Map<string, ToolCall>();

    // Helper to ensure assistant message exists
    const ensureAssistantMessage = () => {
      if (!assistantMessageCreated) {
        assistantMessageCreated = true;
        setMessages((prev) => [
          ...prev,
          {
            id: assistantMessageId,
            role: "assistant",
            content: "",
            toolCalls: [],
          },
        ]);
      }
    };

    try {
      // Use agent-specific endpoint: /api/{agentId}/agui -> /{agentId}/agui after proxy
      const url = `${BACKEND_BASE_URL}/${agentId}/agui`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          thread_id: sessionId || "default",  // Use conversation ID for Agno session persistence
          run_id: crypto.randomUUID(),
          messages: [...messages, userMessage].map((m) => ({
            id: m.id,
            role: m.role,
            content: m.content,
          })),
          state: {},
          tools: [],
          context: [],
          forwarded_props: {},
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;

          // Parse SSE format: lines starting with "data: "
          if (line.startsWith("data: ")) {
            const data = line.slice(6); // Remove "data: " prefix
            try {
              const event = JSON.parse(data) as AGUIEvent;
              processEvent(event);
            } catch {
              // Skip invalid JSON
              console.debug("Skipping invalid JSON:", data);
            }
          }
        }
      }

      // Process any remaining buffer
      if (buffer.trim() && buffer.startsWith("data: ")) {
        const data = buffer.slice(6);
        try {
          const event = JSON.parse(data) as AGUIEvent;
          processEvent(event);
        } catch {
          // Skip invalid JSON
        }
      }
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        return userMessage; // Request was cancelled but still return user message
      }
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }

    return userMessage;

    function processEvent(event: AGUIEvent) {
      switch (event.type) {
        case "TEXT_MESSAGE_START":
          // Ensure message exists, don't create a new one
          ensureAssistantMessage();
          break;

        case "TEXT_MESSAGE_CONTENT":
          ensureAssistantMessage();
          currentMessageContent += event.delta;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMessageId
                ? { ...m, content: currentMessageContent }
                : m
            )
          );
          break;

        case "TEXT_MESSAGE_END":
          // Message content complete
          break;

        case "TOOL_CALL_START":
          ensureAssistantMessage();
          toolCalls.set(event.toolCallId, {
            id: event.toolCallId,
            name: event.toolCallName,
            args: "",
            status: "running",
          });
          updateToolCalls();
          break;

        case "TOOL_CALL_ARGS":
          const toolCall = toolCalls.get(event.toolCallId);
          if (toolCall) {
            toolCall.args += event.delta;
            updateToolCalls();
          }
          break;

        case "TOOL_CALL_END":
          const endedTool = toolCalls.get(event.toolCallId);
          if (endedTool) {
            endedTool.status = "pending";
            updateToolCalls();
          }
          break;

        case "TOOL_CALL_RESULT":
          const resultTool = toolCalls.get(event.toolCallId);
          if (resultTool) {
            resultTool.result = event.content;
            resultTool.status = "complete";
            updateToolCalls();
          }
          break;

        case "RUN_ERROR":
          setError(event.message);
          break;
      }
    }

    function updateToolCalls() {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessageId
            ? { ...m, toolCalls: Array.from(toolCalls.values()) }
            : m
        )
      );
    }
  }, [messages, agentId, sessionId]);

  const stopGeneration = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsLoading(false);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    setMessages,
    isLoading,
    error,
    sendMessage,
    stopGeneration,
    clearMessages,
  };
}
