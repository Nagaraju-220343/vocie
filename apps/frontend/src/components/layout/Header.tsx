'use client';

import { usePathname } from 'next/navigation';

export function Header() {
  const pathname = usePathname();
  
  const getPageTitle = () => {
    if (pathname.startsWith('/live-calls')) return 'Live Calls';
    if (pathname.startsWith('/calls')) return 'Call History';
    if (pathname.startsWith('/orders')) return 'Orders';
    if (pathname.startsWith('/customers')) return 'Customers';
    if (pathname.startsWith('/knowledge')) return 'Knowledge Base';
    if (pathname.startsWith('/settings')) return 'Settings';
    return 'Dashboard';
  };

  return (
    <header className="bg-white shadow-sm h-16 flex items-center justify-between px-6 border-b border-slate-200">
      <div className="flex items-center space-x-4">
        <h2 className="text-lg font-semibold text-slate-800">{getPageTitle()}</h2>
      </div>
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-sm font-medium">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
          </span>
          <span className="text-slate-600">API Connected</span>
        </div>
      </div>
    </header>
  );
}
