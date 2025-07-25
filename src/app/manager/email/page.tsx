'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Email {
  from: string;
  subject: string;
  date: string;
  text: string;
  html: string;
}

export default function EmailPage() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  // Compose form state
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [status, setStatus] = useState('');

  const fetchEmails = async () => {
    try {
      const res = await axios.get('/api/fetch-emails');
      setEmails(res.data.emails);
    } catch (err) {
      console.error('Error fetching emails:', err);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  const handleSendEmail = async () => {
    if (!to || !subject || !body) {
      setStatus('All fields are required');
      return;
    }

    setStatus('Sending...');
    try {
      await axios.post('/api/send-email', { to, subject, text: body });
      setStatus('Email sent successfully!');
      setTo('');
      setSubject('');
      setBody('');
    } catch (err: any) {
      setStatus('Failed to send: ' + (err?.response?.data?.error || err.message));
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      {/* Compose Section */}
      <h2>📨 Compose Email</h2>
      <input
        placeholder="To"
        value={to}
        onChange={(e) => setTo(e.target.value)}
        style={{ width: '100%', padding: '8px', marginBottom: '8px' }}
      />
      <input
        placeholder="Subject"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        style={{ width: '100%', padding: '8px', marginBottom: '8px' }}
      />
      <textarea
        placeholder="Body"
        value={body}
        onChange={(e) => setBody(e.target.value)}
        style={{ width: '100%', height: '100px', padding: '8px' }}
      />
      <button
        onClick={handleSendEmail}
        style={{
          marginTop: '8px',
          padding: '10px 20px',
          background: '#0070f3',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
        }}
      >
        Send
      </button>
      <p>{status}</p>

      <hr style={{ margin: '30px 0' }} />

      {/* Email List */}
      <h2>📥 Received Emails</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {emails.map((email, index) => (
          <li
            key={index}
            style={{
              marginBottom: '10px',
              padding: '10px',
              border: '1px solid #ccc',
              background: selectedIndex === index ? '#f9f9f9' : 'white',
            }}
          >
            <div
              onClick={() =>
                setSelectedIndex(selectedIndex === index ? null : index)
              }
              style={{ cursor: 'pointer' }}
            >
              <p><strong>From:</strong> {email.from}</p>
              <p><strong>Subject:</strong> {email.subject}</p>
              <p><strong>Date:</strong> {email.date}</p>
            </div>

            {selectedIndex === index && (
              <div
                style={{
                  marginTop: '10px',
                  padding: '10px',
                  borderTop: '1px solid #aaa',
                  backgroundColor: '#fff',
                }}
              >
                <h4>📧 Full Message</h4>
                <div
                  dangerouslySetInnerHTML={{
                    __html:
                      email.html ||
                      `<pre>${email.text}</pre>` ||
                      '<p>No content</p>',
                  }}
                  style={{
                    padding: '10px',
                    border: '1px solid #eee',
                    borderRadius: '5px',
                    backgroundColor: '#f7f7f7',
                    whiteSpace: 'pre-wrap',
                  }}
                />
                <button
                  onClick={() => setSelectedIndex(null)}
                  style={{
                    marginTop: '10px',
                    padding: '5px 10px',
                    background: '#e53935',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer',
                  }}
                >
                  Close
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
