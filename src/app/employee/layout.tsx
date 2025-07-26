// src/app/employee/layout.tsx

import React from 'react';
import EmployeeSidebar from '@/components/EmployeeSidebar';

export default function EmployeeLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <aside style={{
        width: '250px',
        backgroundColor: '#f4f4f4',
        padding: '20px',
        borderRight: '1px solid #ddd'
      }}>
        <EmployeeSidebar />
      </aside>
      <main style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
        {children}
      </main>
    </div>
  );
}