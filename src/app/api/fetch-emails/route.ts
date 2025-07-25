import { NextRequest, NextResponse } from 'next/server';
import Imap from 'imap';
import { simpleParser } from 'mailparser';

export async function GET(req: NextRequest) {
  return new Promise((resolve) => {
    const imap = new Imap({
      user: 'contact@nkmdigital.com',
      password: 'Nil@!123#',
      host: 'imap.hostinger.com',
      port: 993,
      tls: true,
    });

    function openInbox(cb: any) {
      imap.openBox('INBOX', true, cb);
    }

    imap.once('ready', function () {
      openInbox(function (err: any, box: any) {
        if (err) throw err;

        // Fetch latest 500 emails
        const start = Math.max(box.messages.total - 499, 1);
        const fetch = imap.seq.fetch(`${start}:${box.messages.total}`, {
          bodies: '',
          struct: true,
        });

        const emails: any[] = [];
        let pending = 0;

        fetch.on('message', function (msg: any, seqno: any) {
          pending++;
          msg.on('body', function (stream: any, info: any) {
            simpleParser(stream, (err, parsed) => {
              if (err) {
                console.error('Parse error:', err);
                pending--;
                return;
              }

              emails.push({
                from: parsed.from?.text || '',
                to: parsed.to?.text || '',
                cc: parsed.cc?.text || '',
                bcc: parsed.bcc?.text || '',
                subject: parsed.subject || '',
                date: parsed.date?.toString() || '',
                text: parsed.text || '',
                html: parsed.html || '',
                attachments: parsed.attachments || [],
                headers: parsed.headers || {},
              });

              pending--;
              if (pending === 0) {
                imap.end();
                emails.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
                resolve(NextResponse.json({ emails }));
              }
            });
          });
        });

        fetch.once('error', function (err: any) {
          console.error('Fetch error:', err);
          imap.end();
          resolve(NextResponse.json({ emails: [], error: 'Fetch failed' }));
        });

        fetch.once('end', function () {
          if (pending === 0) {
            imap.end();
            emails.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
            resolve(NextResponse.json({ emails }));
          }
        });
      });
    });

    imap.once('error', function (err) {
      console.error(err);
      resolve(NextResponse.json({ emails: [], error: 'Connection failed' }));
    });

    imap.connect();
  });
}
