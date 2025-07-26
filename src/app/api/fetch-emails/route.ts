import { NextResponse } from 'next/server';
import Imap from 'imap';
import { simpleParser } from 'mailparser';

export async function GET() {
  const imapConfig = {
    user: 'contact@nkmdigital.com',
    password: 'Nil@!123#',
    host: 'imap.hostinger.com',
    port: 993,
    tls: true,
  };

  const fetchEmails = (): Promise<any[]> =>
    new Promise((resolve, reject) => {
      const imap = new Imap(imapConfig);
      const emails: any[] = [];

      function openInbox(cb: any) {
        imap.openBox('INBOX', true, cb);
      }

      imap.once('ready', () => {
        openInbox((err: any, box: any) => {
          if (err) return reject(err);

          const fetch = imap.seq.fetch(`${box.messages.total}:*`, {
            bodies: '',
            struct: true,
          });
fetch.on('message', (msg: any) => {
  msg.on('body', (stream: any) => {
    simpleParser(stream, (err: any, parsed: any) => {
      if (!err && parsed) {
        emails.push({
          subject: parsed.subject,
          from: parsed.from.text,
          date: parsed.date,
          body: parsed.text,
                  });
                }
              });
            });
          });

          fetch.once('end', () => {
            imap.end();
          });
        });
      });

      imap.once('error', (err: any) => reject(err));
      imap.once('end', () => resolve(emails));
      imap.connect();
    });

  try {
    const emails = await fetchEmails();
    return NextResponse.json({ emails });
  } catch (error) {
    console.error('Fetch email error:', error);
    return NextResponse.json({ error: 'Failed to fetch emails' }, { status: 500 });
  }
}