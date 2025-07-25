'use client';
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

export default function AppProtectedWrapper({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const managerEmail = localStorage.getItem('managerEmail');
    const employeeEmail = localStorage.getItem('employeeEmail');

    if (pathname === '/login') return;

    if (!managerEmail && !employeeEmail) {
      router.replace('/login');
    }
  }, [pathname, router]);

  return <>{children}</>;
}
