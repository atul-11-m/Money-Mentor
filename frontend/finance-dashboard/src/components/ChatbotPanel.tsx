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
    <div className="flex flex-col h-40">
      <div className="flex-1 overflow-y-auto border p-2 mb-2 rounded">
        {messages.map((msg, i) => (
          <div key={i} className="mb-1 text-sm bg-gray-100 p-1 rounded">
            {msg}
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          className="flex-1 border rounded-l px-2 text-sm"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button
          className="bg-blue-500 text-white px-3 rounded-r text-sm"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
}
