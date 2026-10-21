'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api/client';
import { PaginatedOrders } from '@/types/order';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { formatPersonName } from '@/types/call';
import {
  Search,
  Download,
  ArrowUpRight,
  ShoppingCart,
  CheckCircle2,
  Clock,
  XCircle,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  MapPin,
} from 'lucide-react';

export default function OrdersPage() {
  const [orders, setOrders] = useState<PaginatedOrders | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await apiClient.orders.list({ pageSize: '100' });
      setOrders(data);
      setError(null);
    } catch (err) {
      setError('Unable to load orders.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

  const handleExportCSV = () => {
    if (!orders?.data) return;
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      ['Date,Customer,Items,Status,CallId']
        .concat(
          orders.data.map(
            (o) =>
              `"${o.createdAt}","${o.customerName || 'Customer'}","${(o.items || [])
                .map((i) => `${i.quantity}x ${i.name}`)
                .join('; ')}","${o.status}","${o.callId}"`
          )
        )
        .join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'orders_export.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredOrders = (orders?.data || []).filter((order) => {
    const customer = (order.customerName || '').toLowerCase();
    const items = (order.items || []).map((i) => i.name.toLowerCase()).join(' ');
    const query = searchQuery.toLowerCase();
    return !query || customer.includes(query) || items.includes(query);
  });

  const totalOrders = orders?.data.length || 0;
  const confirmedCount = orders?.data.filter((o) => o.status === 'CONFIRMED').length || 0;
  const pendingCount = orders?.data.filter((o) => o.status === 'PENDING').length || 0;
  const cancelledCount = orders?.data.filter((o) => o.status === 'CANCELLED').length || 0;

  const totalPages = Math.ceil(filteredOrders.length / pageSize) || 1;
  const paginatedOrders = filteredOrders.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const startEntry = filteredOrders.length === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endEntry = Math.min(currentPage * pageSize, filteredOrders.length);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-6">
      {/* Top Header Row with Search & Buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Orders
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Voice orders captured and processed automatically by AI agent.
          </p>
        </div>

        {/* Search, Filter, Export Row */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
          <div className="relative min-w-[220px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              placeholder="Search customer, items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 bg-white rounded-lg border border-slate-200 text-xs text-slate-800 placeholder-slate-400 shadow-xs focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
          </div>

          <button
            onClick={fetchOrders}
            type="button"
            className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 text-xs font-semibold shadow-xs hover:bg-slate-50 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleExportCSV}
            type="button"
            className="inline-flex items-center justify-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-white" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Orders
            </p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{totalOrders}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <ShoppingCart className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Confirmed
            </p>
            <p className="text-2xl font-bold text-emerald-600 mt-1">{confirmedCount}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Pending
            </p>
            <p className="text-2xl font-bold text-amber-600 mt-1">{pendingCount}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Cancelled
            </p>
            <p className="text-2xl font-bold text-slate-700 mt-1">{cancelledCount}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center">
            <XCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {loading && !orders && <LoadingState message="Loading orders..." />}
      {error && !orders && <ErrorState message={error} onRetry={fetchOrders} />}

      {/* Main Orders Table */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200/80 font-bold uppercase tracking-wider text-[11px] text-slate-500">
                <th className="px-5 py-3">Order Details</th>
                <th className="px-5 py-3">Customer</th>
                <th className="px-5 py-3">Type</th>
                <th className="px-5 py-3">Items Summary</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedOrders.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-slate-400">
                    No orders captured yet.
                  </td>
                </tr>
              ) : (
                paginatedOrders.map((order) => {
                  const customerDisplay =
                    formatPersonName(order.customerName) || order.customerName || 'Customer';
                  const initial = customerDisplay.charAt(0).toUpperCase() || 'C';
                  const isConfirmed = order.status === 'CONFIRMED';
                  const isCancelled = order.status === 'CANCELLED';

                  return (
                    <tr key={order.id} className="hover:bg-slate-50/70 transition-colors">
                      {/* Order Details */}
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <p className="font-bold text-slate-900 font-mono">
                          #{order.id.slice(-6).toUpperCase()}
                        </p>
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          {new Date(order.createdAt).toLocaleDateString('en-GB', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                          })}
                        </p>
                      </td>

                      {/* Customer */}
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-xs flex-shrink-0">
                            {initial}
                          </div>
                          <div>
                            <p className="font-bold text-slate-900">{customerDisplay}</p>
                            {order.phone && (
                              <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                                {order.phone}
                              </p>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Type & Address */}
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            order.orderType?.toUpperCase() === 'DELIVERY'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-blue-50 text-blue-700 border border-blue-200'
                          }`}
                        >
                          {order.orderType || 'PICKUP'}
                        </span>
                        {order.address && (
                          <div className="flex items-center gap-1 text-[11px] text-slate-500 mt-1 max-w-[190px] truncate" title={order.address}>
                            <MapPin className="w-3 h-3 text-slate-400 flex-shrink-0" />
                            <span className="truncate">{order.address}</span>
                          </div>
                        )}
                      </td>

                      {/* Items */}
                      <td className="px-5 py-3.5 text-slate-700 max-w-xs">
                        {order.items && order.items.length > 0 ? (
                          <div className="flex flex-wrap gap-1.5">
                            {order.items.map((item, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-0.5 rounded-md bg-slate-100 text-slate-800 text-[11px] font-medium"
                              >
                                {item.quantity}x {item.name}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-slate-400 italic text-[11px]">Order In Progress</span>
                        )}
                      </td>

                      {/* Status */}
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                            isConfirmed
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                              : isCancelled
                              ? 'bg-red-50 text-red-600 border-red-200'
                              : 'bg-blue-50 text-blue-700 border border-blue-200'
                          }`}
                        >
                          {order.status || 'PENDING'}
                        </span>
                      </td>

                      {/* Call Link */}
                      <td className="px-5 py-3.5 whitespace-nowrap text-right">
                        <Link
                          href={`/calls/${order.callId}`}
                          className="inline-flex items-center gap-1 font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                        >
                          <span>View Call</span>
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Table Footer with Pagination when > 10 orders */}
        {filteredOrders.length > pageSize ? (
          <div className="px-5 py-3.5 bg-slate-50/70 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
            <div>
              Showing <span className="font-semibold text-slate-800">{startEntry}</span> to{' '}
              <span className="font-semibold text-slate-800">{endEntry}</span> of{' '}
              <span className="font-semibold text-slate-800">{filteredOrders.length}</span> orders
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                disabled={currentPage === 1}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-200 bg-white font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-2xs"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Prev</span>
              </button>

              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                  <button
                    key={p}
                    onClick={() => setCurrentPage(p)}
                    className={`w-7 h-7 rounded-lg text-xs font-bold transition-colors ${
                      p === currentPage
                        ? 'bg-blue-600 text-white shadow-2xs'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>

              <button
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                disabled={currentPage >= totalPages}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-200 bg-white font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-2xs"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ) : (
          <div className="px-5 py-3 bg-slate-50/70 border-t border-slate-100 text-xs text-slate-500">
            Showing <span className="font-semibold text-slate-800">{filteredOrders.length}</span> of{' '}
            <span className="font-semibold text-slate-800">{totalOrders}</span> orders
          </div>
        )}
      </div>
    </div>
  );
}
