// ✅ FILE: app/employee/chat/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { subscribeToChats, getOrCreateChat } from "@/lib/chatService";
import { getDocs, collection } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function EmployeeInboxPage() {
  const [chats, setChats] = useState<any[]>([]);
  const router = useRouter();
  const employeeEmail = typeof window !== "undefined" ? localStorage.getItem("employeeEmail") : "";

  useEffect(() => {
    if (!employeeEmail) return;
    const unsub = subscribeToChats(employeeEmail, setChats);
    return () => unsub();
  }, [employeeEmail]);

  const handleClick = async (email: string) => {
    const chatId = await getOrCreateChat(employeeEmail!, email);
    router.push(`/employee/chat/${chatId}`);
  };

  const contacts = Array.from(new Set(chats.flatMap(chat => chat.participants)))
    .filter(e => e !== employeeEmail);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>📬 My Inbox</h2>
      {contacts.map(email => (
        <div
          key={email}
          onClick={() => handleClick(email)}
          style={{
            padding: "1rem",
            background: "#f3f4f6",
            marginBottom: "10px",
            borderRadius: "6px",
            cursor: "pointer",
            border: "1px solid #ccc",
          }}
        >
          <div><strong>{email}</strong></div>
          <div>Start chatting...</div>
        </div>
      ))}
    </div>
  );
}