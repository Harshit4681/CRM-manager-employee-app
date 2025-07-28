"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth, db } from "@/lib/firebase";
import { getDocs, collection } from "firebase/firestore";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Check if Firebase is initialized
    if (!auth || !db) {
      setError("Authentication service is not available. Please check your configuration.");
      return;
    }

    try {
      // ✅ Manager Login
      if (email === "harshitsharma.it27@jecrc.ac.in") {
        await signInWithEmailAndPassword(auth, email, password);
        localStorage.setItem("managerEmail", email);
        router.push("/manager");
        return;
      }

      // ✅ Employee Login (Firestore)
      const snapshot = await getDocs(collection(db, "employees"));
      const employees = snapshot.docs.map((doc) => doc.data());

      const found = employees.find(
        (emp) => emp.email === email && emp.password === password
      );

      if (found) {
        localStorage.setItem("employeeEmail", email);
        router.push("/employee");
      } else {
        setError("Invalid employee credentials.");
      }
    } catch (err: any) {
      setError("Login failed: " + err.message);
    }
  };

  return (
    <div style={{ padding: "50px", maxWidth: "400px", margin: "auto" }}>
      <h2 style={{ fontSize: "24px", marginBottom: "20px", textAlign: "center" }}>
        Login
      </h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          required
          onChange={(e) => setEmail(e.target.value)}
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          required
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
        />
        <button type="submit" style={buttonStyle}>Login</button>
      </form>
      {error && (
        <p style={{ color: "red", marginTop: "15px", textAlign: "center" }}>
          {error}
        </p>
      )}
    </div>
  );
}

const inputStyle = {
  width: "100%",
  padding: "10px",
  marginBottom: "10px",
  borderRadius: "4px",
  border: "1px solid #ccc",
  fontSize: "16px",
};

const buttonStyle = {
  width: "100%",
  padding: "10px",
  backgroundColor: "#2563eb",
  color: "white",
  border: "none",
  borderRadius: "4px",
  cursor: "pointer",
  fontSize: "16px",
};
