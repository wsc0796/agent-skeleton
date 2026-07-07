import { useState, useCallback, useRef } from "react";
import type { Message, AgentStep } from "../types/chat";

const API_BASE = "/api/v1";

export function useAgentChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [currentSteps, setCurrentSteps] = useState<AgentStep[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(async (text: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      steps: [],
      tools_called: [],
      latency_ms: 0,
    };

    setMessages((prev) => [...prev, userMsg]);
    setStreaming(true);
    setCurrentSteps([]);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, agent_name: "job_matcher" }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        const detail = err.detail || err;
        const agentMsg: Message = {
          id: crypto.randomUUID(),
          role: "agent",
          content: detail.message || detail.code || `Error: ${response.status}`,
          steps: [],
          tools_called: [],
          latency_ms: 0,
        };
        setMessages((prev) => [...prev, agentMsg]);
        setStreaming(false);
        return;
      }

      const data = await response.json();

      const agentMsg: Message = {
        id: crypto.randomUUID(),
        role: "agent",
        content: data.answer,
        steps: data.steps || [],
        tools_called: data.tools_called || [],
        latency_ms: data.total_latency_ms || 0,
      };

      setMessages((prev) => [...prev, agentMsg]);
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") return;
      const agentMsg: Message = {
        id: crypto.randomUUID(),
        role: "agent",
        content: `Network error: ${err instanceof Error ? err.message : "unknown"}`,
        steps: [],
        tools_called: [],
        latency_ms: 0,
      };
      setMessages((prev) => [...prev, agentMsg]);
    } finally {
      setStreaming(false);
      setCurrentSteps([]);
      abortRef.current = null;
    }
  }, []);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { messages, streaming, currentSteps, send, cancel };
}
