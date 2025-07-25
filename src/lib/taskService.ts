import {
  collection,
  query,
  where,
  onSnapshot,
  addDoc,
  deleteDoc,
  doc,
  getDocs,
  Timestamp,
} from "firebase/firestore";
import { db } from "./firebase";

// ─────────────────────────────────────────────
// ✅ 1. Manager creates a new task for an employee
export const createTask = async (task: {
  title: string;
  description: string;
  due: string;
  assignedTo: string;    // employee email
  createdBy: string;     // manager name/email
}) => {
  return await addDoc(collection(db, "tasks"), task);
};

// ✅ 2. Manager fetches all tasks (for table/list view)
export const fetchAllTasks = async () => {
  const snapshot = await getDocs(collection(db, "tasks"));
  return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
};

// ─────────────────────────────────────────────
// ✅ 3. Employee: subscribe to manager-assigned tasks
export const subscribeToTasks = (
  email: string,
  callback: (tasks: any[]) => void
) => {
  const q = query(collection(db, "tasks"), where("assignedTo", "==", email));
  const unsubscribe = onSnapshot(q, (snapshot) => {
    const tasks = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
    callback(tasks);
  });
  return unsubscribe;
};

// ─────────────────────────────────────────────
// ✅ 4. Employee: subscribe to their own personal tasks
export const subscribeToPersonalTasks = (
  email: string,
  callback: (tasks: any[]) => void
) => {
  const q = query(collection(db, "personalTasks"), where("user", "==", email));
  const unsubscribe = onSnapshot(q, (snapshot) => {
    const tasks = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
    callback(tasks);
  });
  return unsubscribe;
};

// ✅ 5. Employee: add a personal task
export const addPersonalTask = async (
  email: string,
  title: string,
  description: string
) => {
  return await addDoc(collection(db, "personalTasks"), {
    user: email,
    title,
    description,
    createdAt: Timestamp.now(),
  });
};

// ✅ 6. Employee: delete a personal task
export const deletePersonalTask = async (id: string) => {
  return await deleteDoc(doc(db, "personalTasks", id));
};

// ✅ 7. Manager: delete any task (by ID)
export const deleteTask = async (id: string) => {
  return await deleteDoc(doc(db, "tasks", id));
};
