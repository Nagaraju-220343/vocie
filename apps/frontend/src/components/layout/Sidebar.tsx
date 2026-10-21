'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  History,
  ShoppingCart,
  Users,
  BookOpen,
  Settings,
} from 'lucide-react';

export function Sidebar() {
  const pathname = usePathname();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, active: pathname === '/dashboard' || pathname === '/' },
    { name: 'Call History', href: '/calls', icon: History, active: pathname.startsWith('/calls') },
    { name: 'Orders', href: '/orders', icon: ShoppingCart, active: pathname.startsWith('/orders') },
    { name: 'Customers', href: '/customers', icon: Users, active: pathname.startsWith('/customers') },
    // { name: 'Knowledge', href: '/knowledge', icon: BookOpen, active: pathname.startsWith('/knowledge') },
    // { name: 'Settings', href: '/settings', icon: Settings, active: pathname.startsWith('/settings') },
  ];

  return (
    <aside className="flex h-full w-56 flex-col bg-[#1e222d] text-slate-300 border-r border-[#262c3b] flex-shrink-0 select-none">
      {/* Brand */}
      <div className="flex h-16 shrink-0 flex-col justify-center px-5 border-b border-white/5">
        <h1 className="text-base font-bold text-white tracking-wide">
          Dominos Le Chesnay
          <span className="block text-xs font-normal text-slate-400 mt-0.5">
            Voice Assistant
          </span>
        </h1>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3.5 py-2.5 text-xs font-semibold rounded-lg transition-all ${item.active
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                }`}
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
