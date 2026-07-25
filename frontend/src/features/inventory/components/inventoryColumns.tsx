import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  InventoryStatus,
  InventoryUnitRecord
} from "@/features/inventory/types/inventory";

const statusToneMap: Record<InventoryStatus, "success" | "warning" | "info"> = {
  Available: "success",
  Reserved: "warning",
  Sold: "info"
};

export function buildInventoryColumns(
  onStatusChange: (unitId: string, status: InventoryStatus) => void
): ColumnDef<InventoryUnitRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Unit ID"
    },
    {
      accessorKey: "unitCode",
      header: "Unit Code"
    },
    {
      accessorKey: "project",
      header: "Project"
    },
    {
      accessorKey: "category",
      header: "Category"
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event =>
              onStatusChange(row.original.id, event.target.value as InventoryStatus)
            }
            value={row.original.status}
          >
            {(["Available", "Reserved", "Sold"] as InventoryStatus[]).map(status => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      accessorKey: "sizeSqFt",
      header: "Size",
      cell: ({ row }) => `${row.original.sizeSqFt} sq ft`
    },
    {
      accessorKey: "price",
      header: "Price",
      cell: ({ row }) =>
        new Intl.NumberFormat("en-IN", {
          style: "currency",
          currency: "INR",
          maximumFractionDigits: 0
        }).format(row.original.price)
    },
    {
      accessorKey: "assignedAgent",
      header: "Agent"
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
