import Sidebar from "@/components/Sidebar";

export default function ManagerLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />
      <main style={{
        marginLeft: "240px",
        padding: "20px",
        width: "100%",
        minHeight: "100vh",
        backgroundColor: "#f3f4f6"
      }}>
        {children}
      </main>
    </div>
  );
}
