import Link from 'next/link';
import {
  LayoutDashboard,
  PhoneCall,
  History,
  ShoppingCart,
  Users,
  BookOpen,
  Settings,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Live Calls', href: '/live-calls', icon: PhoneCall },
  { name: 'Call History', href: '/calls', icon: History },
  { name: 'Orders', href: '/orders', icon: ShoppingCart },
  { name: 'Customers', href: '/customers', icon: Users },
  { name: 'Knowledge', href: '/knowledge', icon: BookOpen },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  return (
    <div className="flex h-full w-64 flex-col bg-slate-900 text-slate-300">
      <div className="flex h-16 shrink-0 items-center px-6 bg-slate-950">
        <h1 className="text-xl font-bold text-white tracking-wide">
          Le Gourmet
          <span className="block text-xs font-normal text-slate-400 mt-1">
            Voice Assistant
          </span>
        </h1>
      </div>
      <div className="flex flex-1 flex-col overflow-y-auto">
        <nav className="flex-1 space-y-1 px-4 py-6">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className="group flex items-center px-2 py-2 text-sm font-medium rounded-md hover:bg-slate-800 hover:text-white"
              >
                <Icon
                  className="mr-3 h-5 w-5 flex-shrink-0 text-slate-400 group-hover:text-white"
                  aria-hidden="true"
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
