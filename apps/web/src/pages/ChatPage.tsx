import { useState } from "react";
import { Link } from "react-router-dom";
import { useChat } from "../hooks/useChat";

export default function ChatPage() {
  const [messages, setMessages] = useState<{ role: "user" | "bot"; text: string }[]>([]);
  const [input, setInput] = useState("");
  const chat = useChat();

  const send = async () => {
    if (!input.trim()) return;
    setMessages(m => [...m, { role: "user", text: input }]);
    setInput("");
    try {
      const reply = await chat.mutateAsync(input);
      setMessages(m => [...m, { role: "bot", text: reply }]);
    } catch (e) {
      setMessages(m => [...m, { role: "bot", text: "❌ Error talking to agent" }]);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Chat with your assistant</h1>
        <Link to="/agenda" className="text-blue-400 hover:underline">Agenda ↗</Link>
      </header>

      <div className="border border-slate-600 rounded p-3 h-96 overflow-y-auto space-y-2">
        {messages.map((m, i) => (
          <p key={i} className={m.role === "user" ? "text-right" : ""}>
            <span className={m.role === "user" ? "text-blue-300" : "text-green-300"}>
              {m.role === "user" ? "You: " : "Bot: "}
            </span>
            {m.text}
          </p>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
          className="flex-1 bg-slate-800 border border-slate-600 rounded p-2"
          placeholder="Ask something…"
        />
        <button onClick={send} className="bg-blue-600 px-4 rounded disabled:opacity-50" disabled={chat.isPending}>
          Send
        </button>
      </div>
    </div>
  );
}
