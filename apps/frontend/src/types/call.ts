export interface Call {
  id: string;
  providerCallId: string;
  direction: string;
  fromNumber: string;
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

export interface PaginatedCalls {
  data: Call[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
