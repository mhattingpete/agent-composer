import { useState } from "react";
import type { ToolCall } from "../types/agui";

interface ToolCallCardProps {
  toolCall: ToolCall;
}

export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const statusColors = {
    pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
    running: "bg-blue-100 text-blue-800 border-blue-200",
    complete: "bg-green-100 text-green-800 border-green-200",
    error: "bg-red-100 text-red-800 border-red-200",
  };

  const statusIcons = {
    pending: "⏳",
    running: "⚙️",
    complete: "✓",
    error: "✗",
  };

  // Try to parse and format args
  let formattedArgs = toolCall.args;
  try {
    const parsed = JSON.parse(toolCall.args);
    formattedArgs = JSON.stringify(parsed, null, 2);
  } catch {
    // Keep original if not valid JSON
  }

  // Try to parse and format result
  let formattedResult = toolCall.result;
  if (toolCall.result) {
    try {
      const parsed = JSON.parse(toolCall.result);
      formattedResult = JSON.stringify(parsed, null, 2);
    } catch {
      // Keep original if not valid JSON
    }
  }

  return (
    <div
      className={`border rounded-lg overflow-hidden ${statusColors[toolCall.status]}`}
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium hover:opacity-80 transition-opacity"
      >
        <div className="flex items-center gap-2">
          <span>{statusIcons[toolCall.status]}</span>
          <span className="font-mono">{toolCall.name}</span>
        </div>
        <span className="text-xs opacity-70">
          {isExpanded ? "▼" : "▶"}
        </span>
      </button>

      {isExpanded && (
        <div className="border-t border-current/20 bg-white/50">
          {/* Arguments */}
          <div className="px-3 py-2">
            <div className="text-xs font-medium text-gray-500 mb-1">Arguments</div>
            <pre className="text-xs bg-white/80 rounded p-2 overflow-x-auto whitespace-pre-wrap">
              {formattedArgs || "(none)"}
            </pre>
          </div>

          {/* Result */}
          {toolCall.result && (
            <div className="px-3 py-2 border-t border-current/10">
              <div className="text-xs font-medium text-gray-500 mb-1">Result</div>
              <pre className="text-xs bg-white/80 rounded p-2 overflow-x-auto whitespace-pre-wrap max-h-48 overflow-y-auto">
                {formattedResult}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
