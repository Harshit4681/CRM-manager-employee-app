// ✅ FILE: src/app/employee/page.tsx
'use client';

import React from 'react';

export default function EmployeeDashboardHome() {
  return (
    <div style={{ padding: '20px' }}>
      <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '20px' }}>
        👋 Welcome to Your Dashboard
      </h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
        <Card title="📨 Email System" description="Send and receive internal company emails." />
        <Card title="📋 Task Manager" description="View and manage assigned tasks." />
        <Card title="💬 Messenger" description="Chat with your teammates in real-time." />
        <Card title="🤖 AI Assistant" description="Use AI for writing, research, and brainstorming." />
        <Card title="📁 Ongoing Projects" description="View your assigned projects and updates." />
        <Card title="📅 Attendance" description="Mark your attendance and view history." />
        <Card title="🗓️ Calendar" description="See upcoming deadlines and meetings." />
        <Card title="📝 Leave Management" description="Apply for leave and track your balance." />
      </div>
    </div>
  );
}

function Card({ title, description }: { title: string; description: string }) {
  return (
    <div style={{ borderRadius: '8px', padding: '16px', background: '#f9f9f9' }}>
      <h2 style={{ fontSize: '20px', marginBottom: '10px' }}>{title}</h2>
      <p style={{ fontSize: '14px', color: '#555' }}>{description}</p>
    </div>
  );
}