"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { label: "Dashboard", href: "/manager", icon: "📊" },
    { label: "Add Employee", href: "/manager/add-employee", icon: "➕" },
    { label: "Remove Employee", href: "/manager/remove-employee", icon: "❌" },
    { label: "List Employees", href: "/manager/list-employees", icon: "📋" },
    { label: "Project Manager", href: "/manager/project-manager", icon: "📁" },
    { label: "Calendar", href: "/manager/calendar", icon: "🗓️" },
    { label: "Email", href: "/manager/email", icon: "✉️" },
    { label: "Tasks", href: "/manager/tasks", icon: "📝" },
    { label: "Chat with Employees", href: "/manager/chat", icon: "💬" },
    { label: "Attendance", href: "/manager/attendance", icon: "📅" },
    { label: "Leave Requests", href: "/manager/leave-requests", icon: "📄" },
  ];

  return (
    <div
      style={{
        width: "200px", // ← reduced from 250px
        height: "100vh",
        position: "fixed",
        top: 0,
        left: 0,
        backgroundColor: "#1f2937",
        padding: "30px 16px", // slightly reduced horizontal padding
        color: "#fff",
      }}
    >
      <h2 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "24px" }}>
        Manager Panel
      </h2>
      <ul
        style={{
          listStyle: "none",
          padding: 0,
          display: "flex",
          flexDirection: "column",
          gap: "14px",
        }}
      >
        {navItems.map((item, index) => {
          return (
            <li key={`${item.href}-${index}`}>
              <Link
                href={item.href}
                style={{
                  textDecoration: "none",
                  color: pathname === item.href ? "#4ade80" : "#f3f4f6",
                  fontSize: "15px",
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  padding: "6px 10px",
                  borderRadius: "6px",
                  backgroundColor: pathname === item.href ? "#374151" : "transparent",
                  transition: "background 0.2s ease",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = "#374151")
                }
                onMouseLeave={(e) => {
                  if (pathname !== item.href) {
                    e.currentTarget.style.backgroundColor = "transparent";
                  }
                }}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
