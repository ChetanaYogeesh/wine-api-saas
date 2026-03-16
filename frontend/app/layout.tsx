import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Wine API - Wine Data as a Service',
  description: 'Access the worlds largest wine database with our easy-to-use API',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
