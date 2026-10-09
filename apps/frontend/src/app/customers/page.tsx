'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { Customer } from '@/types/customer';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import { Users, Phone, MapPin } from 'lucide-react';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCustomers = async () => {
    try {
      const response = await apiClient.customers.list();
      setCustomers(response.data);
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

  if (loading && customers.length === 0) return <LoadingState message="Loading customers..." />;
  if (error && customers.length === 0) return <ErrorState message={error} onRetry={fetchCustomers} />;

  if (customers.length === 0) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-2xl font-semibold text-slate-900">Customers</h1>
        <p className="text-slate-600">Customer information from restaurant calls</p>
        <EmptyState icon={<Users className="w-12 h-12" />} title="No customers yet" description="Customers will appear here after calls." />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Customers</h1>
        <p className="text-slate-600 mt-1">Customer information from restaurant calls</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-sm font-medium text-slate-500">
                <th className="p-4">Customer</th>
                <th className="p-4">Phone</th>
                <th className="p-4">Address</th>
                <th className="p-4 text-center">Calls</th>
                <th className="p-4 text-right">Last Call</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {customers.map((customer) => (
                <tr key={customer.id} className="hover:bg-slate-50 transition-colors">
                  <td className="p-4 font-medium text-slate-900">{customer.name || 'Unknown'}</td>
                  <td className="p-4 text-slate-600">
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4 text-slate-400" />
                      {customer.phone || 'N/A'}
                    </div>
                  </td>
                  <td className="p-4 text-slate-600 max-w-xs truncate" title={customer.address || ''}>
                    {customer.address ? (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-slate-400 flex-shrink-0" />
                        <span className="truncate">{customer.address}</span>
                      </div>
                    ) : (
                      'N/A'
                    )}
                  </td>
                  <td className="p-4 text-slate-600 text-center">{customer.callCount}</td>
                  <td className="p-4 text-slate-500 text-right">
                    {customer.lastCallAt ? new Date(customer.lastCallAt).toLocaleDateString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
