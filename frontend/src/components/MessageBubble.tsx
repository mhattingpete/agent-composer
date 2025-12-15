import ReactMarkdown from "react-markdown";
import type { Message } from "../types/agui";
import { ToolCallCard } from "./ToolCallCard";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const hasContent = message.content?.trim();
  const hasToolCalls = message.toolCalls && message.toolCalls.length > 0;

  // Don't render empty bubbles
  if (!hasContent && !hasToolCalls) {
    return null;
  }

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] ${
          isUser
            ? "bg-blue-500 text-white rounded-2xl rounded-br-md px-4 py-3"
            : "bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm"
        }`}
      >
        {/* Tool calls (shown before content for assistant) */}
        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <div className="space-y-2 mb-3">
            {message.toolCalls.map((toolCall) => (
              <ToolCallCard key={toolCall.id} toolCall={toolCall} />
            ))}
          </div>
        )}

        {/* Message content */}
        {message.content && (
          <div
            className={`prose prose-sm max-w-none ${
              isUser ? "prose-invert" : "prose-gray"
            }`}
          >
            <ReactMarkdown
              components={{
                // Style code blocks
                pre: ({ children }) => (
                  <pre className={`${isUser ? "bg-blue-600" : "bg-gray-100"} rounded-lg p-3 overflow-x-auto`}>
                    {children}
                  </pre>
                ),
                code: ({ children, className }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className={`${isUser ? "bg-blue-600" : "bg-gray-100"} px-1 py-0.5 rounded text-sm`}>
                      {children}
                    </code>
                  ) : (
                    <code className="text-sm">{children}</code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
