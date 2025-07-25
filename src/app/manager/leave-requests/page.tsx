'use client';
import { useEffect, useState } from 'react';
import { db } from '@/lib/firebase';
import { collection, getDocs, doc, updateDoc } from 'firebase/firestore';

const ManagerLeaveRequestsPage = () => {
  const [requests, setRequests] = useState<any[]>([]);

  const fetchAllRequests = async () => {
    const snapshot = await getDocs(collection(db, 'leave_requests'));
    const data = snapshot.docs.map((doc) => ({
      id: doc.id,
      ...doc.data(),
    }));
    setRequests(data);
  };

  useEffect(() => {
    fetchAllRequests();
  }, []);

  const handleUpdateStatus = async (id: string, newStatus: string) => {
    const docRef = doc(db, 'leave_requests', id);
    await updateDoc(docRef, { status: newStatus });
    fetchAllRequests();
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Leave Requests</h2>
      <ul>
        {requests.map((req, i) => (
          <li key={i} style={{ marginBottom: 10 }}>
            <b>{req.email}</b><br />
            {req.from} to {req.to} | {req.type}<br />
            Reason: {req.reason}<br />
            Status: <b>{req.status}</b>
            {req.status === 'Pending' && (
              <>
                <button onClick={() => handleUpdateStatus(req.id, 'Approved')}>✅ Approve</button>
                <button onClick={() => handleUpdateStatus(req.id, 'Rejected')}>❌ Reject</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ManagerLeaveRequestsPage;
    