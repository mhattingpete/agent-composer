import { useState } from "react";
import type { ToolCall } from "../types/agui";

interface ToolCallsSectionProps {
  toolCalls: ToolCall[];
}

export function ToolCallsSection({ toolCalls }: ToolCallsSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedToolId, setExpandedToolId] = useState<string | null>(null);

  const completedCount = toolCalls.filter((t) => t.status === "complete").length;
  const runningCount = toolCalls.filter((t) => t.status === "running").length;
  const isAllComplete = completedCount === toolCalls.length;

  // Format tool arguments for display
  const formatArgs = (args: string): string => {
    try {
      const parsed = JSON.parse(args);
      // For code, show a truncated preview
      if (parsed.code) {
        const lines = parsed.code.split("\n");
        return lines.length > 3
          ? lines.slice(0, 3).join("\n") + "\n..."
          : parsed.code;
      }
      return JSON.stringify(parsed, null, 2);
    } catch {
      return args;
    }
  };

  // Get a summary description for a tool call
  const getToolSummary = (toolCall: ToolCall): string => {
    try {
      const parsed = JSON.parse(toolCall.args);
      if (parsed.code) {
        // Extract first meaningful line of code
        const lines = parsed.code.split("\n").filter((l: string) => l.trim() && !l.trim().startsWith("#"));
        if (lines.length > 0) {
          const firstLine = lines[0].trim();
          return firstLine.length > 50 ? firstLine.slice(0, 50) + "..." : firstLine;
        }
      }
      if (parsed.query) return `Search: ${parsed.query}`;
      if (parsed.url) return `Fetch: ${parsed.url}`;
      if (parsed.package) return `Install: ${parsed.package}`;
    } catch {
      // ignore
    }
    return toolCall.name;
  };

  const statusIcon = (status: ToolCall["status"]) => {
    switch (status) {
      case "complete":
        return (
          <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case "running":
        return (
          <svg className="w-4 h-4 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        );
      case "pending":
        return <div className="w-2 h-2 bg-gray-400 rounded-full" />;
      case "error":
        return (
          <svg className="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
    }
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden mb-3">
      {/* Header - Toggle */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 transition-colors"
      >
        <svg
          className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-0" : "-rotate-90"}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
        <span className="font-medium">
          {isExpanded ? "Hide steps" : "Show steps"}
        </span>
        <span className="text-gray-400">
          {runningCount > 0
            ? `${runningCount} running...`
            : isAllComplete
            ? `${completedCount} completed`
            : `${completedCount}/${toolCalls.length}`}
        </span>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="border-t border-gray-200">
          {toolCalls.map((toolCall) => (
            <div key={toolCall.id} className="border-b border-gray-100 last:border-b-0">
              {/* Tool call row */}
              <button
                onClick={() =>
                  setExpandedToolId(expandedToolId === toolCall.id ? null : toolCall.id)
                }
                className="w-full flex items-center gap-3 px-3 py-2 text-sm hover:bg-gray-100 transition-colors"
              >
                <div className="flex-shrink-0">{statusIcon(toolCall.status)}</div>
                <span className="flex-1 text-left text-gray-700 truncate">
                  {getToolSummary(toolCall)}
                </span>
                {toolCall.result && (
                  <svg
                    className={`w-4 h-4 text-gray-400 transition-transform ${
                      expandedToolId === toolCall.id ? "rotate-180" : ""
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                )}
              </button>

              {/* Tool call details */}
              {expandedToolId === toolCall.id && (
                <div className="px-3 pb-3 bg-white">
                  {/* Arguments */}
                  <div className="mb-2">
                    <div className="text-xs font-medium text-gray-500 mb-1">Code</div>
                    <pre className="text-xs bg-gray-50 border border-gray-200 rounded p-2 overflow-x-auto whitespace-pre-wrap max-h-32 overflow-y-auto">
                      {formatArgs(toolCall.args)}
                    </pre>
                  </div>

                  {/* Result */}
                  {toolCall.result && (
                    <div>
                      <div className="text-xs font-medium text-gray-500 mb-1">Result</div>
                      <pre className="text-xs bg-gray-50 border border-gray-200 rounded p-2 overflow-x-auto whitespace-pre-wrap max-h-48 overflow-y-auto">
                        {toolCall.result.length > 1000
                          ? toolCall.result.slice(0, 1000) + "\n...(truncated)"
                          : toolCall.result}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
