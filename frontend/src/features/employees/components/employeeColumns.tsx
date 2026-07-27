import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { EmployeeRecord, EmployeeStatus } from "@/features/employees/types/employee";

const statusToneMap: Record<EmployeeStatus, "success" | "warning" | "info"> = {
  Active: "success",
  "On Leave": "warning",
  Inactive: "info"
};

export function buildEmployeeColumns(
  onStatusChange: (employeeId: string, status: EmployeeStatus) => void
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
      accessorKey: "department",
      header: "Department"
    },
    {
      accessorKey: "band",
      header: "Band"
    },
    {
      accessorKey: "manager",
      header: "Manager"
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
              onStatusChange(row.original.id, event.target.value as EmployeeStatus)
            }
            value={row.original.status}
          >
            {(["Active", "On Leave", "Inactive"] as EmployeeStatus[]).map(status => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
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
