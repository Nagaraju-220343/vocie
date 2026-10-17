export interface Call {
  id: string;
  providerCallId: string;
  direction: string;
  fromNumber: string;
  customerName?: string | null;
  toNumber: string;
  language: string;
  intent: string;
  status: string;
  startedAt: string | null;
  endedAt: string | null;
  durationSeconds: number;
  transcript: string;
  summary: string;
  recordingUrl: string | null;
  escalated: boolean;
  escalationReason: string | null;
  createdAt: string;
  updatedAt: string;
}

const FOOD_KEYWORDS = ['pizza', 'pizzas', 'burger', 'burgers', 'margherita', 'salad', 'salade', 'drink', 'order', 'business', 'item', 'dish'];

export function formatPersonName(name?: string | null): string {
  if (!name || !name.trim()) return '';
  let cleaned = name.trim();
  const lower = cleaned.toLowerCase();
  if (lower === 'web browser' || lower.includes('browser') || lower === 'unknown' || lower === 'web call' || lower === 'customer' || lower === 'guest caller') {
    return '';
  }
  const words = lower.split(/\s+/);
  if (words.some(w => FOOD_KEYWORDS.includes(w))) {
    return '';
  }
  // Strip speech disfluencies & conversational fillers: "uh, ", "um, ", "it's ", "yeah, ", etc.
  cleaned = cleaned.replace(/^(\s*(uh|um|er|ah|eh|oh|well|yeah|yep|so|it's|its|im|i'm|this is|my name is|name is|je m'appelle|c'est|le nom est)\b[\s,.:!?-]*)+/i, '').trim();
  cleaned = cleaned.replace(/^[\s,.:!?-]+/, '').replace(/[\s,.:!?-]+$/, '').trim();
  if (!cleaned || cleaned.length < 2) return '';
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}

export function getCallerDisplayName(call: { customerName?: string | null; fromNumber?: string | null }): string {
  const fromCust = formatPersonName(call.customerName);
  if (fromCust) {
    return fromCust;
  }
  const fromNum = formatPersonName(call.fromNumber);
  if (fromNum) {
    return fromNum;
  }
  return 'Customer';
}

export interface PaginatedCalls {
  data: Call[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
