'use client';
import { useEffect, useState } from 'react';
import { db } from '@/lib/firebase';
import { collection, query, where, onSnapshot } from 'firebase/firestore';

const today = new Date().toISOString().split('T')[0]; // moved outside

const ManagerAttendancePage = () => {
  const [attendanceList, setAttendanceList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const attendanceRef = collection(db, 'attendance');
    const q = query(attendanceRef, where('date', '==', today));

    const unsub = onSnapshot(q, (snapshot) => {
      const data = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
      console.log('Realtime Attendance Docs:', data);
      setAttendanceList(data);
      setLoading(false);
    });

    return () => unsub();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Today&apos;s Attendance ({today})</h2>
      {loading ? (
        <p>Loading...</p>
      ) : attendanceList.length === 0 ? (
        <p>No one has marked attendance yet.</p>
      ) : (
        <ul>
          {attendanceList.map((item) => (
            <li key={item.id}>
              ✅ {item.email} at{' '}
              {new Date(item.timestamp).toLocaleTimeString()}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ManagerAttendancePage;
