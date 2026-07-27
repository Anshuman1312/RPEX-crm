import { PaymentMethod, PaymentStatus } from "@/features/payments/types/payment";

export const paymentMethodOptions: Array<PaymentMethod | "All"> = [
  "All",
  "UPI",
  "Bank Transfer",
  "Cheque",
  "Card"
];

export const paymentStatusOptions: Array<PaymentStatus | "All"> = [
  "All",
  "Pending",
  "Received",
  "Failed",
  "Refunded"
];
