// ❌ DO NOT use 'use client' here
import { AuthProvider } from "@/lib/authContext";
import AppProtectedWrapper from "@/components/AppProtectedWrapper";

export const metadata = {
  title: "Manager-Employee App",
  description: "Admin dashboard for managing team",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>
        <AuthProvider>
          <AppProtectedWrapper>
            {children}
          </AppProtectedWrapper>
        </AuthProvider>
      </body>
    </html>
  );
}
