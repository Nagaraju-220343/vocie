import type { Metadata } from 'next';
import { Suspense } from 'react';
import { Inter } from 'next/font/google';
import './globals.css';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: "Dominos Le Chesnay — Voice Assistant",
  description: "Voice Assistant operations dashboard for real-time calls and orders",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} h-screen bg-[#f8fafc] text-slate-900 overflow-hidden flex antialiased`}>
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden min-w-0">
          <Suspense fallback={<div className="h-14 border-b border-slate-200 bg-white" />}>
            <Header />
          </Suspense>
          <main className="flex-1 overflow-y-auto bg-[#f8fafc] p-6 md:p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

