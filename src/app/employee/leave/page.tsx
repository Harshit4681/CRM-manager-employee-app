'use client';
import { useEffect, useState } from 'react';
import { db } from '@/lib/firebase';
import { collection, addDoc, query, where, getDocs } from 'firebase/firestore';

const EmployeeLeavePage = () => {
  const [email, setEmail] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [type, setType] = useState('Casual');
  const [reason, setReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [requests, setRequests] = useState<any[]>([]);

  useEffect(() => {
    const storedEmail = localStorage.getItem('employeeEmail');
    if (storedEmail) {
      setEmail(storedEmail);
      fetchRequests(storedEmail);
    }
  }, []);

  const fetchRequests = async (email: string) => {
    const q = query(collection(db, 'leave_requests'), where('email', '==', email));
    const snapshot = await getDocs(q);
    const data = snapshot.docs.map((doc) => doc.data());
    setRequests(data);
  };

  const handleSubmit = async () => {
    if (!fromDate || !toDate || !reason) return alert('Fill all fields');
    setSubmitting(true);

    await addDoc(collection(db, 'leave_requests'), {
      email,
      from: fromDate,
      to: toDate,
      reason,
      type,
      status: 'Pending',
      timestamp: new Date().toISOString(),
    });

    setFromDate('');
    setToDate('');
    setReason('');
    fetchRequests(email);
    setSubmitting(false);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Apply for Leave</h2>
      <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
      <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} />
      <select value={type} onChange={(e) => setType(e.target.value)}>
        <option>Casual</option>
        <option>Sick</option>
        <option>Earned</option>
      </select>
      <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Reason" />
      <button onClick={handleSubmit} disabled={submitting}>
        {submitting ? 'Submitting...' : 'Submit Request'}
      </button>

      <h3>Your Leave Requests</h3>
      <ul>
        {requests.map((req, i) => (
          <li key={i}>
            {req.from} to {req.to} - {req.type} - {req.status}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EmployeeLeavePage; // ✅ VERY IMPORTANT
