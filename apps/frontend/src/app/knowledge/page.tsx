'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { FAQ } from '@/types/faq';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import { BookOpen, RefreshCw, CheckCircle2, MinusCircle } from 'lucide-react';

export default function KnowledgePage() {
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFaqs = async () => {
    try {
      setLoading(true);
      const response = await apiClient.faqs.list();
      setFaqs(response.data || []);
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

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Knowledge Base</h1>
          <p className="text-xs text-slate-500 mt-1">Approved restaurant answers for the voice agent.</p>
        </div>

        <button
          onClick={fetchFaqs}
          type="button"
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 text-xs font-semibold shadow-xs hover:bg-slate-50 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {faqs.length === 0 ? (
        <EmptyState
          icon={<BookOpen className="w-12 h-12 text-slate-400" />}
          title="No knowledge entries yet"
          description="Approved FAQs will be listed here for voice agent reference."
        />
      ) : (
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-200/80 font-bold uppercase tracking-wider text-[11px] text-slate-500">
                  <th className="px-5 py-3">Question</th>
                  <th className="px-5 py-3">English Answer</th>
                  <th className="px-5 py-3">French Answer</th>
                  <th className="px-5 py-3 text-center">Category</th>
                  <th className="px-5 py-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {faqs.map((faq) => (
                  <tr key={faq.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-slate-900">{faq.question}</td>
                    <td className="px-5 py-3.5 text-slate-600 whitespace-pre-wrap leading-relaxed max-w-xs">{faq.answerEn}</td>
                    <td className="px-5 py-3.5 text-slate-600 whitespace-pre-wrap leading-relaxed max-w-xs">{faq.answerFr}</td>
                    <td className="px-5 py-3.5 text-center whitespace-nowrap">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                        {faq.category || 'General'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center whitespace-nowrap">
                      {faq.active ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          <span>Active</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-500 border border-slate-200">
                          <MinusCircle className="w-3 h-3 text-slate-400" />
                          <span>Inactive</span>
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
