'use client';
import { useEffect, useState, useCallback } from 'react';
import { db } from '@/lib/firebase';
import { doc, setDoc, getDoc } from 'firebase/firestore';

const EmployeeAttendancePage = () => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const today = new Date().toISOString().split('T')[0]; // "2025-07-13"
  const docId = `${email}_${today}`;

  const checkAttendance = useCallback(async (email: string) => {
    const docRef = doc(db, 'attendance', `${email}_${today}`);
    const snapshot = await getDoc(docRef);
    if (snapshot.exists()) {
      setStatus(snapshot.data().status);
    }
  }, [today]);

  useEffect(() => {
    const storedEmail = localStorage.getItem('employeeEmail');
    if (storedEmail) {
      setEmail(storedEmail);
      checkAttendance(storedEmail);
    }
  }, [checkAttendance]);

  const handleMarkAttendance = async () => {
    if (!email) return alert('Employee email not found');
    setLoading(true);
    const docRef = doc(db, 'attendance', docId);
    await setDoc(docRef, {
      email,
      date: today,
      status: 'Present',
      timestamp: new Date().toISOString(),
    });
    setStatus('Present');
    setLoading(false);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Attendance for {today}</h2>
      {status ? (
        <p>Status: ✅ {status}</p>
      ) : (
        <button onClick={handleMarkAttendance} disabled={loading}>
          {loading ? 'Marking...' : 'Mark Attendance'}
        </button>
      )}
    </div>
  );
};

export default EmployeeAttendancePage;
