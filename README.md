# CRM Manager Employee App

This is a [Next.js](https://nextjs.org) project for managing employees and projects in a CRM system.

## Prerequisites

- Node.js 18+ 
- Firebase project with Authentication and Firestore enabled

## Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env.local
```

2. Update `.env.local` with your Firebase configuration:
   - `NEXT_PUBLIC_FIREBASE_API_KEY`: Your Firebase project API key
   - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`: Your Firebase auth domain (project-id.firebaseapp.com)
   - `NEXT_PUBLIC_FIREBASE_PROJECT_ID`: Your Firebase project ID
   - `FIREBASE_CLIENT_EMAIL`: Service account email for Firebase Admin
   - `FIREBASE_PRIVATE_KEY`: Service account private key for Firebase Admin

## Getting Started

First, install dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Deployment on Vercel

1. **Set Environment Variables**: In your Vercel project dashboard, go to Settings > Environment Variables and add all the required Firebase environment variables.

2. **Deploy**: Connect your GitHub repository to Vercel and deploy.

### Required Environment Variables for Vercel:
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` 
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY`

## Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Enable Authentication with Email/Password
3. Create a Firestore database
4. Generate a service account key for Firebase Admin SDK
5. Add the configuration to your environment variables

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!