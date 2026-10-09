'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { PaginatedCalls } from '@/types/call';
import { PaginatedOrders } from '@/types/order';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { PhoneCall, ShoppingCart, AlertCircle, PhoneForwarded } from 'lucide-react';
import { StatusBadge } from '@/components/ui/StatusBadge';
import Link from 'next/link';

export default function DashboardPage() {
  const [calls, setCalls] = useState<PaginatedCalls | null>(null);
  const [orders, setOrders] = useState<PaginatedOrders | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  if (loading) return <LoadingState message="Loading dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const activeCalls = calls?.data.filter(c => c.status === 'IN_PROGRESS').length || 0;
  const escalatedCalls = calls?.data.filter(c => c.escalated).length || 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
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
              <p className="text-2xl font-semibold text-slate-900">{orders?.pagination.total || 0}</p>
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
                      <p className="text-sm font-medium text-slate-900">{call.fromNumber}</p>
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
              orders?.data.map((order) => (
                <div key={order.id} className="px-6 py-4 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-900">{order.customerName || 'Unknown Customer'}</p>
                    <p className="text-xs text-slate-500 mt-1">{order.items.length} items</p>
                  </div>
                  <StatusBadge status={order.status} />
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
