'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { Call, getCallerDisplayName } from '@/types/call';
import { Order } from '@/types/order';
import { LoadingState } from '@/components/ui/LoadingState';
import { ErrorState } from '@/components/ui/ErrorState';
import { useRealtime } from '@/hooks/use-realtime';
import {
  Phone,
  Clock,
  Globe,
  MessageSquare,
  Copy,
  Check,
  ShoppingCart,
  ArrowLeft,
  MapPin,
  Volume2,
  FileText,
  AlertTriangle,
  Truck,
  PackageCheck,
} from 'lucide-react';
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
  const [copied, setCopied] = useState(false);

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
      const newTranscript = prev.transcript
        ? `${prev.transcript}\n\n${speaker.toUpperCase()}:\n${text}`
        : `${speaker.toUpperCase()}:\n${text}`;
      return { ...prev, transcript: newTranscript };
    });
  });

  useEvent('order.updated', (event) => {
    setOrders([event.payload]);
  });

  useEvent('call.ended', () => {
    setCall((prev) => (prev ? { ...prev, status: 'COMPLETED' } : null));
  });

  if (loading && !call) return <LoadingState message="Loading call details..." />;
  if (error && !call) return <ErrorState message={error} onRetry={fetchData} />;
  if (!call) return <ErrorState message="Call not found." />;

  const currentOrder = orders[0];
  const callerDisplayName = getCallerDisplayName(call);

  const handleCopyTranscript = () => {
    if (call.transcript) {
      navigator.clipboard.writeText(call.transcript);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Helper to parse raw transcript into clean conversation bubbles
  const renderTranscriptBubbles = () => {
    if (!call.transcript || !call.transcript.trim()) {
      return (
        <div className="p-8 text-center text-xs text-slate-400">
          No transcript captured for this call.
        </div>
      );
    }

    // Split transcript by turns (handles "Agent: ...", "User: ...", "Agent:\n...")
    const rawLines = call.transcript.split('\n');
    const turns: { speaker: 'agent' | 'customer' | 'other'; text: string }[] = [];
    let currentSpeaker: 'agent' | 'customer' | 'other' = 'agent';
    let currentBuffer: string[] = [];

    const flushTurn = () => {
      const text = currentBuffer.join(' ').trim();
      if (text) {
        turns.push({ speaker: currentSpeaker, text });
      }
      currentBuffer = [];
    };

    for (const rawLine of rawLines) {
      const line = rawLine.trim();
      if (!line) continue;

      const agentMatch = /^(?:agent|assistant)\s*:\s*(.*)$/i.exec(line);
      const customerMatch = /^(?:user|customer|caller)\s*:\s*(.*)$/i.exec(line);

      if (agentMatch) {
        flushTurn();
        currentSpeaker = 'agent';
        if (agentMatch[1].trim()) {
          currentBuffer.push(agentMatch[1].trim());
        }
      } else if (customerMatch) {
        flushTurn();
        currentSpeaker = 'customer';
        if (customerMatch[1].trim()) {
          currentBuffer.push(customerMatch[1].trim());
        }
      } else {
        currentBuffer.push(line);
      }
    }
    flushTurn();

    return (
      <div className="space-y-4">
        {turns.map((turn, idx) => {
          if (turn.speaker === 'agent') {
            return (
              <div key={idx} className="space-y-1">
                <span className="text-[11px] font-bold tracking-wider text-blue-600 uppercase">
                  AGENT
                </span>
                <div className="border-l-2 border-blue-500 pl-3 py-1 text-xs text-slate-800 leading-relaxed font-normal">
                  {turn.text}
                </div>
              </div>
            );
          }

          if (turn.speaker === 'customer') {
            return (
              <div key={idx} className="space-y-1">
                <span className="text-[11px] font-bold tracking-wider text-slate-500 uppercase">
                  CUSTOMER
                </span>
                <div className="bg-slate-100/90 rounded-xl px-4 py-2.5 text-xs text-slate-800 font-medium max-w-xl">
                  {turn.text}
                </div>
              </div>
            );
          }

          return (
            <div key={idx} className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              {turn.text}
            </div>
          );
        })}
      </div>
    );
  };

  const isDelivery = currentOrder?.orderType?.toUpperCase() === 'DELIVERY';

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-6">
      {/* Top Breadcrumb & Metadata Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs">
          <Link
            href="/calls"
            className="inline-flex items-center gap-1.5 font-semibold text-blue-600 hover:text-blue-800 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Calls</span>
          </Link>
          <span className="text-slate-300">/</span>
          <span className="text-slate-900 font-bold">Call Details</span>
          <span
            className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border ${
              call.status === 'COMPLETED'
                ? 'bg-slate-100 text-slate-600 border-slate-200'
                : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
            }`}
          >
            {call.status || 'COMPLETED'}
          </span>
        </div>

        {call.escalated && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-50 text-red-700 border border-red-200 text-xs font-semibold">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Escalated to Human</span>
          </div>
        )}
      </div>

      {/* Prominent Call Summary at Top of Page */}
      {call.summary && (
        <div className="bg-white rounded-xl border border-blue-100/80 shadow-xs p-5 bg-gradient-to-r from-blue-50/50 via-white to-white">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="w-4 h-4 text-blue-600" />
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Call Summary
            </h3>
          </div>
          <p className="text-xs text-slate-700 leading-relaxed font-normal">
            {call.summary}
          </p>
        </div>
      )}

      {/* Main 2-Column Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: Transcript & Audio Recording */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs flex flex-col overflow-hidden">
            {/* Transcript Card Header */}
            <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-blue-600" />
                <h2 className="text-sm font-bold text-slate-900">Call Transcript</h2>
              </div>
              {call.transcript && (
                <button
                  onClick={handleCopyTranscript}
                  type="button"
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              )}
            </div>

            <div className="p-5 space-y-4">
              {/* Audio player if recording is available */}
              {call.recordingUrl && (
                <div className="p-3 bg-blue-50/70 border border-blue-100 rounded-xl flex items-center gap-3">
                  <Volume2 className="w-5 h-5 text-blue-600 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-slate-900 mb-1">Call Audio Recording</p>
                    <audio controls className="w-full h-8" src={call.recordingUrl}>
                      Your browser does not support audio playback.
                    </audio>
                  </div>
                </div>
              )}

              {/* Real Transcript Content */}
              {renderTranscriptBubbles()}
            </div>
          </div>
        </div>

        {/* Right 1 Column: Caller Information & Associated Order */}
        <div className="space-y-5">
          {/* Associated Order Card */}
          <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <ShoppingCart className="w-4 h-4 text-blue-600" />
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Associated Order
                </h3>
              </div>
              {currentOrder && (
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                    currentOrder.status === 'CONFIRMED'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}
                >
                  {currentOrder.status || 'CONFIRMED'}
                </span>
              )}
            </div>

            {currentOrder ? (
              <div className="py-3 text-xs space-y-3.5">
                {/* Customer Name */}
                <div>
                  <p className="text-slate-400 text-[11px] font-semibold uppercase">Customer Name</p>
                  <p className="font-bold text-slate-900 text-sm mt-0.5">
                    {currentOrder.customerName || callerDisplayName || 'Customer'}
                  </p>
                  {currentOrder.phone && (
                    <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                      {currentOrder.phone}
                    </p>
                  )}
                </div>

                {/* Order Type (Pickup or Delivery) */}
                <div>
                  <p className="text-slate-400 text-[11px] font-semibold uppercase mb-1">Order Type</p>
                  <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-blue-50 border border-blue-200/70 text-blue-700 text-xs font-bold uppercase tracking-wider">
                    {isDelivery ? (
                      <>
                        <Truck className="w-3.5 h-3.5 text-blue-600" />
                        <span>Delivery</span>
                      </>
                    ) : (
                      <>
                        <PackageCheck className="w-3.5 h-3.5 text-blue-600" />
                        <span>Pickup In-Store</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Delivery Address if order is delivery or address exists */}
                {(isDelivery || currentOrder.address) && (
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                    <p className="text-slate-500 text-[11px] font-semibold uppercase flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-blue-600" />
                      <span>Delivery Address</span>
                    </p>
                    <p className="font-semibold text-slate-900 text-xs leading-relaxed">
                      {currentOrder.address || 'Address pending from customer'}
                    </p>
                  </div>
                )}

                {/* Real Ordered Items */}
                <div className="pt-2 border-t border-slate-100">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-slate-400 text-[11px] font-semibold uppercase">
                      Ordered Items ({currentOrder.items?.length || 0})
                    </p>
                  </div>

                  {currentOrder.items && currentOrder.items.length > 0 ? (
                    <div className="space-y-2">
                      {currentOrder.items.map((item, idx) => (
                        <div
                          key={idx}
                          className="bg-slate-50 rounded-lg p-2.5 border border-slate-100 flex items-center justify-between"
                        >
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-blue-600 text-xs bg-blue-100/70 px-1.5 py-0.5 rounded">
                              {item.quantity}x
                            </span>
                            <span className="font-bold text-slate-800 text-xs">
                              {item.name}
                            </span>
                          </div>
                          {item.price != null && (
                            <span className="font-bold text-slate-900 text-xs">
                              €{Number(item.price).toFixed(2)}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-slate-400 italic text-xs">No items specified</p>
                  )}
                </div>

                {/* Estimated Total Price */}
                {(() => {
                  const calculatedTotal = (currentOrder.items || []).reduce(
                    (sum, item) => sum + (item.price ? Number(item.price) * (item.quantity || 1) : 0),
                    0
                  );
                  return calculatedTotal > 0 ? (
                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-slate-900">
                      <span>Total Amount</span>
                      <span className="text-blue-600 text-sm">€{calculatedTotal.toFixed(2)}</span>
                    </div>
                  ) : null;
                })()}

                {/* Order Notes if present */}
                {currentOrder.notes && (
                  <div className="pt-2 border-t border-slate-100">
                    <p className="text-slate-400 text-[11px] font-semibold uppercase mb-1">Order Notes</p>
                    <p className="text-xs text-slate-600 italic bg-slate-50 p-2 rounded-lg border border-slate-100">
                      {currentOrder.notes}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-6 text-center text-xs text-slate-400">
                No order extracted for this call yet.
              </div>
            )}
          </div>

          {/* Caller Information Card */}
          <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-5">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider pb-3 border-b border-slate-100">
              Caller Information
            </h3>

            <div className="divide-y divide-slate-100 text-xs">
              <div className="py-3 flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">
                  <Phone className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-slate-400 text-[11px] font-semibold uppercase">Caller / Customer</p>
                  <p className="font-bold text-slate-900 mt-0.5">{callerDisplayName}</p>
                  {call.fromNumber && (
                    <p className="text-[11px] text-slate-500 font-mono mt-0.5">{call.fromNumber}</p>
                  )}
                </div>
              </div>

              <div className="py-3 flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0">
                  <Globe className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-slate-400 text-[11px] font-semibold uppercase">Language / Intent</p>
                  <p className="font-bold text-slate-900 mt-0.5 capitalize">
                    {call.language || 'English'} • {call.intent || 'Unknown'}
                  </p>
                </div>
              </div>

              <div className="pt-3 flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0">
                  <Clock className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-slate-400 text-[11px] font-semibold uppercase">Duration</p>
                  <p className="font-bold text-slate-900 mt-0.5">
                    {call.durationSeconds} seconds
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CallDetailPage() {
  return (
    <Suspense fallback={<LoadingState message="Loading call page..." />}>
      <CallDetailContent />
    </Suspense>
  );
}
