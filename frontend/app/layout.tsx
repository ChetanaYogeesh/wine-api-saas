import type { Metadata } from 'next';
import ClientLayout from './components/ClientLayout';

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
      <body>
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
