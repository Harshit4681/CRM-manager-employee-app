"use client";

import { useEffect, useState } from "react";
import { db } from "@/lib/firebase";
import { collection, getDocs } from "firebase/firestore";

export default function EmployeeProjectsPage() {
  const [projects, setProjects] = useState<any[]>([]);

  useEffect(() => {
    const fetchProjects = async () => {
      const snap = await getDocs(collection(db, "projects"));
      const data = snap.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
      setProjects(data);
    };
    fetchProjects();
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>📁 Projects</h2>
      {projects.length === 0 ? (
        <p>No projects found.</p>
      ) : (
        projects.map((p) => (
          <div key={p.id} style={{ marginBottom: "1rem" }}>
            <h3>{p.title}</h3>
            <p>{p.description}</p>
            <p>Deadline: {p.deadline}</p>
          </div>
        ))
      )}
    </div>
  );
}
