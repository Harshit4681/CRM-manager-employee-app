// src/lib/firebase-admin.ts
import * as admin from "firebase-admin";

// Check if we have the required environment variables
const hasRequiredEnvVars = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID && 
                          process.env.FIREBASE_CLIENT_EMAIL && 
                          process.env.FIREBASE_PRIVATE_KEY;

if (!admin.apps.length && hasRequiredEnvVars) {
  admin.initializeApp({
    credential: admin.credential.cert({
      projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
      privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, "\n"),
    }),
  });
}

const adminAuth = hasRequiredEnvVars ? admin.auth() : null;
const adminDb = hasRequiredEnvVars ? admin.firestore() : null;

export { adminAuth, adminDb };
