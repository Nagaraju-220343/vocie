'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { useRealtime } from '@/hooks/use-realtime';
import { Call, PaginatedCalls } from '@/types/call';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import { PhoneCall } from 'lucide-react';
import { StatusBadge } from '@/components/ui/StatusBadge';
import Link from 'next/link';

export default function LiveCallsPage() {
  const [activeCalls, setActiveCalls] = useState<Call[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { useEvent } = useRealtime('restaurant:live-calls');

  const fetchActiveCalls = async () => {
    try {
      const response = await apiClient.calls.list({ status: 'IN_PROGRESS' });
      setActiveCalls(response.data);
      setError(null);
    } catch (err) {
      setError('Unable to load active calls. Check that the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveCalls();
  }, []);

  useEvent('call.started', (event) => {
    // Refresh to get full call details
    fetchActiveCalls();
  });

  useEvent('call.ended', (event) => {
    setActiveCalls((prev) => prev.filter((c) => c.id !== event.callId));
  });

  useEvent('call.escalated', (event) => {
    setActiveCalls((prev) => prev.map((c) => {
      if (c.id === event.callId) {
        return { ...c, escalated: true, escalationReason: event.payload.reason };
      }
      return c;
    }));
  });

  useEvent('call.intent.updated', (event) => {
    setActiveCalls((prev) => prev.map((c) => {
      if (c.id === event.callId) {
        return { ...c, intent: event.payload.intent, language: event.payload.language || c.language };
      }
      return c;
    }));
  });

  if (loading && activeCalls.length === 0) return <LoadingState message="Checking for active calls..." />;
  if (error && activeCalls.length === 0) return <ErrorState message={error} onRetry={fetchActiveCalls} />;

  if (activeCalls.length === 0) {
    return (
      <EmptyState
        icon={<PhoneCall className="w-12 h-12" />}
        title="No active calls"
        description="Live calls will appear here when customers connect."
      />
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Active Calls ({activeCalls.length})</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {activeCalls.map((call) => (
          <div key={call.id} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:border-slate-300 transition-colors">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-2">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                  </span>
                  <span className="text-sm font-bold text-green-600 tracking-wider">LIVE</span>
                </div>
                <div className="text-sm font-medium text-slate-500">
                  {/* Format duration roughly */}
                  {Math.floor(call.durationSeconds / 60)}:{(call.durationSeconds % 60).toString().padStart(2, '0')}
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-xl font-bold text-slate-900">{call.fromNumber}</h3>
                {call.language && (
                  <p className="text-sm text-slate-500 mt-1 flex items-center gap-1">
                    Language: <span className="font-medium text-slate-700">{call.language}</span>
                  </p>
                )}
              </div>

              <div className="flex items-center space-x-3 mb-6">
                <StatusBadge status={call.intent || 'UNKNOWN'} type="call" />
                {call.escalated && (
                  <StatusBadge status="ESCALATED" type="call" />
                )}
              </div>

              <Link
                href={`/calls/${call.id}`}
                className="block w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium text-center rounded-lg transition-colors"
              >
                Open Live Call →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
