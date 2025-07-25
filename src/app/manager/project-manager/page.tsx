"use client";

import { useEffect, useState } from "react";
import { db } from "@/lib/firebase";
import { collection, addDoc, getDocs, deleteDoc, doc, serverTimestamp } from "firebase/firestore";

export default function ProjectManagerPage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [deadline, setDeadline] = useState("");
  const [status, setStatus] = useState("Pending");
  const [loading, setLoading] = useState(false);


  const fetchProjects = async () => {
    const snapshot = await getDocs(collection(db, "projects"));
    const all = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
    setProjects(all);
  };

  useEffect(() => {
    fetchProjects();
  }, []);
  const handleAddProject = async () => {
    if (!title.trim() || !desc.trim()) return;

    setLoading(true);
    await addDoc(collection(db, "projects"), {
      title,
      description: desc,
      assignedTo,
      deadline,
      status,
      createdAt: serverTimestamp(),
    });
    setTitle("");
    setDesc("");
    setAssignedTo("");
    setDeadline("");
    setStatus("Pending");
    await fetchProjects();
    setLoading(false);
  };

  const handleDelete = async (id: string) => {
    await deleteDoc(doc(db, "projects", id));
    setProjects(projects.filter((p) => p.id !== id));
  };

  return (
    <div style={{ marginLeft: "260px", padding: "30px", maxWidth: "800px" }}>
      <h2 style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "20px" }}>Project Manager</h2>

      <div style={{ marginBottom: "20px" }}>
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Project Title" style={inputStyle} />
        <textarea value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="Project Description" rows={3} style={{ ...inputStyle, resize: "vertical" }} />
        <input value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)} placeholder="Assigned To (email)" style={inputStyle} />
        <input value={deadline} onChange={(e) => setDeadline(e.target.value)} type="date" style={inputStyle} />
        <select value={status} onChange={(e) => setStatus(e.target.value)} style={inputStyle}>
          <option>Pending</option>
          <option>In Progress</option>
          <option>Completed</option>
        </select>

        <button onClick={handleAddProject} disabled={loading} style={buttonStyle}>
          {loading ? "Adding..." : "➕ Add Project"}
        </button>
      </div>

      <div>
        {projects.map((proj) => (
          <div key={proj.id} style={cardStyle}>
            <div>
              <h3 style={{ fontSize: "18px", fontWeight: "bold" }}>{proj.title}</h3>
              <p style={{ color: "#333" }}>{proj.description}</p>
              <p style={{ fontSize: "14px", marginTop: "4px" }}><strong>Assigned To:</strong> {proj.assignedTo || "Not assigned"}</p>
              <p style={{ fontSize: "14px" }}><strong>Deadline:</strong> {proj.deadline || "No deadline"}</p>
              <p style={{ fontSize: "14px" }}><strong>Status:</strong> {proj.status}</p>
            </div>
            <button onClick={() => handleDelete(proj.id)} style={deleteButtonStyle}>❌</button>
          </div>
        ))}
      </div>
    </div>
  );
}

const inputStyle = {
  width: "100%",
  padding: "10px",
  marginBottom: "10px",
  borderRadius: "6px",
  border: "1px solid #ccc",
  fontSize: "15px",
};

const buttonStyle = {
  padding: "10px 16px",
  backgroundColor: "#2563eb",
  color: "white",
  fontWeight: "bold",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer",
  marginBottom: "20px",
};

const cardStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  padding: "16px",
  marginBottom: "15px",
  backgroundColor: "#fff",
  boxShadow: "0 1px 6px rgba(0,0,0,0.1)",
  borderRadius: "8px",
};

const deleteButtonStyle = {
  backgroundColor: "#ef4444",
  color: "#fff",
  border: "none",
  borderRadius: "4px",
  padding: "8px",
  cursor: "pointer",
};
