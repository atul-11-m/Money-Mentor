import { useState } from "react";

export default function ChatbotPanel() {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages([...messages, input]);
    setInput("");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: 160 }}>
      <div style={{ flex: 1, overflowY: "auto", border: "1px solid var(--border)", padding: 8, marginBottom: 8, borderRadius: 8 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 6, fontSize: 12, background: "rgba(255,255,255,0.03)", padding: 6, borderRadius: 6 }}>
            {msg}
          </div>
        ))}
      </div>
      <div style={{ display: "flex" }}>
        <input
          className="input"
          style={{ borderTopRightRadius: 0, borderBottomRightRadius: 0 }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button
          className="btn btn-primary"
          style={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
}
