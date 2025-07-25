// src/lib/eventService.ts
import { db } from "./firebase";
import {
  collection,
  addDoc,
  getDocs,
  deleteDoc,
  doc,
  Timestamp,
} from "firebase/firestore";

export async function addEvent(event: {
  title: string;
  description: string;
  date: Date;
}) {
  const dateStr = `${String(event.date.getDate()).padStart(2, "0")}-${String(
    event.date.getMonth() + 1
  ).padStart(2, "0")}-${event.date.getFullYear()}`;

  await addDoc(collection(db, "managerCalendar"), {
    title: event.title,
    description: event.description,
    date: dateStr,
    createdAt: Timestamp.now(),
  });
}

export async function fetchAllEvents() {
  const querySnapshot = await getDocs(collection(db, "managerCalendar"));
  return querySnapshot.docs.map((doc) => ({
    id: doc.id,
    ...(doc.data() as any),
  }));
}

// ✅ ADD THIS FUNCTION
export async function deleteEvent(id: string) {
  await deleteDoc(doc(db, "managerCalendar", id));
}
