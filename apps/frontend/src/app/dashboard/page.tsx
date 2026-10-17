'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { useRealtime } from '@/hooks/use-realtime';
import { PaginatedCalls, getCallerDisplayName, formatPersonName } from '@/types/call';
import { PaginatedOrders } from '@/types/order';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { PhoneCall, ShoppingCart, AlertCircle, PhoneForwarded } from 'lucide-react';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { WebVoiceCallCard } from '@/components/voice/WebVoiceCallCard';
import Link from 'next/link';

export default function DashboardPage() {
  const [calls, setCalls] = useState<PaginatedCalls | null>(null);
  const [orders, setOrders] = useState<PaginatedOrders | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { useEvent } = useRealtime('restaurant:live-calls');

  useEvent('call.started', () => {
    fetchData();
  });

  useEvent('call.ended', () => {
    fetchData();
  });

  useEvent('order.updated', () => {
    fetchData();
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [callsData, ordersData] = await Promise.all([
        apiClient.calls.list({ pageSize: '5' }),
        apiClient.orders.list({ pageSize: '5' })
      ]);
      setCalls(callsData);
      setOrders(ordersData);
    } catch (err) {
      setError('Unable to load dashboard data. Check that the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const activeCalls = calls?.data.filter(c => c.status === 'IN_PROGRESS').length || 0;
  const escalatedCalls = calls?.data.filter(c => c.escalated).length || 0;
  const confirmedOrdersCount = orders?.data.filter(o => o.status === 'CONFIRMED').length || 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Talk to Le Gourmet - Web Voice Call Interface */}
      <WebVoiceCallCard onCallStarted={fetchData} onCallEnded={fetchData} />

      {loading && <LoadingState message="Loading dashboard..." />}
      {error && !loading && <ErrorState message={error} onRetry={fetchData} />}

      {!loading && !error && (
        <>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Metric Cards */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center">
            <div className="bg-blue-50 rounded-lg p-3">
              <PhoneCall className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-slate-500">Total Calls</h3>
              <p className="text-2xl font-semibold text-slate-900">{calls?.pagination.total || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center">
            <div className="bg-amber-50 rounded-lg p-3">
              <PhoneForwarded className="h-6 w-6 text-amber-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-slate-500">Active Calls</h3>
              <p className="text-2xl font-semibold text-slate-900">{activeCalls}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center">
            <div className="bg-green-50 rounded-lg p-3">
              <ShoppingCart className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-slate-500">Orders Taken</h3>
              <p className="text-2xl font-semibold text-slate-900">{confirmedOrdersCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center">
            <div className="bg-red-50 rounded-lg p-3">
              <AlertCircle className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-slate-500">Escalations</h3>
              <p className="text-2xl font-semibold text-slate-900">{escalatedCalls}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow-sm rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 className="font-semibold text-slate-800">Recent Calls</h3>
            <Link href="/calls" className="text-sm font-medium text-blue-600 hover:text-blue-800">View all</Link>
          </div>
          <div className="divide-y divide-slate-100">
            {calls?.data.length === 0 ? (
              <div className="p-6 text-center text-sm text-slate-500">No calls yet.</div>
            ) : (
              calls?.data.map((call) => (
                <Link key={call.id} href={`/calls/${call.id}`} className="block hover:bg-slate-50 transition-colors">
                  <div className="px-6 py-4 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-900">{getCallerDisplayName(call)}</p>
                      <p className="text-xs text-slate-500 mt-1">Intent: {call.intent || 'Unknown'}</p>
                    </div>
                    <StatusBadge status={call.status} />
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        <div className="bg-white shadow-sm rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 className="font-semibold text-slate-800">Recent Orders</h3>
            <Link href="/orders" className="text-sm font-medium text-blue-600 hover:text-blue-800">View all</Link>
          </div>
          <div className="divide-y divide-slate-100">
            {orders?.data.length === 0 ? (
              <div className="p-6 text-center text-sm text-slate-500">No orders yet.</div>
            ) : (
              orders?.data.map((order) => {
                const customerDisplay = formatPersonName(order.customerName) || order.customerName || 'Customer';
                const itemsSummary = order.items && order.items.length > 0
                  ? order.items.map(i => `${i.quantity}x ${i.name}`).join(', ')
                  : (order.orderType && order.orderType !== 'UNKNOWN' ? `${order.orderType.toUpperCase()} order` : 'Order In Progress');
                return (
                  <div key={order.id} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                    <div>
                      <p className="text-sm font-medium text-slate-900">{customerDisplay}</p>
                      <p className="text-xs text-slate-500 mt-1">{itemsSummary}</p>
                    </div>
                    <StatusBadge status={order.status} />
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </>
  )}
</div>
  );
}
