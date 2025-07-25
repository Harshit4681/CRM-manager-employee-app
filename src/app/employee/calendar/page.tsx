"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import "react-calendar/dist/Calendar.css";
import { fetchAllEvents } from "@/lib/eventService";

const Calendar = dynamic(() => import("react-calendar"), { ssr: false });

type Event = {
  id: string;
  title: string;
  description: string;
  date: string; // "dd-mm-yyyy"
};

export default function EmployeeCalendarPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  useEffect(() => {
    const loadEvents = async () => {
      const all = await fetchAllEvents();
      setEvents(all as Event[]);
    };
    loadEvents();
  }, []);

  const formatDate = (date: Date) => {
    const dd = String(date.getDate()).padStart(2, "0");
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const yyyy = date.getFullYear();
    return `${dd}-${mm}-${yyyy}`;
  };

  const tileContent = ({ date }: { date: Date }) => {
    const formatted = formatDate(date);
    const hasEvent = events.find((ev) => ev.date === formatted);
    return hasEvent ? (
      <div style={{ fontSize: "10px", color: "blue" }}>📌</div>
    ) : null;
  };

  const showEventsForDate = (date: Date) => {
    const formatted = formatDate(date);
    return events.filter((ev) => ev.date === formatted);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>📅 My Calendar</h2>

      <Calendar
        onClickDay={(date) => setSelectedDate(date)}
        tileContent={tileContent}
      />

      {selectedDate && (
        <div style={{ marginTop: "2rem" }}>
          <h3>Events on {formatDate(selectedDate)}</h3>
          {showEventsForDate(selectedDate).length === 0 ? (
            <p>No events.</p>
          ) : (
            showEventsForDate(selectedDate).map((event) => (
              <div
                key={event.id}
                style={{
                  border: "1px solid #ccc",
                  padding: "10px",
                  marginBottom: "10px",
                }}
              >
                <strong>{event.title}</strong>
                <p>{event.description}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
