'use client';

import { useRealtime } from '@/hooks/use-realtime';
import { Store, Globe, Server, Activity, UtensilsCrossed } from 'lucide-react';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';

export default function SettingsPage() {
  const { isConnected } = useRealtime();
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    apiClient.faqs
      .list({ limit: '1' })
      .then(() => setBackendStatus('online'))
      .catch(() => setBackendStatus('offline'));
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Settings & Operations</h1>
        <p className="text-xs text-slate-500 mt-1">System configuration and operational status.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Restaurant Details */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
          <div className="border-b border-slate-100 bg-slate-50/50 px-5 py-3.5 flex items-center gap-2">
            <Store className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">Restaurant Details</h2>
          </div>
          <div className="p-5 space-y-3.5 text-xs">
            <div>
              <p className="text-slate-400 font-semibold uppercase text-[11px] mb-0.5">Name</p>
              <p className="font-bold text-slate-900 text-sm">Dominos Le Chesnay</p>
            </div>
            <div>
              <p className="text-slate-400 font-semibold uppercase text-[11px] mb-0.5">Address</p>
              <p className="font-medium text-slate-700">12 Rue de Paris, 75001 Paris</p>
            </div>
            <div>
              <p className="text-slate-400 font-semibold uppercase text-[11px] mb-1">Supported Languages</p>
              <div className="flex gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-[11px] font-semibold">
                  French
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-semibold">
                  English
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
          <div className="border-b border-slate-100 bg-slate-50/50 px-5 py-3.5 flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">System Status</h2>
          </div>
          <div className="p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Server className="w-4 h-4 text-slate-400" />
                <div>
                  <p className="text-xs font-bold text-slate-900">Backend API</p>
                  <p className="text-[11px] text-slate-500">FastAPI REST Services</p>
                </div>
              </div>
              <div>
                {backendStatus === 'checking' && (
                  <span className="text-xs text-slate-400">Checking...</span>
                )}
                {backendStatus === 'online' && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    Online
                  </span>
                )}
                {backendStatus === 'offline' && (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-50 text-red-700 border border-red-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                    Offline
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Globe className="w-4 h-4 text-slate-400" />
                <div>
                  <p className="text-xs font-bold text-slate-900">Realtime Engine</p>
                  <p className="text-[11px] text-slate-500">Socket.IO Live Events</p>
                </div>
              </div>
              <div>
                {isConnected ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    Connected
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                    Disconnected
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Voice-Extractable Menu Items */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="border-b border-slate-100 bg-slate-50/50 px-5 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UtensilsCrossed className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">Voice-Extractable Menu Items</h2>
          </div>
          <span className="text-[11px] px-2.5 py-0.5 bg-emerald-50 text-emerald-700 font-semibold rounded-full border border-emerald-200">
            Active in Voice AI
          </span>
        </div>
        <div className="p-5">
          <p className="text-xs text-slate-500 mb-4 leading-relaxed">
            The Retell voice assistant and order extraction pipeline are configured to recognize and extract the following menu items:
          </p>
          <div className="divide-y divide-slate-100 border border-slate-200/70 rounded-lg overflow-hidden">
            <div className="p-4 flex items-center justify-between hover:bg-slate-50/70 transition-colors">
              <div>
                <p className="text-xs font-bold text-slate-900">Dominos Le Chesnay Classic Burger</p>
                <p className="text-[11px] text-slate-500 mt-0.5">Keywords: burger, burgers (FR & EN quantities supported)</p>
              </div>
              <span className="text-xs font-bold text-slate-900">€14.50</span>
            </div>
            <div className="p-4 flex items-center justify-between hover:bg-slate-50/70 transition-colors">
              <div>
                <p className="text-xs font-bold text-slate-900">Pizza Margherita</p>
                <p className="text-[11px] text-slate-500 mt-0.5">Keywords: pizza, pizzas, margherita</p>
              </div>
              <span className="text-xs font-bold text-slate-900">€12.00</span>
            </div>
            <div className="p-4 flex items-center justify-between hover:bg-slate-50/70 transition-colors">
              <div>
                <p className="text-xs font-bold text-slate-900">Salade Fraîcheur</p>
                <p className="text-[11px] text-slate-500 mt-0.5">Keywords: salade, salad, salades</p>
              </div>
              <span className="text-xs font-bold text-slate-900">€9.50</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
