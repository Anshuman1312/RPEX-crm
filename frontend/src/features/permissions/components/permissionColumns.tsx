import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { PermissionRecord, PermissionStatus } from "@/features/permissions/types/permission";

const statusToneMap: Record<PermissionStatus, "success" | "info"> = {
  Active: "success",
  Inactive: "info"
};

const actionToneMap: Record<string, "success" | "info" | "warning" | "danger"> = {
  view: "info",
  create: "success",
  edit: "warning",
  delete: "danger"
};

export function buildPermissionColumns(
  onStatusChange: (permissionId: string, status: PermissionStatus) => void
): ColumnDef<PermissionRecord>[] {
  return [
    { accessorKey: "id", header: "Permission ID" },
    { accessorKey: "key", header: "Key" },
    { accessorKey: "module", header: "Module" },
    {
      accessorKey: "action",
      header: "Action",
      cell: ({ row }) => (
        <StatusBadge
          label={row.original.action}
          tone={actionToneMap[row.original.action]}
        />
      )
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={e =>
              onStatusChange(row.original.id, e.target.value as PermissionStatus)
            }
            value={row.original.status}
          >
            {(["Active", "Inactive"] as PermissionStatus[]).map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      )
    },
    { accessorKey: "description", header: "Description" },
    { accessorKey: "assignedRoles", header: "Roles" },
    { accessorKey: "createdAt", header: "Created" }
  ];
}
