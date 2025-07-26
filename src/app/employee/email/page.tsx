'use client';
import { useEffect, useState } from 'react';

const EmployeeEmailPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('');
  const [text, setText] = useState('');
  const [inbox, setInbox] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  /* ───────────────────────────────────────────
     Load credentials once on the client side */
  useEffect(() => {
    const storedEmail = localStorage.getItem('employeeEmail') || '';
    const storedPassword = localStorage.getItem('employeePassword') || '';
    setEmail(storedEmail);
    setPassword(storedPassword);
    loadInbox();          // 👈 fetch inbox with GET
  }, []);

  /* ───────────────────────────────────────────
     Send e‑mail via /api/send-email (unchanged) */
  const sendEmail = async () => {
    setLoading(true);
    const res = await fetch('/api/send-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, to, subject, text }),
    });
    const data = await res.json();
    setLoading(false);
    if (data.success) {
      alert('✅ Email sent!');
      setTo(''); setSubject(''); setText('');
      loadInbox();               // refresh inbox after sending
    } else {
      alert('❌ Send failed: ' + data.error);
    }
  };

  /* ───────────────────────────────────────────
     GET inbox from /api/fetch-emails (your route) */
  const loadInbox = async () => {
    try {
      const res = await fetch('/api/fetch-emails', { method: 'GET' });
      if (!res.ok) {
        console.error('Inbox fetch failed:', await res.text());
        return;
      }
      const data = await res.json();
      setInbox(data.emails || []);
    } catch (err) {
      console.error('loadInbox error:', err);
    }
  };

  /* ─────────────────────────────────────────── */
  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ marginBottom: 20 }}>📨 Compose Email</h2>
      <input placeholder="To" value={to} onChange={(e) => setTo(e.target.value)} style={input} />
      <input placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} style={input} />
      <textarea placeholder="Message" value={text} onChange={(e) => setText(e.target.value)}
                style={{ ...input, height: 100 }} />
      <button onClick={sendEmail} disabled={loading} style={button}>
        {loading ? 'Sending…' : 'Send'}
      </button>

      <h2 style={{ marginTop: 40 }}>📥 Inbox</h2>
      {inbox.length === 0 ? (
        <p>No emails found.</p>
      ) : (
        inbox.map((mail, i) => (
          <div key={i} style={mailBox}>
            <strong>{mail.subject}</strong> — {mail.from}<br/>
            <small>{new Date(mail.date).toLocaleString()}</small>
            <p style={{ whiteSpace: 'pre-wrap' }}>{mail.text}</p>
          </div>
        ))
      )}
    </div>
  );
};

const input = { width: '100%', padding: 10, marginBottom: 10, borderRadius: 4, border: '1px solid #ccc' };
const button = { ...input, background: '#2563eb', color: '#fff', cursor: 'pointer', fontWeight: 'bold' };
const mailBox = { padding: 10, marginBottom: 15, border: '1px solid #ccc', borderRadius: 6, background: '#f9f9f9' };

export default EmployeeEmailPage;