import { ColumnDef } from "@tanstack/react-table";
import { CustomerRecord } from "@/features/customers/types/customer";
import { Button } from "@/components/ui/button";
import { Edit, Eye, Trash2 } from "lucide-react";

export function buildCustomerColumns(
  onEdit: (customer: CustomerRecord) => void,
  onDelete: (customerId: string) => void,
  onView: (customer: CustomerRecord) => void
): ColumnDef<CustomerRecord>[] {
  return [
    {
      accessorKey: "customer_number",
      header: "Customer ID",
      cell: ({ row }) => (
        <span className="font-semibold text-muted-foreground font-mono text-xs">
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
      accessorKey: "created_at",
      header: "Created At",
      cell: ({ row }) => {
        try {
          return new Date(row.original.created_at).toLocaleDateString();
        } catch {
          return "-";
        }
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex items-center gap-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onView(row.original)}
            className="h-8 w-8 p-0"
            title="View Customer Details"
          >
            <Eye className="h-4 w-4 text-muted-foreground hover:text-foreground" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(row.original)}
            className="h-8 w-8 p-0"
            title="Edit Customer"
          >
            <Edit className="h-4 w-4 text-muted-foreground hover:text-foreground" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onDelete(row.original.id)}
            className="h-8 w-8 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
            title="Delete Customer"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];
}
