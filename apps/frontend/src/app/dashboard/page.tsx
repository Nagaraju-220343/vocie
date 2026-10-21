'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api/client';
import { useRealtime } from '@/hooks/use-realtime';
import { PaginatedCalls, getCallerDisplayName, formatPersonName } from '@/types/call';
import { PaginatedOrders } from '@/types/order';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import {
  PhoneCall,
  PhoneForwarded,
  ShoppingCart,
  AlertCircle,
  RefreshCw,
  ChevronRight,
  Clock,
} from 'lucide-react';

export default function DashboardPage() {
  const [calls, setCalls] = useState<PaginatedCalls | null>(null);
  const [orders, setOrders] = useState<PaginatedOrders | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { useEvent } = useRealtime('restaurant:live-calls');

  useEvent('call.started', () => fetchData());
  useEvent('call.ended', () => fetchData());
  useEvent('order.updated', () => fetchData());

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [callsData, ordersData] = await Promise.all([
        apiClient.calls.list({ pageSize: '5' }),
        apiClient.orders.list({ pageSize: '5' }),
      ]);
      setCalls(callsData);
      setOrders(ordersData);
    } catch (err) {
      setError('Unable to load dashboard data. Check that backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const totalCallsCount = calls?.pagination.total ?? 0;
  const activeCalls = calls?.data.filter((c) => c.status === 'IN_PROGRESS').length || 0;
  const confirmedOrders = orders?.data.filter((o) => o.status === 'CONFIRMED').length || 0;
  const escalationsCount = calls?.data.filter((c) => c.escalated).length || 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Dashboard
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time operations overview for voice agent calls and orders.
          </p>
        </div>

        <button
          onClick={fetchData}
          type="button"
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 text-xs font-semibold shadow-xs hover:bg-slate-50 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
          <span>Sync Data</span>
        </button>
      </div>

      {loading && !calls && <LoadingState message="Loading dashboard..." />}
      {error && !calls && <ErrorState message={error} onRetry={fetchData} />}

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Calls */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Calls
            </p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{totalCallsCount}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <PhoneCall className="w-5 h-5" />
          </div>
        </div>

        {/* Active Calls */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Active Calls
            </p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{activeCalls}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <PhoneForwarded className="w-5 h-5" />
          </div>
        </div>

        {/* Orders Taken */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Orders Taken
            </p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{confirmedOrders}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <ShoppingCart className="w-5 h-5" />
          </div>
        </div>

        {/* Escalations */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Escalations
            </p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{escalationsCount}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-red-50 text-red-500 flex items-center justify-center">
            <AlertCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* 2 Column Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Calls */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs flex flex-col overflow-hidden">
          <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Recent Calls</h2>
            <Link
              href="/calls"
              className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-0.5"
            >
              <span>View all</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-100 flex-1">
            {(!calls?.data || calls.data.length === 0) ? (
              <div className="p-8 text-center text-xs text-slate-400">No calls logged yet</div>
            ) : (
              calls.data.slice(0, 5).map((call) => {
                const displayName = getCallerDisplayName(call);
                const initial = displayName.charAt(0).toUpperCase() || 'C';
                const intent = call.intent || 'Unknown';
                const isCompleted = call.status === 'COMPLETED';

                return (
                  <Link
                    key={call.id}
                    href={`/calls/${call.id}`}
                    className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs flex-shrink-0">
                        {initial}
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                          {displayName}
                        </p>
                        <p className="text-[11px] text-slate-500 mt-0.5">
                          Intent: {intent}
                        </p>
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                        isCompleted
                          ? 'bg-slate-100 text-slate-600 border border-slate-200'
                          : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      }`}
                    >
                      {call.status}
                    </span>
                  </Link>
                );
              })
            )}
          </div>
        </div>

        {/* Recent Orders */}
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs flex flex-col overflow-hidden">
          <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Recent Orders</h2>
            <Link
              href="/orders"
              className="text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-0.5"
            >
              <span>View all</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-100 flex-1">
            {(!orders?.data || orders.data.length === 0) ? (
              <div className="p-8 text-center text-xs text-slate-400">No orders captured yet</div>
            ) : (
              orders.data.slice(0, 5).map((order) => {
                const customerDisplay =
                  formatPersonName(order.customerName) || order.customerName || 'Customer';
                const initial = customerDisplay.charAt(0).toUpperCase() || 'C';
                const itemsSummary =
                  order.items && order.items.length > 0
                    ? order.items.map((i) => `${i.quantity}x ${i.name}`).join(', ')
                    : 'Order In Progress';
                const isConfirmed = order.status === 'CONFIRMED';
                const isCancelled = order.status === 'CANCELLED';

                return (
                  <div
                    key={order.id}
                    className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs flex-shrink-0">
                        {initial}
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900">{customerDisplay}</p>
                        <p className="text-[11px] text-slate-500 mt-0.5 truncate max-w-[200px] sm:max-w-xs">
                          {itemsSummary}
                        </p>
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                        isConfirmed
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : isCancelled
                          ? 'bg-red-50 text-red-600 border border-red-200'
                          : 'bg-blue-50 text-blue-700 border border-blue-200'
                      }`}
                    >
                      {order.status || 'PENDING'}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


