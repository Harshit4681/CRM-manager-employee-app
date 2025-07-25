"use client";

export default function AiAssistantPage() {
  return (
    <div style={{ padding: 32 }}>
      <h2 style={{ marginBottom: 20 }}>🤖 AI Assistant</h2>
      
      <div
        style={{
          height: "700px",
          width: "100%",
          border: "1px solid #ccc",
          borderRadius: "10px",
          overflow: "hidden",
        }}
      >
        <iframe
          src="https://www.chatbase.co/chatbot-iframe/h9NUWADrwoi0pXheBgpCS"
          width="100%"
          style={{ height: "100%", border: "none" }}
          frameBorder="0"
        />
      </div>
    </div>
  );
}
