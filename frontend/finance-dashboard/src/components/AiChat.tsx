import { useState, useEffect, useRef } from "react";

const BASE_URL = "http://localhost:5001";

type Message = { role: string; content: string; sql?: string };

export default function AiChat() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  async function startSession() {
    setLoading(true);
    setStatus("Analyzing your uploaded data...");
    setMessages([]);
    try {
      const res = await fetch(`${BASE_URL}/ai/start`, { method: "POST" });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setSessionId(data.session_id);
      setMessages([{ role: "assistant", content: data.assistant }]);
      setStatus(null);
    } catch (err: any) {
      setStatus(`Error: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    startSession();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!sessionId) return setStatus("No session. Click 'Refresh Analysis' first.");
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: userMsg }]);
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(`${BASE_URL}/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: userMsg }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setMessages((m) => [...m, { role: "assistant", content: data.assistant, sql: data.sql || undefined }]);
    } catch (err: any) {
      setStatus(`Error: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ marginBottom: 8, display: "flex", gap: 8, alignItems: "center" }}>
        <button
          className="btn btn-primary"
          onClick={startSession}
          disabled={loading}
          title="Re-analyze based on your current uploaded transactions"
        >
          {loading && messages.length === 0 ? "Analyzing..." : "🔄 Refresh Analysis"}
        </button>
        {status && <span style={{ color: "var(--muted)", fontSize: 13 }}>{status}</span>}
      </div>

      <div style={{ flex: 1, overflowY: "auto", border: "1px solid var(--border)", padding: "12px 10px", borderRadius: 8, marginBottom: 8, display: "flex", flexDirection: "column", gap: 12 }}>
        {messages.length === 0 && loading && (
          <div style={{ color: "var(--muted)", fontSize: 14, textAlign: "center", marginTop: 24 }}>
            Loading analysis from your uploaded data...
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: m.role === "user" ? "flex-end" : "flex-start" }}>
            <div
              style={{
                maxWidth: "85%",
                background: m.role === "user" ? "var(--accent)" : "var(--card-bg, #23272f)",
                color: m.role === "user" ? "#fff" : "var(--fg)",
                borderRadius: m.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                padding: "8px 14px",
                fontSize: 14,
                lineHeight: 1.6,
                whiteSpace: "pre-wrap",
                boxShadow: "0 1px 3px rgba(0,0,0,0.15)",
              }}
            >
              {m.content}
            </div>
            {m.sql && (
              <details style={{ maxWidth: "85%", marginTop: 4 }}>
                <summary style={{ fontSize: 11, color: "var(--muted)", cursor: "pointer", userSelect: "none" }}>
                  🔍 Live SQL query used
                </summary>
                <pre style={{
                  fontSize: 11, color: "var(--muted)", background: "var(--card-bg, #1a1d23)",
                  borderRadius: 6, padding: "6px 10px", marginTop: 4, overflowX: "auto",
                  border: "1px solid var(--border)", whiteSpace: "pre-wrap", wordBreak: "break-all",
                }}>
                  {m.sql}
                </pre>
              </details>
            )}
            <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 2, paddingLeft: 4 }}>
              {m.role === "user" ? "You" : "MoneyMentor"}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          className="input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
          placeholder="Ask about your finances... (Enter to send)"
          disabled={loading || !sessionId}
          style={{ flex: 1 }}
        />
        <button
          className="btn btn-primary"
          onClick={sendMessage}
          disabled={!sessionId || loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
