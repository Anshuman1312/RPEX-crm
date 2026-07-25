import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { BookingRecord } from "@/features/bookings/types/booking";

export function buildBookingColumns(): ColumnDef<BookingRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Booking ID"
    },
    {
      accessorKey: "bookingInterested",
      header: "Booking Interested"
    },
    {
      accessorKey: "bookingAmount",
      header: "Booking Amount",
      cell: ({ row }) =>
        new Intl.NumberFormat("en-IN", {
          style: "currency",
          currency: "INR",
          maximumFractionDigits: 0
        }).format(row.original.bookingAmount)
    },
    {
      accessorKey: "preferredPaymentMode",
      header: "Preferred Payment Mode"
    },
    {
      accessorKey: "financeRequired",
      header: "Finance Required",
      cell: ({ row }) => (
        <StatusBadge
          label={row.original.financeRequired ? "Yes" : "No"}
          tone={row.original.financeRequired ? "success" : "info"}
        />
      )
    },
    {
      accessorKey: "loanAssistanceRequired",
      header: "Loan Assistance Required",
      cell: ({ row }) => (
        <StatusBadge
          label={row.original.loanAssistanceRequired ? "Yes" : "No"}
          tone={row.original.loanAssistanceRequired ? "success" : "info"}
        />
      )
    }
  ];
}
