"use client";
import { useEffect, useState } from "react";
// import { useRouter } from "next/navigation";
// import { onAuthStateChanged } from "firebase/auth";
// import { auth } from "@/lib/firebase";

export default function ManagerDashboardPage() {
  // const router = useRouter();
  const [loading, setLoading] = useState(false); // Set to false directly since no auth

  // useEffect(() => {
  //   const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
  //     if (!currentUser) {
  //       router.push("/login");
  //     } else if (currentUser.email !== "harshitsharma.it27@jecrc.ac.in") {
  //       router.push("/not-authorized");
  //     } else {
  //       setLoading(false);
  //     }
  //   });

  //   return () => unsubscribe();
  // }, [router]);

  if (loading) return <p>.......Loading</p>;

  return (
    <div>
      <h1 style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "20px" }}>
        Dashboard
      </h1>
      <div
        style={{
          background: "#fff",
          borderRadius: "10px",
          padding: "30px",
          boxShadow: "0 0 10px rgba(0,0,0,0.05)",
        }}
      >
        <h3>Google Analytics Area</h3>
        <div
          style={{
            background: "#e5e7eb",
            height: "300px",
            marginTop: "20px",
            borderRadius: "10px",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            color: "#6b7280",
          }}
        >
          Embed Google Analytics here
        </div>
      </div>
    </div>
  );
}
