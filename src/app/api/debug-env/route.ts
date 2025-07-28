// Debug endpoint to check environment variables
export async function GET() {
  const envCheck = {
    NODE_ENV: process.env.NODE_ENV,
    hasFirebaseApiKey: !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    hasFirebaseAuthDomain: !!process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    hasFirebaseProjectId: !!process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    hasFirebaseClientEmail: !!process.env.FIREBASE_CLIENT_EMAIL,
    hasFirebasePrivateKey: !!process.env.FIREBASE_PRIVATE_KEY,
    firebaseApiKeyPrefix: process.env.NEXT_PUBLIC_FIREBASE_API_KEY?.substring(0, 10) + '...',
    firebaseProjectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    vercelUrl: process.env.VERCEL_URL || 'not set',
    vercel: process.env.VERCEL || 'not set',
    hasValidConfig: !!(
      process.env.NEXT_PUBLIC_FIREBASE_API_KEY && 
      process.env.NEXT_PUBLIC_FIREBASE_API_KEY !== "dummy-api-key" &&
      process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN && 
      process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID
    )
  };

  return Response.json(envCheck);
}