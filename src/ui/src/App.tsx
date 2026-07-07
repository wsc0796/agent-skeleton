import { useAgentChat } from "./hooks/useAgentChat";
import { ChatMessage } from "./components/ChatMessage";
import { ChatInput } from "./components/ChatInput";

const container: React.CSSProperties = {
  maxWidth: "800px",
  margin: "0 auto",
  height: "100vh",
  display: "flex",
  flexDirection: "column",
};

const header: React.CSSProperties = {
  padding: "14px 20px",
  background: "#1e293b",
  borderBottom: "1px solid #334155",
  textAlign: "center",
};

const title: React.CSSProperties = {
  fontSize: "16px",
  fontWeight: 700,
  color: "#f8fafc",
};

const subtitle: React.CSSProperties = {
  fontSize: "12px",
  color: "#64748b",
  marginTop: "2px",
};

const chatArea: React.CSSProperties = {
  flex: 1,
  overflowY: "auto",
  padding: "20px",
};

const emptyState: React.CSSProperties = {
  textAlign: "center",
  color: "#475569",
  marginTop: "100px",
  fontSize: "14px",
  lineHeight: 2,
};

const exampleChip: React.CSSProperties = {
  display: "inline-block",
  background: "#1e293b",
  border: "1px solid #334155",
  borderRadius: "6px",
  padding: "6px 12px",
  margin: "4px",
  fontSize: "13px",
  color: "#94a3b8",
  cursor: "pointer",
};

const EXAMPLES = [
  "Analyze: AI Agent intern, requires Python, LLM, RAG, FastAPI",
  "Match my skills: Python, FastAPI, Docker, Git, LLM, RAG, Agent",
  "Generate a study plan for missing skills: React, TypeScript, Kubernetes",
];

export function App() {
  const { messages, streaming, send } = useAgentChat();

  return (
    <div style={container}>
      <div style={header}>
        <div style={title}>Agent Skeleton — Job Matcher</div>
        <div style={subtitle}>
          Paste a job description, get skill analysis and study plan
        </div>
      </div>

      <div style={chatArea}>
        {messages.length === 0 && (
          <div style={emptyState}>
            <div style={{ marginBottom: "16px" }}>
              👋 Try one of these:
            </div>
            {EXAMPLES.map((ex, i) => (
              <div
                key={i}
                style={exampleChip}
                onClick={() => !streaming && send(ex)}
              >
                {ex}
              </div>
            ))}
            <div style={{ marginTop: "24px", fontSize: "12px" }}>
              The agent uses analyze_jd → match_resume → generate_gap_report → generate_study_plan
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {streaming && (
          <div style={{ textAlign: "center", color: "#64748b", padding: "12px" }}>
            Agent is thinking...
          </div>
        )}
      </div>

      <ChatInput onSend={send} disabled={streaming} />
    </div>
  );
}
