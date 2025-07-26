// ✅ FILE: src/app/manager/chat/page.tsx

"use client"; // ⬅️ MUST be the very first line

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { subscribeToChats } from "@/lib/chatService";
import { collection, getDocs } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function ManagerInbox() {
  const router = useRouter();
  const [managerEmail, setManagerEmail] = useState("");
  const [chats, setChats] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);

  useEffect(() => {
    const email = localStorage.getItem("managerEmail");
    if (!email) return;
    setManagerEmail(email);
    const unsub = subscribeToChats(email, setChats);
    return () => unsub();
  }, []);

  useEffect(() => {
    const fetchEmployees = async () => {
      const snap = await getDocs(collection(db, "employees"));
      const list = snap.docs.map((doc) => doc.data());
      setEmployees(list);
    };
    fetchEmployees();
  }, []);

  const handleChat = async (email: string) => {
    const { getOrCreateChat } = await import("@/lib/chatService");
    const chatId = await getOrCreateChat(managerEmail, email);
    router.push(`/manager/chat/${chatId}`);
  };

  return (
    <div style={{ padding: 32 }}>
      <h2>💬 Manager Inbox</h2>

      {chats.map((chat) => {
        const other = chat.participants.find((p: string) => p !== managerEmail);
        return (
          <div key={chat.id} style={{ border: "1px solid #ccc", padding: 16, margin: 10 }}>
            <p><strong>{other}</strong></p>
            <p>{chat.lastMessage || "Start chatting..."}</p>
            <button onClick={() => router.push(`/manager/chat/${chat.id}`)}>Open</button>
          </div>
        );
      })}

      <h3>Start New Chat</h3>
      {employees.map((emp: any) => (
        <div key={emp.email} style={{ marginTop: 10 }}>
          <p>{emp.name} ({emp.email})</p>
          <button onClick={() => handleChat(emp.email)}>Chat</button>
        </div>
      ))}
    </div>
  );
}