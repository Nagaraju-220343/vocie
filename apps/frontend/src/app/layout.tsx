import type { Metadata } from 'next';
import { Suspense } from 'react';
import { Inter } from 'next/font/google';
import './globals.css';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Le Gourmet Voice Assistant',
  description: 'Operations dashboard for Le Gourmet bilingual voice agent',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} h-screen bg-slate-50 overflow-hidden flex`}>
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Suspense fallback={<div className="h-16 border-b border-slate-200" />}>
            <Header />
          </Suspense>
          <main className="flex-1 overflow-y-auto bg-slate-50 p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
