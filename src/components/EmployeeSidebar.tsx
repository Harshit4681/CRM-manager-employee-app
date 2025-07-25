// src/components/EmployeeSidebar.tsx

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function EmployeeSidebar() {
  const pathname = usePathname();

  const navItems = [
    { href: '/employee', label: '👨‍💼 Dashboard' },
    { href: '/employee/email', label: '📨 Email' },
    { href: '/employee/tasks', label: '📋 Task Manager' },
    { href: '/employee/chat', label: '💬 Messenger' },
    { href: '/employee/ai', label: '🤖 AI Assistant' },
    { href: '/employee/projects', label: '📁 Projects' },
    { href: '/employee/attendance', label: '📅 Attendance' },
    { href: '/employee/calendar', label: '🗓️ Calendar' },
    { label: "Leave Management", href: "/employee/leave-management", icon: "📝" },

    { href: '/employee/leave', label: '📝 Leave Management' },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontSize: '20px', fontWeight: 'bold' }}>Employee Panel</h2>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            style={{
              textDecoration: 'none',
              color: pathname === item.href ? '#0070f3' : '#333',
              fontWeight: pathname === item.href ? 'bold' : 'normal',
              backgroundColor: pathname === item.href ? '#e0e0e0' : 'transparent',
              padding: '8px 12px',
              borderRadius: '6px'
            }}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </div>
  );
}
 