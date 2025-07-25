"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { subscribeToMessages, sendMessage, markChatAsRead } from "@/lib/chatService";

export default function ManagerChatScreen() {
  const { chatId } = useParams();
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const managerEmail =
    typeof window !== "undefined" ? localStorage.getItem("managerEmail") : "";

  useEffect(() => {
    if (!chatId || !managerEmail) return;

    const unsub = subscribeToMessages(chatId as string, setMessages);
    markChatAsRead(chatId as string, managerEmail);
    return () => unsub();
  }, [chatId, managerEmail]);

  const handleSend = async () => {
    if (!input.trim()) return;
    await sendMessage(chatId as string, managerEmail!, input);
    setInput("");
  };

  return (
    <div style={{ padding: 32 }}>
      <h2>💬 Manager Chat</h2>

      <div style={{ maxHeight: 400, overflowY: "auto", border: "1px solid #ddd", padding: 12 }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              margin: "10px 0",
              textAlign: msg.sender === managerEmail ? "right" : "left",
            }}
          >
            <p
              style={{
                display: "inline-block",
                padding: 10,
                borderRadius: 10,
                background: msg.sender === managerEmail ? "#2563eb" : "#ccc",
                color: msg.sender === managerEmail ? "#fff" : "#000",
              }}
            >
              {msg.text}
            </p>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 20, display: "flex", gap: 10 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{
            flex: 1,
            padding: 10,
            borderRadius: 6,
            border: "1px solid #ccc",
          }}
          placeholder="Type a message..."
        />
        <button
          onClick={handleSend}
          style={{
            padding: "10px 20px",
            backgroundColor: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: 6,
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
