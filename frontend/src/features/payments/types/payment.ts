export type PaymentMethod = "UPI" | "Bank Transfer" | "Cheque" | "Card";
export type PaymentStatus = "Pending" | "Received" | "Failed" | "Refunded";

export interface PaymentRecord {
  id: string;
  bookingId: string;
  customerName: string;
  projectName: string;
  amount: number;
  method: PaymentMethod;
  status: PaymentStatus;
  transactionDate: string;
  owner: string;
  updatedAt: string;
}

export interface PaymentFilters {
  search?: string;
  method?: PaymentMethod | "All";
  status?: PaymentStatus | "All";
}

export interface PaymentStats {
  totalTransactions: number;
  receivedCount: number;
  pendingCount: number;
  totalReceivedAmount: number;
}

export interface PaymentListResponse {
  items: PaymentRecord[];
  total: number;
  stats: PaymentStats;
}

export interface CreatePaymentInput {
  bookingId: string;
  customerName: string;
  projectName: string;
  amount: number;
  method: PaymentMethod;
  transactionDate: string;
  owner: string;
}
