import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  PaymentRecord,
  PaymentStatus
} from "@/features/payments/types/payment";

const paymentStatusToneMap: Record<PaymentStatus, "warning" | "success" | "danger" | "info"> = {
  Pending: "warning",
  Received: "success",
  Failed: "danger",
  Refunded: "info"
};

export function buildPaymentColumns(
  onStatusChange: (paymentId: string, status: PaymentStatus) => void
): ColumnDef<PaymentRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Payment ID"
    },
    {
      accessorKey: "bookingId",
      header: "Booking ID"
    },
    {
      accessorKey: "customerName",
      header: "Customer"
    },
    {
      accessorKey: "projectName",
      header: "Project"
    },
    {
      accessorKey: "amount",
      header: "Amount",
      cell: ({ row }) =>
        new Intl.NumberFormat("en-IN", {
          style: "currency",
          currency: "INR",
          maximumFractionDigits: 0
        }).format(row.original.amount)
    },
    {
      accessorKey: "method",
      header: "Method"
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge
            label={row.original.status}
            tone={paymentStatusToneMap[row.original.status]}
          />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event =>
              onStatusChange(row.original.id, event.target.value as PaymentStatus)
            }
            value={row.original.status}
          >
            {(["Pending", "Received", "Failed", "Refunded"] as PaymentStatus[]).map(status => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      accessorKey: "transactionDate",
      header: "Transaction Date"
    },
    {
      accessorKey: "owner",
      header: "Owner"
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
