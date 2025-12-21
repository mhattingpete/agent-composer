import { useState, useRef, useEffect, useCallback } from "react";
import { useChat } from "./hooks/useChat";
import { MessageBubble } from "./components/MessageBubble";
import { Sidebar } from "./components/Sidebar";
import type { ConversationSummary, Message } from "./types/agui";

interface Agent {
  id: string;
  name: string;
  description: string;
  type?: "agent" | "team";  // Added to distinguish agents from teams
}

export default function App() {
  // Agent state
  const [selectedAgent, setSelectedAgent] = useState("general");
  const [agents, setAgents] = useState<Agent[]>([]);

  // Track saved message IDs to avoid re-saving loaded messages
  const savedMessageIds = useRef<Set<string>>(new Set());

  // Conversation state
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Chat hook - pass conversation ID for Agno session persistence
  const {
    messages,
    setMessages,
    isLoading,
    error,
    sendMessage: sendChatMessage,
    stopGeneration,
  } = useChat(selectedAgent, currentConversationId || undefined);

  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Fetch available agents and teams on mount
  useEffect(() => {
    const fetchAgentsAndTeams = async () => {
      try {
        // Fetch agents
        const agentsRes = await fetch("/api/agents");
        const agentsData = await agentsRes.json();
        const agents = agentsData.map((a: Agent) => ({ ...a, type: "agent" as const }));

        // Fetch teams - prefix ID with "team-" to match backend URL pattern
        const teamsRes = await fetch("/api/teams");
        const teamsData = await teamsRes.json();
        const teams = teamsData.map((t: Agent) => ({
          ...t,
          id: `team-${t.id}`,  // Backend expects /team-{id}/agui
          type: "team" as const,
        }));

        // Combine: agents first, then teams
        setAgents([...agents, ...teams]);
      } catch (err) {
        console.error("Failed to fetch agents/teams:", err);
      }
    };
    fetchAgentsAndTeams();
  }, []);

  // Fetch conversations on mount
  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const res = await fetch("/api/conversations");
      const data = await res.json();
      setConversations(data);
    } catch (err) {
      console.error("Failed to fetch conversations:", err);
    }
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount and when conversation changes
  useEffect(() => {
    inputRef.current?.focus();
  }, [currentConversationId]);

  // Create a new conversation
  const handleNewConversation = useCallback(async () => {
    try {
      const res = await fetch("/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: selectedAgent }),
      });
      const newConv = await res.json();
      setCurrentConversationId(newConv.id);
      setMessages([]);
      setSelectedAgent(newConv.agent_id);
      // Clear saved message tracking for new conversation
      savedMessageIds.current = new Set();
      await fetchConversations();
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  }, [selectedAgent, setMessages]);

  // Select an existing conversation
  const handleSelectConversation = useCallback(async (convId: string) => {
    try {
      const res = await fetch(`/api/conversations/${convId}`);
      const conv = await res.json();
      setCurrentConversationId(conv.id);
      setSelectedAgent(conv.agent_id);
      // Convert messages to the format useChat expects
      const loadedMessages: Message[] = conv.messages.map((m: { id: string; role: string; content: string; tool_calls?: { id: string; name: string; args: string; result?: string; status: string }[] }) => ({
        id: m.id,
        role: m.role as "user" | "assistant",
        content: m.content,
        toolCalls: m.tool_calls,
      }));
      // Mark all loaded messages as already saved to avoid re-saving
      savedMessageIds.current = new Set(loadedMessages.map(m => m.id));
      setMessages(loadedMessages);
    } catch (err) {
      console.error("Failed to load conversation:", err);
    }
  }, [setMessages]);

  // Delete a conversation
  const handleDeleteConversation = useCallback(async (convId: string) => {
    try {
      await fetch(`/api/conversations/${convId}`, { method: "DELETE" });
      if (currentConversationId === convId) {
        setCurrentConversationId(null);
        setMessages([]);
      }
      await fetchConversations();
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  }, [currentConversationId, setMessages]);

  // Save message to backend (skips if already saved)
  const saveMessage = useCallback(async (convId: string, message: Message) => {
    // Skip if this message was already saved
    if (savedMessageIds.current.has(message.id)) {
      return;
    }

    try {
      await fetch(`/api/conversations/${convId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: message.role,
          content: message.content,
          tool_calls: message.toolCalls || [],
          message_id: message.id,
        }),
      });
      // Mark as saved
      savedMessageIds.current.add(message.id);
      // Refresh conversation list to update message count and timestamp
      await fetchConversations();
    } catch (err) {
      console.error("Failed to save message:", err);
    }
  }, []);

  // Send message handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const messageContent = input;
    setInput("");

    // If no conversation, create one first
    let convId = currentConversationId;
    if (!convId) {
      try {
        const res = await fetch("/api/conversations", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ agent_id: selectedAgent }),
        });
        const newConv = await res.json();
        convId = newConv.id;
        setCurrentConversationId(newConv.id);
        await fetchConversations();
      } catch (err) {
        console.error("Failed to create conversation:", err);
        return;
      }
    }

    // Send message via chat hook
    const userMessage = await sendChatMessage(messageContent);

    // Save user message to backend
    if (userMessage && convId) {
      await saveMessage(convId, userMessage);
    }
  };

  // Handle assistant message completion
  useEffect(() => {
    // Save the last assistant message when it's complete (not loading)
    if (!isLoading && messages.length > 0 && currentConversationId) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === "assistant" && lastMessage.content) {
        saveMessage(currentConversationId, lastMessage);
      }
    }
  }, [isLoading, messages, currentConversationId, saveMessage]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Handle agent change - update conversation if one is active
  const handleAgentChange = async (newAgentId: string) => {
    setSelectedAgent(newAgentId);
    // Note: Chat history is preserved per user preference
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
          <h1 className="text-xl font-semibold text-gray-800">Agent Composer</h1>
          <div className="flex items-center gap-4">
            <select
              value={selectedAgent}
              onChange={(e) => handleAgentChange(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              title="Select agent"
            >
              {agents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}
                </option>
              ))}
            </select>
          </div>
        </header>

        {/* Messages area */}
        <main className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">
                  Start a conversation with{" "}
                  {agents.find((a) => a.id === selectedAgent)?.name || "the agent"}
                </p>
                <p className="text-gray-400 text-sm mt-2">
                  {agents.find((a) => a.id === selectedAgent)?.description ||
                    "Select an agent to begin"}
                </p>
              </div>
            )}

            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}

            {isLoading &&
              messages.length > 0 &&
              !messages[messages.length - 1]?.content && (
                <div className="flex items-center gap-2 text-gray-500">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                </div>
              )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Input area */}
        <footer className="bg-white border-t border-gray-200 px-4 py-4">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex gap-3 items-end">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a message..."
                  rows={1}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  style={{
                    minHeight: "48px",
                    maxHeight: "200px",
                  }}
                  disabled={isLoading}
                />
              </div>
              {isLoading ? (
                <button
                  type="button"
                  onClick={stopGeneration}
                  className="px-5 py-3 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors font-medium"
                >
                  Stop
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="px-5 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              )}
            </div>
          </form>
        </footer>
      </div>
    </div>
  );
}
