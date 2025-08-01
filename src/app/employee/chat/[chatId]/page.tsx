"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import {
  subscribeToMessages,
  sendMessage,
  markChatAsRead,
} from "@/lib/chatService";

export default function EmployeeChatScreen() {
  const params = useParams();
  const chatId = params?.chatId as string | undefined;

  const [msgs, setMsgs] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const [employeeEmail, setEmployeeEmail] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedEmail = localStorage.getItem("employeeEmail");
      if (storedEmail) setEmployeeEmail(storedEmail);
    }
  }, []);

  useEffect(() => {
    if (!chatId || !employeeEmail) return;

    const unsub = subscribeToMessages(chatId, setMsgs);
    markChatAsRead(chatId, employeeEmail);

    return () => {
      if (typeof unsub === "function") unsub();
    };
  }, [chatId, employeeEmail]);

  useEffect(() => {
    ref.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs]);

  const handleSend = async () => {
    if (!input.trim() || !chatId || !employeeEmail) return;
    await sendMessage(chatId, employeeEmail, input.trim());
    setInput("");
  };

  return (
    <div
      style={{
        padding: "2rem",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <h2>💬 Chat</h2>
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          background: "#f3f4f6",
          padding: "1rem",
          borderRadius: "8px",
        }}
      >
        {msgs.map((msg) => (
          <div
            key={msg.id}
            style={{
              textAlign: msg.sender === employeeEmail ? "right" : "left",
              marginBottom: "10px",
            }}
          >
            <div
              style={{
                display: "inline-block",
                backgroundColor:
                  msg.sender === employeeEmail ? "#22c55e" : "#d1d5db",
                color: msg.sender === employeeEmail ? "#fff" : "#000",
                padding: "10px 14px",
                borderRadius: "20px",
              }}
            >
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={ref} />
      </div>
      <div
        style={{
          display: "flex",
          gap: "10px",
          marginTop: "1rem",
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: "10px",
            borderRadius: "6px",
            border: "1px solid #ccc",
          }}
        />
        <button
          onClick={handleSend}
          style={{
            padding: "10px 20px",
            background: "#22c55e",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
