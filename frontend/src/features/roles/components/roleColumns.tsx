import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { RoleRecord, RoleStatus } from "@/features/roles/types/role";

const statusToneMap: Record<RoleStatus, "success" | "info"> = {
  Active: "success",
  Inactive: "info"
};

export function buildRoleColumns(
  onStatusChange: (roleId: string, status: RoleStatus) => void
): ColumnDef<RoleRecord>[] {
  return [
    { accessorKey: "id", header: "Role ID" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "scope", header: "Scope" },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={e => onStatusChange(row.original.id, e.target.value as RoleStatus)}
            value={row.original.status}
          >
            {(["Active", "Inactive"] as RoleStatus[]).map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      )
    },
    { accessorKey: "description", header: "Description" },
    { accessorKey: "assignedUsers", header: "Users" },
    {
      id: "permissionsCount",
      header: "Permissions",
      cell: ({ row }) => `${row.original.permissions.length} modules`
    },
    { accessorKey: "createdAt", header: "Created" },
    { accessorKey: "updatedAt", header: "Updated" }
  ];
}
