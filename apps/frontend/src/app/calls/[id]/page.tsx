'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { Call } from '@/types/call';
import { Order } from '@/types/order';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { useRealtime } from '@/hooks/use-realtime';
import { Phone, MapPin, User, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Suspense } from 'react';

function CallDetailContent() {
  const params = useParams();
  const id = params.id as string;
  const [call, setCall] = useState<Call | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { useEvent } = useRealtime(`call:${id}`);

  const fetchData = async () => {
    try {
      const callData = await apiClient.calls.get(id);
      setCall(callData);
      
      try {
        const orderRes = await apiClient.orders.list({ callId: id });
        setOrders(orderRes.data);
      } catch (err) {
        console.warn('Failed to fetch orders for call', err);
      }
      
      setError(null);
    } catch (err) {
      setError('Unable to load call details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  useEvent('transcript.updated', (event) => {
    setCall((prev) => {
      if (!prev) return prev;
      const speaker = event.payload.role === 'user' ? 'customer' : 'agent';
      const text = event.payload.content;
      // In a real app we'd map to transcriptMessages, but here we append to the text transcript roughly
      const newTranscript = prev.transcript ? `${prev.transcript}\n\n${speaker.toUpperCase()}:\n${text}` : `${speaker.toUpperCase()}:\n${text}`;
      return { ...prev, transcript: newTranscript };
    });
  });

  useEvent('order.updated', (event) => {
    setOrders([event.payload]);
  });

  useEvent('call.escalated', (event) => {
    setCall((prev) => prev ? { ...prev, escalated: true, escalationReason: event.payload.reason } : null);
  });

  useEvent('call.ended', (event) => {
    setCall((prev) => prev ? { ...prev, status: 'COMPLETED' } : null);
  });

  if (loading && !call) return <LoadingState message="Loading call details..." />;
  if (error && !call) return <ErrorState message={error} onRetry={fetchData} />;
  if (!call) return <ErrorState message="Call not found." />;

  const currentOrder = orders[0];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/calls" className="text-sm font-medium text-slate-500 hover:text-slate-900">
            ← Back
          </Link>
          <h1 className="text-2xl font-semibold text-slate-900">Call Details</h1>
          {call.status === 'IN_PROGRESS' && (
            <span className="flex items-center space-x-2 bg-green-100 px-3 py-1 rounded-full">
              <span className="animate-ping inline-flex h-2 w-2 rounded-full bg-green-500"></span>
              <span className="text-xs font-bold text-green-700">IN PROGRESS</span>
            </span>
          )}
          {call.status !== 'IN_PROGRESS' && (
            <StatusBadge status={call.status} type="call" />
          )}
        </div>
        {call.escalated && (
          <div className="flex items-center space-x-2 bg-red-100 px-4 py-2 rounded-lg text-red-700 font-medium text-sm">
            <AlertTriangle className="w-5 h-5" />
            <span>Escalated to Human</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Conversation Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col h-[600px]">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-xl">
              <h3 className="font-semibold text-slate-800">Transcript</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {call.transcript ? (
                <div className="whitespace-pre-wrap text-sm text-slate-700 leading-relaxed font-mono bg-slate-50 p-4 rounded-lg border border-slate-100">
                  {call.transcript}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-400 text-sm">
                  Transcript not available yet.
                </div>
              )}
            </div>
          </div>
          
          {call.summary && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-semibold text-slate-800 mb-2">Summary</h3>
              <p className="text-sm text-slate-600">{call.summary}</p>
            </div>
          )}
        </div>

        {/* Sidebar Info Column */}
        <div className="space-y-6">
          {/* Caller Info */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="font-semibold text-slate-800 mb-4">Caller Information</h3>
            <div className="space-y-4 text-sm">
              <div className="flex items-start">
                <Phone className="w-4 h-4 text-slate-400 mt-0.5 mr-3" />
                <div>
                  <p className="text-slate-500 text-xs">Phone</p>
                  <p className="font-medium text-slate-900">{call.fromNumber}</p>
                </div>
              </div>
              <div className="flex items-start">
                <User className="w-4 h-4 text-slate-400 mt-0.5 mr-3" />
                <div>
                  <p className="text-slate-500 text-xs">Language / Intent</p>
                  <p className="font-medium text-slate-900 capitalize">{call.language || 'Unknown'} / {call.intent || 'Unknown'}</p>
                </div>
              </div>
              {call.durationSeconds > 0 && (
                <div className="pt-4 border-t border-slate-100">
                  <p className="text-slate-500 text-xs">Duration</p>
                  <p className="font-medium text-slate-900">{call.durationSeconds} seconds</p>
                </div>
              )}
            </div>
          </div>

          {/* Current Order */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-800">Current Order</h3>
              {currentOrder && <StatusBadge status={currentOrder.status} type="order" />}
            </div>
            
            {currentOrder ? (
              <div className="space-y-4 text-sm">
                <div className="flex items-start">
                  <User className="w-4 h-4 text-slate-400 mt-0.5 mr-3" />
                  <p className="font-medium text-slate-900">{currentOrder.customerName || 'Not provided'}</p>
                </div>
                <div className="flex items-start">
                  <MapPin className="w-4 h-4 text-slate-400 mt-0.5 mr-3" />
                  <p className="font-medium text-slate-900">{currentOrder.address || 'Not provided'}</p>
                </div>
                
                <div className="pt-4 border-t border-slate-100">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Items</h4>
                  <ul className="space-y-3">
                    {currentOrder.items.map((item, idx) => (
                      <li key={idx} className="flex justify-between items-start">
                        <span className="font-medium text-slate-900">
                          {item.quantity} × {item.name}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-center py-6 text-sm text-slate-500">
                No order extracted yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CallDetailPage() {
  return (
    <Suspense fallback={<LoadingState message="Loading call details..." />}>
      <CallDetailContent />
    </Suspense>
  );
}
