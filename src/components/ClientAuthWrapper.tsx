'use client';

import { AuthProvider } from "@/lib/authContext";
import { useEffect, useState } from "react";

export default function ClientAuthWrapper({ children }: { children: React.ReactNode }) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // During SSR or before hydration, render without Firebase context
  if (!isMounted) {
    return <>{children}</>;
  }

  // After hydration, render with Firebase context
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}