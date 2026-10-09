import { Call, PaginatedCalls } from '@/types/call';
import { Order, PaginatedOrders } from '@/types/order';
import { Customer, PaginatedCustomers } from '@/types/customer';
import { FAQ, PaginatedFAQs } from '@/types/faq';
import { Feedback, PaginatedFeedback } from '@/types/feedback';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetcher<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`);
  }

  // Handle empty responses (like 204 No Content)
  const text = await response.text();
  return text ? JSON.parse(text) : ({} as T);
}

export const apiClient = {
  calls: {
    list: (params?: Record<string, string>) => {
      const query = new URLSearchParams(params).toString();
      return fetcher<PaginatedCalls>(`/calls${query ? `?${query}` : ''}`);
    },
    get: (id: string) => fetcher<Call>(`/calls/${id}`),
  },
  orders: {
    list: (params?: Record<string, string>) => {
      const query = new URLSearchParams(params).toString();
      return fetcher<PaginatedOrders>(`/orders${query ? `?${query}` : ''}`);
    },
    get: (id: string) => fetcher<Order>(`/orders/${id}`),
  },
  customers: {
    list: (params?: Record<string, string>) => {
      const query = new URLSearchParams(params).toString();
      return fetcher<PaginatedCustomers>(`/customers${query ? `?${query}` : ''}`);
    },
    get: (id: string) => fetcher<Customer>(`/customers/${id}`),
  },
  faqs: {
    list: (params?: Record<string, string>) => {
      const query = new URLSearchParams(params).toString();
      return fetcher<PaginatedFAQs>(`/faqs${query ? `?${query}` : ''}`);
    },
    get: (id: string) => fetcher<FAQ>(`/faqs/${id}`),
    create: (data: Partial<FAQ>) => 
      fetcher<FAQ>('/faqs', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: Partial<FAQ>) => 
      fetcher<FAQ>(`/faqs/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: string) => 
      fetcher<void>(`/faqs/${id}`, { method: 'DELETE' }),
  },
  feedback: {
    list: (params?: Record<string, string>) => {
      const query = new URLSearchParams(params).toString();
      return fetcher<PaginatedFeedback>(`/feedback${query ? `?${query}` : ''}`);
    },
  },
};
