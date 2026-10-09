import { Loader2 } from 'lucide-react';

export function LoadingState({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 w-full h-full min-h-[200px]">
      <Loader2 className="w-8 h-8 text-slate-400 animate-spin mb-4" />
      <p className="text-sm text-slate-500 font-medium">{message}</p>
    </div>
  );
}
