'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { FAQ } from '@/types/faq';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import { BookOpen } from 'lucide-react';

export default function KnowledgePage() {
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFaqs = async () => {
    try {
      const response = await apiClient.faqs.list();
      setFaqs(response.data);
      setError(null);
    } catch (err) {
      setError('Unable to load knowledge entries.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFaqs();
  }, []);

  if (loading && faqs.length === 0) return <LoadingState message="Loading knowledge base..." />;
  if (error && faqs.length === 0) return <ErrorState message={error} onRetry={fetchFaqs} />;

  if (faqs.length === 0) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-2xl font-semibold text-slate-900">Knowledge Base</h1>
        <p className="text-slate-600">Approved restaurant answers for the voice agent.</p>
        <EmptyState icon={<BookOpen className="w-12 h-12" />} title="No knowledge entries yet" description="Add FAQs to help the voice agent answer questions." />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Knowledge Base</h1>
          <p className="text-slate-600 mt-1">Approved restaurant answers for the voice agent.</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-sm font-medium text-slate-500">
                <th className="p-4">Question</th>
                <th className="p-4">English Answer</th>
                <th className="p-4">French Answer</th>
                <th className="p-4 text-center">Category</th>
                <th className="p-4 text-center">Active</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {faqs.map((faq) => (
                <tr key={faq.id} className="hover:bg-slate-50 transition-colors">
                  <td className="p-4 font-medium text-slate-900">{faq.question}</td>
                  <td className="p-4 text-slate-600 whitespace-pre-wrap">{faq.answerEn}</td>
                  <td className="p-4 text-slate-600 whitespace-pre-wrap">{faq.answerFr}</td>
                  <td className="p-4 text-slate-500 text-center">
                    <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                      {faq.category || 'General'}
                    </span>
                  </td>
                  <td className="p-4 text-center">
                    {faq.active ? (
                      <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-700">
                        ✓
                      </span>
                    ) : (
                      <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-slate-400">
                        -
                      </span>
                    )}
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
