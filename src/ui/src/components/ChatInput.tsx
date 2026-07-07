import { useState, type KeyboardEvent } from "react";

const wrapper: React.CSSProperties = {
  display: "flex",
  gap: "8px",
  padding: "16px",
  background: "#1e293b",
  borderTop: "1px solid #334155",
};

const input: React.CSSProperties = {
  flex: 1,
  padding: "10px 14px",
  borderRadius: "8px",
  border: "1px solid #475569",
  background: "#0f172a",
  color: "#e2e8f0",
  fontSize: "14px",
  outline: "none",
};

const btn: React.CSSProperties = {
  padding: "10px 20px",
  borderRadius: "8px",
  border: "none",
  background: "#3b82f6",
  color: "#fff",
  fontWeight: 600,
  fontSize: "14px",
  cursor: "pointer",
};

const btnDisabled: React.CSSProperties = {
  ...btn,
  opacity: 0.5,
  cursor: "not-allowed",
};

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  };

  const handleKey = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={wrapper}>
      <input
        style={input}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKey}
        placeholder="Paste a job description or ask a question..."
        disabled={disabled}
      />
      <button style={disabled ? btnDisabled : btn} onClick={handleSend} disabled={disabled}>
        {disabled ? "..." : "Send"}
      </button>
    </div>
  );
}
