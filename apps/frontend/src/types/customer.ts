export interface Customer {
  id: string;
  name: string | null;
  phone: string;
  address: string | null;
  callCount: number;
  lastCallAt: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface PaginatedCustomers {
  data: Customer[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
