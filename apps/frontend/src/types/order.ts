export interface OrderItem {
  name: string;
  quantity: number;
  price?: number | null;
}

export interface Order {
  id: string;
  callId: string;
  customerId: string | null;
  items: OrderItem[];
  customerName: string | null;
  phone: string | null;
  address: string | null;
  orderType: string;
  status: string;
  notes: string;
  createdAt: string;
  updatedAt: string;
}

export interface PaginatedOrders {
  data: Order[];
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}
