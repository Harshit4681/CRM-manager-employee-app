import {
  collection,
  doc,
  addDoc,
  getDoc,
  getDocs,
  updateDoc,
  query,
  where,
  onSnapshot,
  orderBy,
  serverTimestamp,
  DocumentData,
} from "firebase/firestore";
import { db } from "./firebase";

/* 🟡  one stable chat per two users */
export const getOrCreateChat = async (a: string, b: string): Promise<string> => {
  const chatKey = a < b ? `${a}_${b}` : `${b}_${a}`;
  const q = query(collection(db, "chats"), where("chatKey", "==", chatKey));
  const snap = await getDocs(q);
  if (!snap.empty) return snap.docs[0].id;

  const ref = await addDoc(collection(db, "chats"), {
    participants: [a, b],
    chatKey,
    lastMessage: "",
    lastUpdated: serverTimestamp(),
    unreadBy: [b],
  });
  return ref.id;
};

/* 🟡  send message + update metadata */
export const sendMessage = async (
  chatId: string,
  sender: string,
  text: string
): Promise<void> => {
  if (!text.trim()) return;

  await addDoc(collection(db, "chats", chatId, "messages"), {
    sender,
    text,
    timestamp: serverTimestamp(),
  });

  const ref = doc(db, "chats", chatId);
  const snap = await getDoc(ref);
  if (!snap.exists()) return;

  const data = snap.data() as { participants: string[] };
  const unreadBy = data.participants.filter((p) => p !== sender);

  await updateDoc(ref, {
    lastMessage: text,
    lastUpdated: serverTimestamp(),
    unreadBy,
  });
};

/* 🟡  live inbox */
export const subscribeToChats = (
  email: string,
  cb: (c: any[]) => void
): (() => void) =>
  onSnapshot(
    query(collection(db, "chats"), where("participants", "array-contains", email)),
    (s) =>
      cb(
        s.docs
          .map((d) => ({ id: d.id, ...d.data() }))
          .sort((x: DocumentData, y: DocumentData) => {
            const t1 = x.lastUpdated?.toMillis?.() ?? 0;
            const t2 = y.lastUpdated?.toMillis?.() ?? 0;
            return t2 - t1;
          })
      )
  );

/* 🟡  live messages */
export const subscribeToMessages = (
  id: string,
  cb: (m: any[]) => void
): (() => void) =>
  onSnapshot(
    query(collection(db, "chats", id, "messages"), orderBy("timestamp", "asc")),
    (s) => cb(s.docs.map((d) => ({ id: d.id, ...d.data() })))
  );

/* 🟡  clear unread for viewer */
export const markChatAsRead = async (id: string, email: string): Promise<void> => {
  const ref = doc(db, "chats", id);
  const snap = await getDoc(ref);
  if (!snap.exists()) return;
  const data = snap.data() as { unreadBy: string[] };
  await updateDoc(ref, { unreadBy: data.unreadBy.filter((u) => u !== email) });
};
//hii