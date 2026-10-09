import { AlertCircle } from 'lucide-react';

export function ErrorState({ title = 'Error', message, onRetry }: { title?: string; message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-red-50 rounded-lg border border-red-100">
      <AlertCircle className="w-10 h-10 text-red-500 mb-4" />
      <h3 className="text-lg font-medium text-red-800">{title}</h3>
      <p className="text-sm text-red-600 mt-1 mb-4 text-center">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 text-sm font-medium rounded-md transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
}
