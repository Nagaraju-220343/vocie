'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { Customer } from '@/types/customer';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  Search,
  Phone,
  Users,
  MapPin,
  RefreshCw,
  PhoneCall,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.customers.list({ pageSize: '100' });
      setCustomers(response.data || []);
      setError(null);
    } catch (err) {
      setError('Unable to load customers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

  const filteredCustomers = customers.filter((c) => {
    const name = (c.name || '').toLowerCase();
    const phone = (c.phone || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    return !query || name.includes(query) || phone.includes(query);
  });

  const totalCalls = customers.reduce((acc, c) => acc + (c.callCount || 0), 0);
  const totalPages = Math.ceil(filteredCustomers.length / pageSize) || 1;
  const paginatedCustomers = filteredCustomers.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const startEntry = filteredCustomers.length === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endEntry = Math.min(currentPage * pageSize, filteredCustomers.length);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Customers
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Customer profiles captured from restaurant AI voice calls.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="relative min-w-[220px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              placeholder="Search customer or phone..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-1.5 bg-white rounded-lg border border-slate-200 text-xs text-slate-800 placeholder-slate-400 shadow-xs focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
          </div>

          <button
            onClick={fetchCustomers}
            type="button"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 text-xs font-semibold shadow-xs hover:bg-slate-50 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Customers
            </p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{customers.length}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Users className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Customer Calls
            </p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{totalCalls}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <PhoneCall className="w-5 h-5" />
          </div>
        </div>
      </div>

      {loading && customers.length === 0 && <LoadingState message="Loading customers..." />}
      {error && customers.length === 0 && <ErrorState message={error} onRetry={fetchCustomers} />}

      {!loading && customers.length === 0 && (
        <EmptyState
          icon={<Users className="w-12 h-12 text-slate-400" />}
          title="No customers yet"
          description="Customer records will appear here as voice calls are received."
        />
      )}

      {/* Real Customers Table */}
      {customers.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100">
              <thead className="bg-slate-50/70">
                <tr>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    CUSTOMER
                  </th>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    PHONE
                  </th>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    ADDRESS
                  </th>
                  <th className="px-5 py-3 text-center text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    CALLS
                  </th>
                  <th className="px-5 py-3 text-right text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    LAST CALL
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {paginatedCustomers.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-8 text-center text-slate-400">
                      No customers match your search query.
                    </td>
                  </tr>
                ) : (
                  paginatedCustomers.map((customer) => {
                    const initial = (customer.name || 'C').charAt(0).toUpperCase();

                    return (
                      <tr key={customer.id} className="hover:bg-slate-50/70 transition-colors">
                        {/* Name */}
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          <div className="flex items-center gap-2.5">
                            <div className="w-7 h-7 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs flex-shrink-0">
                              {initial}
                            </div>
                            <span className="font-bold text-slate-900">{customer.name}</span>
                          </div>
                        </td>

                        {/* Phone */}
                        <td className="px-5 py-3.5 whitespace-nowrap font-mono text-slate-700">
                          {customer.phone || 'N/A'}
                        </td>

                        {/* Address */}
                        <td className="px-5 py-3.5 text-slate-600 max-w-xs truncate">
                          {customer.address ? (
                            <span className="flex items-center gap-1 text-slate-700">
                              <MapPin className="w-3 h-3 text-slate-400 flex-shrink-0" />
                              <span className="truncate">{customer.address}</span>
                            </span>
                          ) : (
                            <span className="text-slate-400 italic">No address recorded</span>
                          )}
                        </td>

                        {/* Calls */}
                        <td className="px-5 py-3.5 whitespace-nowrap text-center">
                          <span className="inline-flex items-center justify-center px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-bold text-xs">
                            {customer.callCount}
                          </span>
                        </td>

                        {/* Last Call */}
                        <td className="px-5 py-3.5 whitespace-nowrap text-right text-slate-600 font-medium">
                          {customer.lastCallAt
                            ? new Date(customer.lastCallAt).toLocaleString('en-GB', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })
                            : 'N/A'}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Table Footer with Pagination when > 10 customers */}
          {filteredCustomers.length > pageSize ? (
            <div className="px-5 py-3.5 bg-slate-50/70 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
              <div>
                Showing <span className="font-semibold text-slate-800">{startEntry}</span> to{' '}
                <span className="font-semibold text-slate-800">{endEntry}</span> of{' '}
                <span className="font-semibold text-slate-800">{filteredCustomers.length}</span> customers
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
              Showing <span className="font-semibold text-slate-800">{filteredCustomers.length}</span> of{' '}
              <span className="font-semibold text-slate-800">{customers.length}</span> customers
            </div>
          )}
        </div>
      )}
    </div>
  );
}
