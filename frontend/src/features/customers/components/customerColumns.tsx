import { ColumnDef } from "@tanstack/react-table";
import { CustomerRecord } from "@/features/customers/types/customer";

export function buildCustomerColumns(): ColumnDef<CustomerRecord>[] {
  return [
    {
      accessorKey: "customer_number",
      header: "Customer ID",
      cell: ({ row }) => (
        <span className="font-semibold text-primary font-mono text-xs">
          {row.original.customer_number}
        </span>
      )
    },
    {
      id: "fullName",
      header: "Client Name",
      cell: ({ row }) => (
        <span className="font-medium">
          {row.original.first_name} {row.original.last_name}
        </span>
      )
    },
    {
      accessorKey: "phone",
      header: "Mobile"
    },
    {
      accessorKey: "alternate_phone",
      header: "Alternate Mobile",
      cell: ({ row }) => row.original.alternate_phone || "-"
    },
    {
      accessorKey: "email",
      header: "Email ID"
    },
    {
      accessorKey: "company_name",
      header: "Company Name",
      cell: ({ row }) => row.original.company_name || "-"
    },
    {
      accessorKey: "customer_type",
      header: "Type",
      cell: ({ row }) => (
        <span className="capitalize">{(row.original.customer_type || "").toLowerCase()}</span>
      )
    },
    {
      accessorKey: "preferred_contact_method",
      header: "Preferred Contact",
      cell: ({ row }) => {
        const method = row.original.preferred_contact_method;
        return method ? <span className="capitalize">{method.toLowerCase()}</span> : "-";
      }
    },
    {
      accessorKey: "preferred_language",
      header: "Language",
      cell: ({ row }) => (
        <span className="uppercase text-xs font-medium">{row.original.preferred_language || "EN"}</span>
      )
    },
    {
      accessorKey: "gstin",
      header: "GSTIN",
      cell: ({ row }) => row.original.gstin || "-"
    },
    {
      accessorKey: "pan",
      header: "PAN",
      cell: ({ row }) => row.original.pan || "-"
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = (row.original.status || "").toLowerCase();
        let colorClass = "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300";
        if (status === "inactive") {
          colorClass = "bg-gray-100 text-gray-800 dark:bg-gray-800/30 dark:text-gray-300";
        } else if (status === "blacklisted") {
          colorClass = "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300";
        }
        return (
          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${colorClass}`}>
            {row.original.status}
          </span>
        );
      }
    },
    {
      accessorKey: "notes",
      header: "Notes",
      cell: ({ row }) => (
        <span className="block max-w-[200px] truncate" title={row.original.notes}>
          {row.original.notes || "-"}
        </span>
      )
    },
    {
      accessorKey: "created_at",
      header: "Created At",
      cell: ({ row }) => {
        try {
          return new Date(row.original.created_at).toLocaleDateString();
        } catch {
          return "-";
        }
      }
    }
  ];
}
