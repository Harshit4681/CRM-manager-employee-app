'use client';
import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';

export default function AppProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const managerEmail = localStorage.getItem('managerEmail');
    const employeeEmail = localStorage.getItem('employeeEmail');

    // ⛔ Allow access to login page
    if (pathname === '/login') return;

    // ✅ If user is logged in (either manager or employee), allow
    if (managerEmail || employeeEmail) return;

    // ⛔ Not logged in → redirect to login
    router.replace('/login');
  }, [pathname, router]);

  return <>{children}</>;
}
