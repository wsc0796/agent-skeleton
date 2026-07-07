import { useState } from "react";
import type { AgentStep } from "../types/chat";

const panel: React.CSSProperties = {
  background: "#1e293b",
  border: "1px solid #334155",
  borderRadius: "8px",
  margin: "8px 0",
  overflow: "hidden",
  fontSize: "13px",
};

const header: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "8px 12px",
  cursor: "pointer",
  background: "#334155",
  borderBottom: "1px solid #475569",
};

const body: React.CSSProperties = {
  padding: "10px 12px",
  maxHeight: "200px",
  overflowY: "auto",
};

const codeBlock: React.CSSProperties = {
  background: "#0f172a",
  color: "#94e2d5",
  padding: "8px",
  borderRadius: "4px",
  fontFamily: "monospace",
  fontSize: "12px",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  maxHeight: "120px",
  overflowY: "auto",
};

interface ToolCallPanelProps {
  steps: AgentStep[];
}

export function ToolCallPanel({ steps }: ToolCallPanelProps) {
  const [open, setOpen] = useState(true);

  const toolSteps = steps.filter((s) => s.tool_name);
  if (toolSteps.length === 0) return null;

  return (
    <div style={panel}>
      <div style={header} onClick={() => setOpen(!open)}>
        <span>
          🔧 {toolSteps.length} tool call{toolSteps.length > 1 ? "s" : ""}
          {" — "}
          {toolSteps.map((s) => s.tool_name).join(", ")}
        </span>
        <span style={{ color: "#94a3b8" }}>{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div style={body}>
          {toolSteps.map((step, i) => (
            <div key={i} style={{ marginBottom: 10 }}>
              <div style={{ color: "#facc15", fontWeight: 600, marginBottom: 4 }}>
                Step {step.iteration}: {step.tool_name}
              </div>
              {step.tool_args && (
                <div style={codeBlock}>
                  {JSON.stringify(step.tool_args, null, 2)}
                </div>
              )}
              {step.tool_result && (
                <div style={{ ...codeBlock, color: "#a5d6ff", marginTop: 4 }}>
                  {step.tool_result.length > 300
                    ? step.tool_result.slice(0, 300) + "..."
                    : step.tool_result}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
