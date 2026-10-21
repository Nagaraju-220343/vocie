'use client';

import { usePathname } from 'next/navigation';

export function Header() {
  const pathname = usePathname();

  const getPageTitle = () => {
    if (pathname.startsWith('/calls')) return 'Call History';
    if (pathname.startsWith('/orders')) return 'Orders';
    if (pathname.startsWith('/customers')) return 'Customers';
    if (pathname.startsWith('/knowledge')) return 'Knowledge Base';
    if (pathname.startsWith('/settings')) return 'Settings';
    return 'Dashboard';
  };

  return (
    <header className="bg-white h-14 shrink-0 flex items-center justify-between px-6 border-b border-slate-200 select-none">
      <div className="flex items-center">
        <h2 className="text-base font-bold text-slate-900 tracking-tight">{getPageTitle()}</h2>
      </div>

      <div className="flex items-center space-x-3">
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-700 text-xs font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
          <span>API Connected</span>
        </div>
      </div>
    </header>
  );
}
