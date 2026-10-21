'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiClient } from '@/lib/api/client';
import { PaginatedCalls, getCallerDisplayName } from '@/types/call';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import {
  Search,
  Download,
  PhoneIncoming,
  ChevronRight,
  ChevronLeft,
  RefreshCw,
  PhoneCall,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

export default function CallsPage() {
  const [calls, setCalls] = useState<PaginatedCalls | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'orders'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const fetchCalls = async () => {
    try {
      setLoading(true);
      const data = await apiClient.calls.list({ pageSize: '100' });
      setCalls(data);
      setError(null);
    } catch (err) {
      setError('Unable to load calls.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCalls();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, filterType]);

  const handleExportCSV = async () => {
    try {
      setExporting(true);
      const params = new URLSearchParams();
      if (filterType === 'orders') {
        params.append('intent', 'ORDER');
      }
      const query = params.toString();

      let response: Response | null = null;

      // 1. Try local FastAPI backend directly if on localhost
      if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
        try {
          const localRes = await fetch(`http://localhost:8000/api/calls/export${query ? `?${query}` : ''}`);
          if (localRes.ok) {
            response = localRes;
          }
        } catch {
          // Local direct fetch failed or CORS blocked; try Next.js proxy
        }
      }

      // 2. Try proxied /api/calls/export
      if (!response) {
        try {
          const proxyRes = await fetch(`/api/calls/export${query ? `?${query}` : ''}`, {
            headers: { 'ngrok-skip-browser-warning': 'true' },
          });
          if (proxyRes.ok) {
            response = proxyRes;
          }
        } catch {
          // Proxy failed
        }
      }

      if (response && response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'call_history.csv');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        return;
      }

      // 3. Fallback: generate CSV client-side from loaded calls if backend export route is not reached
      if (calls?.data) {
        const csvContent =
          'data:text/csv;charset=utf-8,' +
          ['Call ID,Date,Caller / Customer,Phone Number,Intent,Duration (Seconds),Status']
            .concat(
              calls.data.map(
                (c) =>
                  `"${c.id}","${c.createdAt}","${getCallerDisplayName(c)}","${c.fromNumber || ''}","${
                    c.intent || 'UNKNOWN'
                  }","${c.durationSeconds}","${c.status}"`
              )
            )
            .join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'call_history.csv');
        document.body.appendChild(link);
        link.click();
        link.remove();
      }
    } catch (err) {
      console.error('Export CSV error:', err);
    } finally {
      setExporting(false);
    }
  };

  const filteredCalls = (calls?.data || []).filter((call) => {
    const name = getCallerDisplayName(call).toLowerCase();
    const phone = (call.fromNumber || '').toLowerCase();
    const id = call.id.toLowerCase();
    const query = searchQuery.toLowerCase();
    const matchesQuery = !query || name.includes(query) || phone.includes(query) || id.includes(query);

    if (!matchesQuery) return false;
    if (filterType === 'orders') return (call.intent || '').toUpperCase().includes('ORDER');
    return true;
  });

  const totalCalls = calls?.pagination.total ?? calls?.data.length ?? 0;
  const orderIntents = calls?.data.filter((c) => (c.intent || '').toUpperCase().includes('ORDER')).length || 0;
  const escalatedCalls = calls?.data.filter((c) => c.escalated).length || 0;

  const totalPages = Math.ceil(filteredCalls.length / pageSize) || 1;
  const paginatedCalls = filteredCalls.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const startEntry = filteredCalls.length === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endEntry = Math.min(currentPage * pageSize, filteredCalls.length);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-6">
      {/* Top Header Row with Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Call History
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Historical logs of incoming calls, detected intents, and conversations.
          </p>
        </div>

        {/* 3 Real Summary KPI Cards */}
        <div className="flex items-center gap-3">
          <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs px-4 py-2 min-w-[100px]">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">TOTAL CALLS</p>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{totalCalls}</p>
          </div>
          <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs px-4 py-2 min-w-[100px]">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">ORDER INTENT</p>
            <p className="text-lg font-bold text-blue-600 mt-0.5">{orderIntents}</p>
          </div>
          <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs px-4 py-2 min-w-[100px]">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">ESCALATED</p>
            <p className="text-lg font-bold text-red-600 mt-0.5">{escalatedCalls}</p>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            placeholder="Search by customer, phone, or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-1.5 bg-white rounded-lg border border-slate-200 text-xs text-slate-800 placeholder-slate-400 shadow-xs focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Filters: All Calls and Orders Only (Exceptions removed) */}
          <div className="inline-flex rounded-lg bg-slate-100 p-0.5 text-xs font-semibold">
            <button
              onClick={() => setFilterType('all')}
              className={`px-3 py-1.5 rounded-md transition-colors ${
                filterType === 'all'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All Calls
            </button>
            <button
              onClick={() => setFilterType('orders')}
              className={`px-3 py-1.5 rounded-md transition-colors ${
                filterType === 'orders'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Orders Only
            </button>
          </div>

          <button
            onClick={fetchCalls}
            className="p-1.5 rounded-lg bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors shadow-xs"
            title="Refresh Calls"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={handleExportCSV}
            disabled={exporting}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-semibold shadow-xs transition-colors"
          >
            <Download className={`w-3.5 h-3.5 text-white ${exporting ? 'animate-bounce' : ''}`} />
            <span>{exporting ? 'Exporting...' : 'Export CSV'}</span>
          </button>
        </div>
      </div>

      {loading && !calls && <LoadingState message="Loading call history..." />}
      {error && !calls && <ErrorState message={error} onRetry={fetchCalls} />}

      {/* Main Table Card */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200/80 font-bold uppercase tracking-wider text-[11px] text-slate-500">
                <th className="px-5 py-3">Timestamp</th>
                <th className="px-5 py-3">Caller</th>
                <th className="px-5 py-3">Intent</th>
                <th className="px-5 py-3">Duration</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedCalls.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-slate-400">
                    No calls match your search query or filter.
                  </td>
                </tr>
              ) : (
                paginatedCalls.map((call) => {
                  const displayName = getCallerDisplayName(call);
                  const initial = displayName.charAt(0).toUpperCase() || 'C';
                  const isCompleted = call.status === 'COMPLETED';
                  const isOrder = (call.intent || '').toUpperCase().includes('ORDER');
                  const phoneFormatted = call.fromNumber || 'Restricted Phone';

                  return (
                    <tr key={call.id} className="hover:bg-slate-50/70 transition-colors">
                      {/* Timestamp */}
                      <td className="px-5 py-3.5 whitespace-nowrap text-slate-600">
                        <div className="flex items-center gap-1.5">
                          <PhoneIncoming className="w-3.5 h-3.5 text-blue-600" />
                          <span className="font-medium">
                            {new Date(call.createdAt).toLocaleString('en-GB', {
                              day: '2-digit',
                              month: '2-digit',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                        </div>
                      </td>

                      {/* Caller / Customer */}
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs flex-shrink-0">
                            {initial}
                          </div>
                          <div>
                            <p className="font-bold text-slate-900 leading-tight">{displayName}</p>
                            <p className="text-[11px] text-slate-400 font-mono">{phoneFormatted}</p>
                          </div>
                        </div>
                      </td>

                      {/* Intent */}
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            isOrder
                              ? 'bg-blue-50 text-blue-700 border border-blue-200'
                              : 'bg-slate-100 text-slate-700'
                          }`}
                        >
                          {call.intent || 'Unknown'}
                        </span>
                      </td>

                      {/* Duration */}
                      <td className="px-5 py-3.5 whitespace-nowrap text-slate-700 font-medium">
                        {call.durationSeconds}s
                      </td>

                      {/* Status */}
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase border ${
                            isCompleted
                              ? 'bg-slate-100 text-slate-600 border-slate-200'
                              : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          }`}
                        >
                          {call.status}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="px-5 py-3.5 whitespace-nowrap text-right">
                        <Link
                          href={`/calls/${call.id}`}
                          className="inline-flex items-center gap-1 font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                        >
                          <span>View Detail</span>
                          <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Table Footer with Pagination when > 10 calls */}
        {filteredCalls.length > pageSize ? (
          <div className="px-5 py-3.5 bg-slate-50/70 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
            <div>
              Showing <span className="font-semibold text-slate-800">{startEntry}</span> to{' '}
              <span className="font-semibold text-slate-800">{endEntry}</span> of{' '}
              <span className="font-semibold text-slate-800">{filteredCalls.length}</span> calls
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
            Showing <span className="font-semibold text-slate-800">{filteredCalls.length}</span> of{' '}
            <span className="font-semibold text-slate-800">{totalCalls}</span> calls
          </div>
        )}
      </div>
    </div>
  );
}
