import type { Message } from "../types/chat";
import { ToolCallPanel } from "./ToolCallPanel";

const msgRow: React.CSSProperties = {
  display: "flex",
  gap: "12px",
  marginBottom: "20px",
};

const avatar: React.CSSProperties = {
  width: "32px",
  height: "32px",
  borderRadius: "50%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontSize: "14px",
  flexShrink: 0,
  fontWeight: 600,
};

const bubble: React.CSSProperties = {
  maxWidth: "80%",
  lineHeight: 1.6,
};

const meta: React.CSSProperties = {
  fontSize: "11px",
  color: "#64748b",
  marginTop: "6px",
};

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div style={{ ...msgRow, flexDirection: isUser ? "row-reverse" : "row" }}>
      <div
        style={{
          ...avatar,
          background: isUser ? "#3b82f6" : "#10b981",
          color: "#fff",
        }}
      >
        {isUser ? "U" : "A"}
      </div>
      <div style={{ ...bubble, textAlign: isUser ? "right" : "left" }}>
        <div>{message.content}</div>
        {!isUser && message.steps.length > 0 && (
          <ToolCallPanel steps={message.steps} />
        )}
        {!isUser && message.latency_ms > 0 && (
          <div style={meta}>
            {message.tools_called.length} tools · {message.latency_ms}ms
          </div>
        )}
      </div>
    </div>
  );
}
