#!/bin/bash
# Script to set Vercel environment variables

echo "Setting Vercel environment variables..."

vercel env add NEXT_PUBLIC_FIREBASE_API_KEY production
# When prompted, paste: AIzaSyC-ODeVBRPqiwT_STxqoSsVBxv_tYFnXD4

vercel env add NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN production  
# When prompted, paste: login-b3e0f.firebaseapp.com

vercel env add NEXT_PUBLIC_FIREBASE_PROJECT_ID production
# When prompted, paste: login-b3e0f

vercel env add FIREBASE_CLIENT_EMAIL production
# When prompted, paste: firebase-adminsdk-fbsvc@login-b3e0f.iam.gserviceaccount.com

vercel env add FIREBASE_PRIVATE_KEY production
# When prompted, paste the entire private key (including BEGIN/END lines)

echo "Environment variables set! Now redeploy your app."