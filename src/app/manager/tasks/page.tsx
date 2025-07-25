"use client";

import { useEffect, useState } from "react";
import {
  createTask,
  fetchAllTasks,
  deleteTask,
} from "@/lib/taskService";

export default function ManagerTasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    due: "",
    assignedTo: "",
  });

  // ⬇️ Load tasks once on page load
  useEffect(() => {
    const load = async () => setTasks(await fetchAllTasks());
    load();
  }, []);

  const handleAdd = async () => {
    const { title, description, due, assignedTo } = form;
    if (!title || !description || !due || !assignedTo) return alert("Fill all");

    await createTask({
      ...form,
      createdBy: "Manager", // or manager email
    });

    setTasks(await fetchAllTasks());
    setForm({ title: "", description: "", due: "", assignedTo: "" });
  };

  const handleDelete = async (id: string) => {
    await deleteTask(id);
    setTasks(await fetchAllTasks());
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>📋 Task Manager (Manager)</h2>

      {/* --- Add Task Form --- */}
      <input
        placeholder="Title"
        value={form.title}
        onChange={(e) => setForm({ ...form, title: e.target.value })}
      />
      <input
        placeholder="Description"
        value={form.description}
        onChange={(e) => setForm({ ...form, description: e.target.value })}
      />
      <input
        placeholder="Due (dd-mm-yyyy)"
        value={form.due}
        onChange={(e) => setForm({ ...form, due: e.target.value })}
      />
      <input
        placeholder="Assign to (employee email)"
        value={form.assignedTo}
        onChange={(e) => setForm({ ...form, assignedTo: e.target.value })}
      />
      <button onClick={handleAdd}>➕ Add Task</button>

      {/* --- Task List --- */}
      <h3 style={{ marginTop: "2rem" }}>All Tasks</h3>
      {tasks.map((task) => (
        <div key={task.id} style={{ border: "1px solid #ccc", padding: "1rem", marginBottom: "1rem" }}>
          <strong>{task.title}</strong> — {task.assignedTo}
          <br />
          {task.due} | {task.completed ? "✅" : "❌"}
          <br />
          <button onClick={() => handleDelete(task.id)}>🗑 Delete</button>
        </div>
      ))}
    </div>
  );
}
