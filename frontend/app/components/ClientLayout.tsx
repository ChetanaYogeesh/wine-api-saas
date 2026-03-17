'use client';

import '../globals.css';
import Chatbot from './Chatbot';

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      {children}
      <Chatbot />
    </>
  );
}
