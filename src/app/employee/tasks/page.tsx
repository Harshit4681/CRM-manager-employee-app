"use client";

import { useEffect, useState } from "react";
import {
  subscribeToTasks,            // ← existing (manager→employee)
  subscribeToPersonalTasks,    // ← new
  addPersonalTask,
  deletePersonalTask,
} from "@/lib/taskService";

export default function EmployeeTasksPage() {
  const [managerTasks,  setManagerTasks]  = useState<any[]>([]);
  const [personalTasks, setPersonalTasks] = useState<any[]>([]);
  const [title, setTitle]         = useState("");
  const [description, setDesc]    = useState("");

  /* ---------------- listen once we know the employee email ---------------- */
  useEffect(() => {
    const email = localStorage.getItem("employeeEmail");
    if (!email) {
      console.warn("employeeEmail missing from localStorage");
      return;
    }

    const unsubMgr  = subscribeToTasks(email,  setManagerTasks);
    const unsubPers = subscribeToPersonalTasks(email, setPersonalTasks);

    return () => { unsubMgr(); unsubPers(); };
  }, []);

  /* ---------------- add / delete personal tasks ---------------- */
  const handleAdd = async () => {
    const email = localStorage.getItem("employeeEmail");
    if (!email || !title.trim()) return;
    await addPersonalTask(email, title, description);
    setTitle(""); setDesc("");
  };
  const handleDelete = async (id: string) => deletePersonalTask(id);

  /* ---------------- UI ---------------- */
  return (
    <div style={{ padding: "2rem" }}>
      {/* Manager‑assigned */}
      <h2>📋 Tasks from Manager</h2>
      {managerTasks.length === 0
        ? <p>No tasks assigned.</p>
        : managerTasks.map(t => (
            <div key={t.id} style={box}>
              <h3>{t.title}</h3>
              <p>{t.description}</p>
              <p><strong>Due:</strong> {t.due}</p>
              <p>Status: {t.completed ? "✅ Done" : "❌ Pending"}</p>
            </div>
          ))}

      <hr style={{ margin: "2rem 0" }} />

      {/* Personal */}
      <h2>📝 My Personal Tasks</h2>
      <div style={{ marginBottom: "1rem" }}>
        <input
          placeholder="Title"
          value={title}
          onChange={e => setTitle(e.target.value)}
          style={{ ...input, width: "12rem" }}
        />
        <input
          placeholder="Description"
          value={description}
          onChange={e => setDesc(e.target.value)}
          style={{ ...input, width: "18rem" }}
        />
        <button onClick={handleAdd}>Add</button>
      </div>

      {personalTasks.length === 0
        ? <p>No personal tasks yet.</p>
        : personalTasks.map(t => (
            <div key={t.id} style={{ ...box, borderColor: "#999" }}>
              <h3>{t.title}</h3>
              <p>{t.description}</p>
              <button onClick={() => handleDelete(t.id)}>🗑️ Delete</button>
            </div>
          ))}
    </div>
  );
}

/* ---------- simple inline styles ---------- */
const box  = { border: "1px solid #ccc", padding: "1rem", marginBottom: "1rem" };
const input = { padding: "0.5rem", marginRight: "0.5rem" };
