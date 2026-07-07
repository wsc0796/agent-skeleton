export interface AgentStep {
  iteration: number;
  thought?: string;
  tool_name?: string | null;
  tool_args?: Record<string, unknown> | null;
  tool_result?: string | null;
  is_final?: boolean;
}

export interface ChatResponse {
  agent_name: string;
  answer: string;
  steps: AgentStep[];
  iterations: number;
  tools_called: string[];
  total_latency_ms: number;
}

export interface Message {
  id: string;
  role: "user" | "agent";
  content: string;
  steps: AgentStep[];
  tools_called: string[];
  latency_ms: number;
}

export interface SSEEvent {
  event: string;
  data: string;
}
