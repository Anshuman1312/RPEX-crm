import { ColumnDef } from "@tanstack/react-table";
import { CustomerRecord } from "@/features/customers/types/customer";

export function buildCustomerColumns(): ColumnDef<CustomerRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Customer ID"
    },
    {
      id: "fullName",
      header: "Client Details",
      cell: ({ row }) => (
        <div>
          <span className="font-semibold text-xs text-muted-foreground mr-1">{row.original.title || "Mr."}</span>
          <span className="font-medium">{row.original.name}</span>
        </div>
      )
    },
    {
      accessorKey: "phone",
      header: "Mobile (Primary)"
    },
    {
      accessorKey: "alternatePhone",
      header: "Alternate Mobile",
      cell: ({ row }) => row.original.alternatePhone || "-"
    },
    {
      accessorKey: "email",
      header: "Email ID",
      cell: ({ row }) => row.original.email || "-"
    },
    {
      accessorKey: "occupation",
      header: "Occupation",
      cell: ({ row }) => row.original.occupation || "-"
    },
    {
      accessorKey: "address",
      header: "Address",
      cell: ({ row }) => row.original.address || "-"
    },
    {
      accessorKey: "budgetRange",
      header: "Budget Range",
      cell: ({ row }) => row.original.budgetRange || "-"
    },
    {
      accessorKey: "timeDuration",
      header: "Time Duration",
      cell: ({ row }) => row.original.timeDuration || "-"
    },
    {
      accessorKey: "purpose",
      header: "Purpose"
    },
    {
      accessorKey: "propertyType",
      header: "Property Type"
    },
    {
      accessorKey: "remarks",
      header: "Remarks",
      cell: ({ row }) => row.original.remarks || "-"
    }
  ];
}
