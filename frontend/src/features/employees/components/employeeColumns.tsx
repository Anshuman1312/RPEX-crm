import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { EmployeeRecord, EmployeeStatus } from "@/features/employees/types/employee";

const statusToneMap: Record<EmployeeStatus, "success" | "warning" | "info"> = {
  Active: "success",
  "On Leave": "warning",
  Inactive: "info"
};

export function buildEmployeeColumns(
  onStatusChange: (employeeId: string, status: string) => void,
  onRoleChange: (employeeId: string, roleId: string) => void,
  isSuperAdmin: boolean,
  rolesList: Array<{ id: string; name: string }>
): ColumnDef<EmployeeRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Employee ID"
    },
    {
      accessorKey: "fullName",
      header: "Name"
    },
    {
      accessorKey: "email",
      header: "Email"
    },
    {
      accessorKey: "roleName",
      header: "Role",
      cell: ({ row }) => {
        const currentRoleId = row.original.roleId;
        const currentRoleName = row.original.roleName || "No Role";
        if (isSuperAdmin) {
          return (
            <select
              className="h-8 rounded border bg-background px-2 text-xs"
              onChange={event => onRoleChange(row.original.id, event.target.value)}
              value={currentRoleId || ""}
            >
              <option value="">No Role</option>
              {rolesList.map(r => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          );
        }
        return <span className="text-sm">{currentRoleName}</span>;
      }
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          {isSuperAdmin && (
            <select
              className="h-8 rounded border bg-background px-2 text-xs"
              onChange={event =>
                onStatusChange(row.original.id, event.target.value)
              }
              value={row.original.status}
            >
              {(["Active", "Inactive"] as string[]).map(status => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          )}
        </div>
      )
    },
    {
      accessorKey: "joiningDate",
      header: "Joining Date"
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
