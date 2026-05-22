export type AgentRole = "planner" | "researcher" | "synthesizer" | "critic";

export type ToolName =
  | "web_search"
  | "web_fetch"
  | "wikipedia"
  | "arxiv"
  | "pdf_read"
  | "python_exec"
  | "calculator"
  | "vector_search"
  | "vector_write"
  | "summarize"
  | "translate"
  | "datetime";

export interface ToolCall {
  id: string;
  tool: ToolName;
  input: Record<string, unknown>;
  output?: unknown;
  durationMs?: number;
  error?: string;
}

export interface AgentStep {
  id: string;
  role: AgentRole;
  thought: string;
  toolCalls: ToolCall[];
  startedAt: string;
  endedAt?: string;
  tokensIn?: number;
  tokensOut?: number;
}

export interface ResearchSession {
  id: string;
  userId: string;
  query: string;
  answer?: string;
  score?: number;
  steps: AgentStep[];
  createdAt: string;
  updatedAt: string;
}

export interface SessionSummary {
  id: string;
  query: string;
  score?: number;
  createdAt: string;
}

export interface User {
  id: string;
  email: string;
  createdAt: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export type SSEEvent =
  | { type: "agent_step"; step: AgentStep }
  | { type: "tool_call"; stepId: string; call: ToolCall }
  | { type: "token"; text: string }
  | { type: "done"; sessionId: string; answer: string; score: number }
  | { type: "error"; message: string };
