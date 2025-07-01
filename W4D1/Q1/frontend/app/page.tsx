"use client";
import { useState, useRef, useEffect } from "react";
import { sendChatMessage, ChatResponse } from "@/lib/api";
import Message from "@/components/Message";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res: ChatResponse = await sendChatMessage(userMsg.content);
      const botMsg: Message = { role: "assistant", content: res.answer, sources: res.sources || [] };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { role: "assistant", content: "Error fetching response" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">MCP Expert Chatbot</h1>
      <div className="flex-1 overflow-y-auto border rounded p-4 space-y-4 bg-gray-50 dark:bg-zinc-900">
        {messages.map((m, idx) => (
          <Message key={idx} {...m} />
        ))}
        {loading && <p className="text-gray-400">Generating...</p>}
        <div ref={bottomRef} />
      </div>
      <div className="mt-4 flex gap-2">
        <input
          className="flex-1 border rounded p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me about MCP..."
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={handleSend}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
