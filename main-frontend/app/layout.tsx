import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '../index.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Ugunja - LPG Delivery & Fleet Management',
  description: 'Modern LPG delivery and fleet management platform with real-time tracking and role-based access.',
  keywords: ['LPG delivery', 'fleet management', 'logistics', 'tracking', 'energy'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div className="min-h-screen bg-background text-foreground">
          {children}
        </div>
      </body>
    </html>
  );
}