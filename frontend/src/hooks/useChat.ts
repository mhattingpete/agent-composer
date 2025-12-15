import { useState, useCallback, useRef } from "react";
import type { Message, ToolCall, AGUIEvent } from "../types/agui";

const BACKEND_URL = "/api/agui";

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

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

    // Track current assistant message and tool calls
    let currentMessageId: string | null = null;
    let currentMessageContent = "";
    const toolCalls = new Map<string, ToolCall>();

    try {
      const response = await fetch(BACKEND_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          thread_id: "default",
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
        return; // Request was cancelled
      }
      setError((err as Error).message);
    } finally {
      setIsLoading(false);
    }

    function processEvent(event: AGUIEvent) {
      switch (event.type) {
        case "TEXT_MESSAGE_START":
          // All streamed text messages are from assistant
          currentMessageId = event.messageId;
          currentMessageContent = "";
          setMessages((prev) => [
            ...prev,
            {
              id: event.messageId,
              role: "assistant",
              content: "",
              toolCalls: [],
            },
          ]);
          break;

        case "TEXT_MESSAGE_CONTENT":
          if (event.messageId === currentMessageId) {
            currentMessageContent += event.delta;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === currentMessageId
                  ? { ...m, content: currentMessageContent }
                  : m
              )
            );
          }
          break;

        case "TEXT_MESSAGE_END":
          // Message is complete
          break;

        case "ACTION_EXECUTION_START":
          toolCalls.set(event.actionExecutionId, {
            id: event.actionExecutionId,
            name: event.actionName,
            args: "",
            status: "running",
          });
          updateToolCalls();
          break;

        case "ACTION_EXECUTION_ARGS":
          const toolCall = toolCalls.get(event.actionExecutionId);
          if (toolCall) {
            toolCall.args += event.args;
            updateToolCalls();
          }
          break;

        case "ACTION_EXECUTION_END":
          const endedTool = toolCalls.get(event.actionExecutionId);
          if (endedTool) {
            endedTool.status = "pending";
            updateToolCalls();
          }
          break;

        case "ACTION_EXECUTION_RESULT":
          const resultTool = toolCalls.get(event.actionExecutionId);
          if (resultTool) {
            resultTool.result = event.result;
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
      if (!currentMessageId) return;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === currentMessageId
            ? { ...m, toolCalls: Array.from(toolCalls.values()) }
            : m
        )
      );
    }
  }, [messages]);

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
    isLoading,
    error,
    sendMessage,
    stopGeneration,
    clearMessages,
  };
}
