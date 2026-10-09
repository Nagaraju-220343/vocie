export interface FAQ {
  id: string;
  question: string;
  answerFr: string;
  answerEn: string;
  category: string;
  active: boolean;
  updatedAt: string;
}

export interface PaginatedFAQs {
  data: FAQ[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
