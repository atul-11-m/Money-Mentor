import { useState } from "react";

export default function AiChat() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function analyze() {
    setLoading(true);
    setStatus(null);
    try {
      const fd = new FormData();
      if (file) fd.append("file", file);
      const res = await fetch("http://localhost:5000/ai/analyze", { method: "POST", body: fd });
      let data: any = null;
      try {
        data = await res.json();
      } catch (e) {
        const text = await res.text();
        throw new Error(`Non-JSON response from server: ${text}`);
      }
      if (data.error) {
        throw new Error(data.error || JSON.stringify(data));
      }
      const assistantContent = typeof data.assistant === "string" ? data.assistant : JSON.stringify(data.assistant);
      if (data.session_id) {
        setSessionId(data.session_id);
        setMessages([{ role: "assistant", content: assistantContent }] as any);
      } else if (data.assistant) {
        setMessages([{ role: "assistant", content: assistantContent }] as any);
      }
      setStatus("Analysis complete");
    } catch (err: any) {
      setStatus(`Error: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage() {
    if (!sessionId) return setStatus("No session. Run analysis first or start a session.");
    if (!input.trim()) return;
    setLoading(true);
    setStatus(null);
    try {
      setMessages((m) => [...m, { role: "user", content: input }] );
      const res = await fetch("http://localhost:5000/ai/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ session_id: sessionId, message: input }) });
      let data: any = null;
      try {
        data = await res.json();
      } catch (e) {
        const text = await res.text();
        throw new Error(`Non-JSON response from server: ${text}`);
      }
      if (data.error) {
        throw new Error(data.error || JSON.stringify(data));
      }
      const assistantContent = typeof data.assistant === "string" ? data.assistant : JSON.stringify(data.assistant);
      if (data.assistant) {
        setMessages((m) => [...m, { role: "assistant", content: assistantContent }]);
      }
      setInput("");
    } catch (err: any) {
      setStatus(`Error: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ marginBottom: 8, display: "flex", gap: 8, alignItems: "center" }}>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} className="input" />
        <button className="btn btn-primary" onClick={analyze} disabled={loading}>{loading ? "Analyzing..." : "Analyze CSV / Data"}</button>
        <div style={{ color: "var(--muted)", fontSize: 13 }}>{status}</div>
      </div>

      <div style={{ flex: 1, overflowY: "auto", border: "1px solid var(--border)", padding: 8, borderRadius: 8, marginBottom: 8 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 6 }}>
            <div style={{ fontSize: 12, color: m.role === "assistant" ? "var(--muted)" : "var(--accent)", fontWeight: 600 }}>{m.role.toUpperCase()}</div>
            <div style={{ marginTop: 4 }}>{m.content}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <input className="input" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about your finances..." />
        <button className="btn btn-primary" onClick={sendMessage} disabled={!sessionId || loading}>Send</button>
      </div>
    </div>
  );
}
