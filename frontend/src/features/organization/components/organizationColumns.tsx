import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { OrganizationRecord, OrganizationStatus } from "@/features/organization/types/organization";

const statusToneMap: Record<OrganizationStatus, "success" | "warning" | "info"> = {
  Active: "success",
  Suspended: "warning",
  Inactive: "info"
};

export function buildOrganizationColumns(
  onStatusChange: (organizationId: string, status: OrganizationStatus) => void
): ColumnDef<OrganizationRecord>[] {
  return [
    { accessorKey: "id", header: "Org ID" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "industry", header: "Industry" },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={e => onStatusChange(row.original.id, e.target.value as OrganizationStatus)}
            value={row.original.status}
          >
            {(["Active", "Suspended", "Inactive"] as OrganizationStatus[]).map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      )
    },
    { accessorKey: "primaryContact", header: "Contact" },
    { accessorKey: "email", header: "Email" },
    { accessorKey: "city", header: "City" },
    { accessorKey: "employeeCount", header: "Employees" },
    { accessorKey: "createdAt", header: "Created" },
    { accessorKey: "updatedAt", header: "Updated" }
  ];
}
