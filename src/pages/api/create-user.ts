// src/pages/api/create-user.ts
import type { NextApiRequest, NextApiResponse } from "next";
import { adminAuth, adminDb } from "@/lib/firebase-admin"; // Must be working!

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method Not Allowed" });
  }

  const { name, email, password } = req.body;

  if (!email || !password || !name) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  // Check if Firebase Admin is properly initialized
  if (!adminAuth || !adminDb) {
    return res.status(500).json({ error: "Firebase Admin not initialized. Check environment variables." });
  }

  try {
    // ✅ Create Firebase Auth user
    const userRecord = await adminAuth.createUser({
      email,
      password,
      displayName: name,
    });

    // ✅ Store additional details in Firestore
    await adminDb.collection("employees").doc(userRecord.uid).set({
      uid: userRecord.uid,
      name,
      email,
      password,
      createdAt: new Date(),
    });

    return res.status(200).json({ success: true });
  } catch (err: any) {
    console.error("🔥 Error creating user:", err.message);
    return res.status(500).json({ error: err.message || "Internal server error" });
  }
}
