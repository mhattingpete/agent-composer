// AG-UI Protocol Event Types (SSE format from Agno AGUI interface)

export type EventType =
  | "RUN_STARTED"
  | "RUN_FINISHED"
  | "RUN_ERROR"
  | "TEXT_MESSAGE_START"
  | "TEXT_MESSAGE_CONTENT"
  | "TEXT_MESSAGE_END"
  | "ACTION_EXECUTION_START"
  | "ACTION_EXECUTION_ARGS"
  | "ACTION_EXECUTION_END"
  | "ACTION_EXECUTION_RESULT";

export interface BaseEvent {
  type: EventType;
}

export interface RunStartedEvent extends BaseEvent {
  type: "RUN_STARTED";
  threadId: string;
  runId: string;
}

export interface RunFinishedEvent extends BaseEvent {
  type: "RUN_FINISHED";
  threadId: string;
  runId: string;
}

export interface RunErrorEvent extends BaseEvent {
  type: "RUN_ERROR";
  message: string;
  code?: string;
}

export interface TextMessageStartEvent extends BaseEvent {
  type: "TEXT_MESSAGE_START";
  messageId: string;
  role: "assistant" | "user";
}

export interface TextMessageContentEvent extends BaseEvent {
  type: "TEXT_MESSAGE_CONTENT";
  messageId: string;
  delta: string;
}

export interface TextMessageEndEvent extends BaseEvent {
  type: "TEXT_MESSAGE_END";
  messageId: string;
}

export interface ActionExecutionStartEvent extends BaseEvent {
  type: "ACTION_EXECUTION_START";
  actionExecutionId: string;
  actionName: string;
  parentMessageId?: string;
}

export interface ActionExecutionArgsEvent extends BaseEvent {
  type: "ACTION_EXECUTION_ARGS";
  actionExecutionId: string;
  args: string;
}

export interface ActionExecutionEndEvent extends BaseEvent {
  type: "ACTION_EXECUTION_END";
  actionExecutionId: string;
}

export interface ActionExecutionResultEvent extends BaseEvent {
  type: "ACTION_EXECUTION_RESULT";
  actionExecutionId: string;
  actionName: string;
  result: string;
}

export type AGUIEvent =
  | RunStartedEvent
  | RunFinishedEvent
  | RunErrorEvent
  | TextMessageStartEvent
  | TextMessageContentEvent
  | TextMessageEndEvent
  | ActionExecutionStartEvent
  | ActionExecutionArgsEvent
  | ActionExecutionEndEvent
  | ActionExecutionResultEvent;

// Message types for the UI
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  id: string;
  name: string;
  args: string;
  result?: string;
  status: "pending" | "running" | "complete" | "error";
}
