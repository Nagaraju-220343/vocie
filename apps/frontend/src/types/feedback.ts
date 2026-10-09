export interface Feedback {
  id: string;
  callId: string;
  field: string;
  originalValue: string | null;
  correctedValue: string | null;
  reason: string | null;
  createdBy: string;
  createdAt: string;
}

export interface PaginatedFeedback {
  data: Feedback[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
