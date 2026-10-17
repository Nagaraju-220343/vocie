'use client';

import { useEffect, useRef, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import {
  Mic,
  PhoneOff,
  Radio,
  Loader2,
  AlertCircle,
  ExternalLink,
  Volume2,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';
import Link from 'next/link';

export type CallState =
  | 'ready'
  | 'requesting_mic'
  | 'connecting'
  | 'active'
  | 'ending'
  | 'ended'
  | 'error';

interface WebVoiceCallCardProps {
  onCallStarted?: (callId: string) => void;
  onCallEnded?: (callId: string) => void;
}

export function WebVoiceCallCard({ onCallStarted, onCallEnded }: WebVoiceCallCardProps) {
  const [callState, setCallState] = useState<CallState>('ready');
  const [callId, setCallId] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // References to preserve instances across re-renders and React StrictMode
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const clientRef = useRef<any>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const endedTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isStartingRef = useRef(false);

  // Clean up on component unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (endedTimerRef.current) {
        clearTimeout(endedTimerRef.current);
      }
      if (clientRef.current) {
        try {
          clientRef.current.stopCall();
        } catch {
          // Ignore cleanup errors on unmount
        }
        clientRef.current = null;
      }
    };
  }, []);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartCall = async () => {
    // Prevent duplicate call creation when clicking repeatedly
    if (callState !== 'ready' && callState !== 'error' && callState !== 'ended') {
      return;
    }
    if (isStartingRef.current) {
      return;
    }

    isStartingRef.current = true;
    setErrorMessage(null);

    try {
      // 1. Verify browser audio capabilities and request microphone permission
      if (typeof window === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
        throw new Error('UNSUPPORTED_BROWSER');
      }

      setCallState('requesting_mic');

      // Check mic access early to give clear permission prompt
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Immediately release test tracks so Retell SDK can acquire cleanly
        stream.getTracks().forEach((track) => track.stop());
      } catch (micErr: any) {
        if (
          micErr.name === 'NotAllowedError' ||
          micErr.name === 'PermissionDeniedError'
        ) {
          throw new Error('PERMISSION_DENIED');
        } else if (
          micErr.name === 'NotFoundError' ||
          micErr.name === 'DevicesNotFoundError'
        ) {
          throw new Error('NO_MIC_AVAILABLE');
        }
        throw micErr;
      }

      // 2. Transition to connecting
      setCallState('connecting');

      // 3. Request web call session and access token from backend (keeps API key server-side)
      const session = await apiClient.voice.createWebCall();
      if (!session.access_token || !session.call_id) {
        throw new Error('INVALID_SESSION');
      }

      setCallId(session.call_id);

      // 4. Dynamically import RetellWebClient for client-side execution
      const { RetellWebClient } = await import('retell-client-js-sdk');
      const retellClient = new RetellWebClient();
      clientRef.current = retellClient;

      // 5. Set up real SDK lifecycle listeners
      retellClient.on('call_started', () => {
        isStartingRef.current = false;
        setCallState('active');
        setDuration(0);

        // Start duration counter
        if (timerRef.current) clearInterval(timerRef.current);
        timerRef.current = setInterval(() => {
          setDuration((prev) => prev + 1);
        }, 1000);

        onCallStarted?.(session.call_id);
      });

      retellClient.on('call_ended', () => {
        if (timerRef.current) clearInterval(timerRef.current);
        setIsSpeaking(false);
        setCallState('ended');
        isStartingRef.current = false;
        clientRef.current = null;
        onCallEnded?.(session.call_id);

        // Automatically transition back to ready after displaying "Call ended"
        if (endedTimerRef.current) clearTimeout(endedTimerRef.current);
        endedTimerRef.current = setTimeout(() => {
          setCallState('ready');
          setDuration(0);
        }, 3500);
      });

      retellClient.on('agent_start_talking', () => {
        setIsSpeaking(true);
      });

      retellClient.on('agent_stop_talking', () => {
        setIsSpeaking(false);
      });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      retellClient.on('error', (err: any) => {
        console.error('Retell Web Client error:', err);
        if (timerRef.current) clearInterval(timerRef.current);
        setIsSpeaking(false);
        setCallState('error');
        isStartingRef.current = false;
        clientRef.current = null;
        setErrorMessage(
          'An error occurred during the voice call. Please check your connection and try again.'
        );
      });

      // 6. Connect the browser audio session using the temporary access token
      await retellClient.startCall({
        accessToken: session.access_token,
      });
    } catch (err: unknown) {
      isStartingRef.current = false;
      if (timerRef.current) clearInterval(timerRef.current);
      setCallState('error');

      const message = (err as Error).message || '';
      if (message === 'PERMISSION_DENIED') {
        setErrorMessage(
          'Microphone permission was denied. Please allow microphone access in your browser address bar and try again.'
        );
      } else if (message === 'NO_MIC_AVAILABLE') {
        setErrorMessage(
          'No microphone found on your device. Please connect a microphone or headset and try again.'
        );
      } else if (message === 'UNSUPPORTED_BROWSER') {
        setErrorMessage(
          'Your browser does not support browser-based audio calls. Please try using modern Google Chrome, Microsoft Edge, or Firefox.'
        );
      } else {
        setErrorMessage(
          'Unable to establish a voice session. Please ensure the backend is reachable and Retell credentials are configured.'
        );
      }
    }
  };

  const handleEndCall = () => {
    if (callState === 'ending' || callState === 'ready' || callState === 'ended') return;

    setCallState('ending');
    if (timerRef.current) clearInterval(timerRef.current);

    try {
      if (clientRef.current) {
        clientRef.current.stopCall();
      }
    } catch (err) {
      console.warn('Error stopping call:', err);
    }

    setTimeout(() => {
      setCallState('ended');
      setIsSpeaking(false);
      clientRef.current = null;
      if (callId) {
        onCallEnded?.(callId);
      }

      if (endedTimerRef.current) clearTimeout(endedTimerRef.current);
      endedTimerRef.current = setTimeout(() => {
        setCallState('ready');
        setDuration(0);
      }, 3500);
    }, 500);
  };

  return (
    <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl shadow-lg border border-indigo-900/40 p-6 text-white overflow-hidden relative">
      {/* Background decorative glow */}
      <div className="absolute -top-12 -right-12 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-12 -left-12 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        {/* Left Column: Title & Description */}
        <div className="space-y-2 max-w-xl">
          <div className="flex items-center gap-2">
            <span className="p-1.5 bg-indigo-500/20 text-indigo-300 rounded-lg border border-indigo-500/30">
              <Sparkles className="w-4 h-4 text-indigo-400" />
            </span>
            <h2 className="text-xl font-bold tracking-tight text-white">Le Gourmet AI Assistant</h2>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Bilingual (FR / EN)
            </span>
          </div>
          <p className="text-slate-300 text-sm leading-relaxed">
            Experience our AI restaurant assistant. Start a conversation, ask questions, or place a sample order.
          </p>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Mic className="w-3.5 h-3.5 text-slate-400" />
            <span>Browser will request microphone access when you start the call.</span>
          </div>
        </div>

        {/* Right Column: Dynamic Action Interface */}
        <div className="w-full md:w-auto flex flex-col items-start md:items-end gap-3 min-w-[280px]">
          {/* READY STATE */}
          {callState === 'ready' && (
            <div className="w-full md:w-auto flex flex-col sm:flex-row items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/80 border border-slate-700/60 rounded-xl text-xs text-slate-300">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                <span>Ready</span>
              </div>
              <button
                onClick={handleStartCall}
                id="talk-to-le-gourmet-btn"
                className="w-full sm:w-auto px-6 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-xl shadow-md hover:shadow-indigo-500/25 transition-all duration-200 flex items-center justify-center gap-2.5 cursor-pointer"
              >
                <Mic className="w-4 h-4" />
                <span>Talk to Le Gourmet</span>
              </button>
            </div>
          )}

          {/* REQUESTING MICROPHONE PERMISSION STATE */}
          {callState === 'requesting_mic' && (
            <div className="w-full md:w-auto flex items-center gap-2.5 px-4 py-2.5 bg-amber-950/60 border border-amber-700/50 rounded-xl text-sm text-amber-200">
              <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
              <span>Requesting microphone permission...</span>
            </div>
          )}

          {/* CONNECTING STATE */}
          {callState === 'connecting' && (
            <div className="w-full md:w-auto flex items-center gap-2.5 px-4 py-2.5 bg-indigo-950/60 border border-indigo-700/50 rounded-xl text-sm text-indigo-200">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
              <span>Connecting to Le Gourmet...</span>
            </div>
          )}

          {/* ACTIVE CALL STATE (LIVE CALL) */}
          {callState === 'active' && (
            <div className="w-full flex flex-col items-start md:items-end gap-3">
              <div className="flex items-center gap-3">
                {/* Live Call Indicator */}
                <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/20 border border-emerald-500/30 rounded-lg">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                  </span>
                  <span className="text-xs font-bold text-emerald-400 tracking-wider">LIVE CALL</span>
                </div>

                {/* Duration */}
                <div className="px-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-xs font-mono font-semibold text-slate-200">
                  {formatDuration(duration)}
                </div>

                {/* End Call Button */}
                <button
                  onClick={handleEndCall}
                  id="end-call-btn"
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs rounded-lg shadow transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <PhoneOff className="w-3.5 h-3.5" />
                  <span>End Call</span>
                </button>
              </div>

              {/* Status Indicator (Speaking vs Listening) */}
              <div className="flex items-center justify-between w-full text-xs">
                <div className="flex items-center gap-2 text-slate-300">
                  {isSpeaking ? (
                    <>
                      <Volume2 className="w-4 h-4 text-indigo-400 animate-pulse" />
                      <span className="text-indigo-300 font-medium">Assistant speaking...</span>
                    </>
                  ) : (
                    <>
                      <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
                      <span className="text-emerald-300 font-medium">Listening to you...</span>
                    </>
                  )}
                </div>

                {callId && (
                  <Link
                    href={`/calls/${callId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-indigo-300 hover:text-indigo-200 flex items-center gap-1 hover:underline ml-3"
                  >
                    <span>View Live Call</span>
                    <ExternalLink className="w-3 h-3" />
                  </Link>
                )}
              </div>
            </div>
          )}

          {/* ENDING STATE */}
          {callState === 'ending' && (
            <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-sm">
              <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
              <span>Ending call...</span>
            </div>
          )}

          {/* CALL ENDED STATE */}
          {callState === 'ended' && (
            <div className="flex items-center gap-2.5 px-4 py-2 bg-emerald-950/60 border border-emerald-800/50 text-emerald-300 rounded-xl text-sm">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Call ended ({formatDuration(duration)})</span>
            </div>
          )}

          {/* ERROR STATE */}
          {callState === 'error' && (
            <div className="flex flex-col items-start md:items-end gap-2 w-full">
              <div className="flex items-start gap-2 p-3 bg-rose-950/70 border border-rose-800/60 rounded-xl text-xs text-rose-200 max-w-md">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span>{errorMessage || 'Call failed to start.'}</span>
              </div>
              <button
                onClick={() => {
                  setCallState('ready');
                  setErrorMessage(null);
                }}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-white rounded-lg transition-colors cursor-pointer"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
