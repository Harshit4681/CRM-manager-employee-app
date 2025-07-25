import { NextResponse } from 'next/server';
import nodemailer from 'nodemailer';

export async function POST(req: Request) {
  try {
    const { to, subject, text, cc, bcc } = await req.json();

    const transporter = nodemailer.createTransport({
      host: 'smtp.hostinger.com',
      port: 465,
      secure: true,
      auth: {
        user: 'contact@nkmdigital.com',
        pass: 'Nil@!123#',
      },
    });

    const mailOptions = {
      from: 'contact@nkmdigital.com',
      to,
      cc,
      bcc,
      subject,
      text,
    };

    await transporter.sendMail(mailOptions);
    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
