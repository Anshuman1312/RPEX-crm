import {
  CreatePaymentInput,
  PaymentListResponse,
  PaymentRecord,
  PaymentStats
} from "@/features/payments/types/payment";

function formatDate(offset: number) {
  const date = new Date();
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

export const initialPaymentRecords: PaymentRecord[] = [
  {
    id: "PY-6101",
    bookingId: "BK-5101",
    customerName: "Ishita Rao",
    projectName: "Skyline Heights Phase 2",
    amount: 1200000,
    method: "Bank Transfer",
    status: "Received",
    transactionDate: formatDate(-8),
    owner: "Rohan",
    updatedAt: formatDate(-1)
  },
  {
    id: "PY-6102",
    bookingId: "BK-5102",
    customerName: "Aarav Mehta",
    projectName: "Riverfront Residency",
    amount: 900000,
    method: "UPI",
    status: "Pending",
    transactionDate: formatDate(-4),
    owner: "Riya",
    updatedAt: formatDate(-2)
  },
  {
    id: "PY-6103",
    bookingId: "BK-5103",
    customerName: "Neel Jain",
    projectName: "Orchid Greens",
    amount: 750000,
    method: "Cheque",
    status: "Failed",
    transactionDate: formatDate(-2),
    owner: "Aman",
    updatedAt: formatDate(-1)
  },
  {
    id: "PY-6104",
    bookingId: "BK-5104",
    customerName: "Kavya Sharma",
    projectName: "Emerald Business Park",
    amount: 650000,
    method: "Card",
    status: "Refunded",
    transactionDate: formatDate(-12),
    owner: "Priya",
    updatedAt: formatDate(-5)
  }
];

export function buildPaymentStats(records: PaymentRecord[]): PaymentStats {
  return {
    totalTransactions: records.length,
    receivedCount: records.filter(record => record.status === "Received").length,
    pendingCount: records.filter(record => record.status === "Pending").length,
    totalReceivedAmount: records
      .filter(record => record.status === "Received")
      .reduce((sum, record) => sum + record.amount, 0)
  };
}

export function buildPaymentListResponse(records: PaymentRecord[]): PaymentListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildPaymentStats(records)
  };
}

export function createPaymentRecord(payload: CreatePaymentInput, index: number): PaymentRecord {
  return {
    id: `PY-${6100 + index}`,
    bookingId: payload.bookingId,
    customerName: payload.customerName,
    projectName: payload.projectName,
    amount: payload.amount,
    method: payload.method,
    status: "Pending",
    transactionDate: payload.transactionDate,
    owner: payload.owner,
    updatedAt: new Date().toISOString().slice(0, 10)
  };
}
