'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { PaginatedOrders } from '@/types/order';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { StatusBadge } from '@/components/ui/StatusBadge';
import Link from 'next/link';

export default function OrdersPage() {
  const [orders, setOrders] = useState<PaginatedOrders | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await apiClient.orders.list({ pageSize: '50' });
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

  if (loading && !orders) return <LoadingState message="Loading orders..." />;
  if (error && !orders) return <ErrorState message={error} onRetry={fetchOrders} />;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Orders</h1>
      </div>

      <div className="bg-white shadow-sm rounded-xl border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Date</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Customer</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Items</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Call Link</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {orders?.data.map((order) => (
                <tr key={order.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    {new Date(order.createdAt).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                    {order.customerName || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 max-w-xs" title={order.items.map(item => `${item.quantity}x ${item.name}`).join(', ')}>
                    {order.items.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {order.items.map((item, idx) => (
                          <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                            <span className="font-bold mr-1">{item.quantity}x</span> {item.name}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-sm text-slate-500">No items</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <StatusBadge status={order.status} type="order" />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link href={`/calls/${order.callId}`} className="text-blue-600 hover:text-blue-900">
                      View Call
                    </Link>
                  </td>
                </tr>
              ))}
              {orders?.data.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-sm text-slate-500">
                    No orders found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
