"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import "react-calendar/dist/Calendar.css";
import { addEvent, fetchAllEvents, deleteEvent } from "@/lib/eventService";

const Calendar = dynamic(() => import("react-calendar"), { ssr: false });

type Event = { id: string; title: string; description: string; date: string };

export default function ManagerCalendarPage() {
  const [mounted, setMounted] = useState(false);
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    setMounted(true);
    const load = async () => setEvents(await fetchAllEvents());
    load();
  }, []);

  if (!mounted) return null; // 🔐 Fix hydration mismatch

  const fmt = (d: Date) =>
    `${String(d.getDate()).padStart(2, "0")}-${String(d.getMonth() + 1).padStart(
      2,
      "0"
    )}-${d.getFullYear()}`;

  const tileContent = ({ date }: { date: Date }) =>
    events.some((e) => e.date === fmt(date)) ? (
      <div style={{ fontSize: "10px", color: "red" }}>●</div>
    ) : null;

  const handleAdd = async () => {
    if (!selectedDate || !title || !description) {
      alert("Pick a date and fill title/description.");
      return;
    }
    await addEvent({ title, description, date: selectedDate });
    setTitle("");
    setDescription("");
    setSelectedDate(null);
    setEvents(await fetchAllEvents());
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this event?")) return;
    await deleteEvent(id);
    setEvents(await fetchAllEvents());
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>🗓️ Calendar (Manager)</h2>

      <Calendar
        onClickDay={(d) => setSelectedDate(d)}
        tileContent={tileContent}
      />

      {selectedDate && (
        <div style={{ marginTop: "1.5rem", border: "1px solid #ccc", padding: "1rem" }}>
          <h3>Add Event on {fmt(selectedDate)}</h3>
          <input
            style={{ display: "block", marginBottom: "8px", width: "100%" }}
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <textarea
            style={{ display: "block", marginBottom: "8px", width: "100%" }}
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <button onClick={handleAdd}>➕ Save Event</button>
        </div>
      )}

      <h3 style={{ marginTop: "2rem" }}>All Events</h3>
      {events.map((ev) => (
        <div key={ev.id} style={{ border: "1px solid #ddd", padding: "8px", marginBottom: "8px" }}>
          <strong>{ev.title}</strong> — {ev.date}
          <p>{ev.description}</p>
          <button onClick={() => handleDelete(ev.id)}>🗑️ Delete</button>
        </div>
      ))}
    </div>
  );
}
