import { z } from "zod";
import { paymentMethodOptions } from "@/features/payments/constants/paymentOptions";

export const createPaymentSchema = z.object({
  bookingId: z.string().min(2, "Booking id is required"),
  customerName: z.string().min(2, "Customer name is required"),
  projectName: z.string().min(2, "Project name is required"),
  amount: z.coerce.number().positive("Amount must be greater than zero"),
  method: z.enum(paymentMethodOptions.filter(option => option !== "All") as ["UPI", "Bank Transfer", "Cheque", "Card"]),
  transactionDate: z.string().min(10, "Transaction date is required"),
  owner: z.string().min(2, "Payment owner is required")
});

export type CreatePaymentFormValues = z.infer<typeof createPaymentSchema>;
