'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Lock, Sparkles, ArrowRight, AlertCircle, Loader2, UtensilsCrossed } from 'lucide-react';
import { Suspense } from 'react';

function DemoLoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectPath = searchParams.get('redirect') || '/dashboard';

  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/demo-auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code.trim() }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Invalid demo access code.');
      }

      // Set fallback client-side cookie for immediate synchronization
      document.cookie = 'demo_session=authenticated; path=/; max-age=604800; SameSite=Lax';

      // Always resolve root or empty redirect to /dashboard
      const target =
        !redirectPath || redirectPath === '/' || redirectPath.includes('demo-login')
          ? '/dashboard'
          : redirectPath;

      window.location.href = target;
    } catch (err: any) {
      setError(err.message || 'Access verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background ambient glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-72 h-72 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-2xl mb-4 shadow-sm">
            <UtensilsCrossed className="w-7 h-7 text-indigo-400" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center justify-center gap-2">
            <span>Le Gourmet</span>
            <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Paris
            </span>
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            AI Restaurant Assistant — Client Demonstration
          </p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 shadow-2xl rounded-2xl p-7 backdrop-blur-xl">
          <div className="flex items-center gap-2 text-xs font-medium text-indigo-300 mb-6 bg-indigo-950/60 border border-indigo-900/50 px-3.5 py-2 rounded-xl">
            <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
            <span>Bienvenue! Please enter the demo code to proceed.</span>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="demo-code" className="block text-xs font-medium text-slate-300 mb-1.5">
                Demonstration Access Code
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-slate-500" />
                </div>
                <input
                  id="demo-code"
                  type="password"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="Enter access code"
                  required
                  autoFocus
                  className="block w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                />
              </div>
            </div>

            {error && (
              <div className="flex items-start gap-2.5 p-3 bg-rose-950/60 border border-rose-800/60 rounded-xl text-xs text-rose-300">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !code.trim()}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm rounded-xl shadow-md shadow-indigo-600/20 transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Verifying...</span>
                </>
              ) : (
                <>
                  <span>Enter Demonstration</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>

        <p className="mt-6 text-center text-xs text-slate-500">
          Restaurant Voice Assistant Prototype &copy; 2026 Le Gourmet
        </p>
      </div>
    </div>
  );
}

export default function DemoLoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">Loading...</div>}>
      <DemoLoginForm />
    </Suspense>
  );
}
