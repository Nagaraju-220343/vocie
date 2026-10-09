export function StatusBadge({ status, type }: { status: string; type?: 'call' | 'order' }) {
  const normalized = status.toUpperCase();
  let bg = 'bg-slate-100';
  let text = 'text-slate-700';

  if (normalized === 'LIVE' || normalized === 'IN_PROGRESS' || normalized === 'CONFIRMED') {
    bg = 'bg-green-100';
    text = 'text-green-700';
  } else if (normalized === 'ESCALATED' || normalized === 'FAILED' || normalized === 'CANCELLED') {
    bg = 'bg-red-100';
    text = 'text-red-700';
  } else if (normalized === 'DRAFT' || normalized === 'PENDING' || normalized === 'REVIEW_REQUIRED') {
    bg = 'bg-amber-100';
    text = 'text-amber-700';
  } else if (normalized === 'COMPLETED') {
    bg = 'bg-slate-100';
    text = 'text-slate-700';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bg} ${text}`}>
      {normalized}
    </span>
  );
}
