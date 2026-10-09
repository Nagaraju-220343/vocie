'use client';

import { useRealtime } from '@/hooks/use-realtime';
import { Store, Globe, Server, Activity } from 'lucide-react';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';

export default function SettingsPage() {
  const { isConnected } = useRealtime();
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    // A simple check using a known endpoint (like faqs or calls) to verify backend REST connectivity
    apiClient.faqs.list({ limit: '1' })
      .then(() => setBackendStatus('online'))
      .catch(() => setBackendStatus('offline'));
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Settings & Operations</h1>
        <p className="text-slate-600 mt-1">System configuration and operational status.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="border-b border-slate-100 bg-slate-50/50 p-4 flex items-center gap-2">
            <Store className="w-5 h-5 text-slate-500" />
            <h2 className="font-semibold text-slate-900">Restaurant Details</h2>
          </div>
          <div className="p-6 space-y-4 text-sm">
            <div>
              <p className="text-slate-500 mb-1">Name</p>
              <p className="font-medium text-slate-900">Le Gourmet</p>
            </div>
            <div>
              <p className="text-slate-500 mb-1">Address</p>
              <p className="font-medium text-slate-900">12 Rue de Paris, 75001 Paris</p>
            </div>
            <div>
              <p className="text-slate-500 mb-1">Supported Languages</p>
              <div className="flex gap-2 mt-1">
                <span className="px-2 py-1 rounded bg-blue-50 text-blue-700 text-xs font-medium">French</span>
                <span className="px-2 py-1 rounded bg-blue-50 text-blue-700 text-xs font-medium">English</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="border-b border-slate-100 bg-slate-50/50 p-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-slate-500" />
            <h2 className="font-semibold text-slate-900">System Status</h2>
          </div>
          <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Server className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-sm font-medium text-slate-900">Backend API</p>
                  <p className="text-xs text-slate-500">FastAPI REST Services</p>
                </div>
              </div>
              <div>
                {backendStatus === 'checking' && <span className="text-xs text-slate-400">Checking...</span>}
                {backendStatus === 'online' && <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700"><span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>Online</span>}
                {backendStatus === 'offline' && <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700"><span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>Offline</span>}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Globe className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-sm font-medium text-slate-900">Realtime Engine</p>
                  <p className="text-xs text-slate-500">Socket.IO Live Events</p>
                </div>
              </div>
              <div>
                {isConnected ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                    Connected
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                    Disconnected
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
