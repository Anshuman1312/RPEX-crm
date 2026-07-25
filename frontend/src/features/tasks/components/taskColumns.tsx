import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  TaskPriority,
  TaskRecord,
  TaskStatus
} from "@/features/tasks/types/task";

const priorityToneMap: Record<TaskPriority, "info" | "warning" | "danger" | "success"> = {
  Low: "info",
  Medium: "success",
  High: "warning",
  Critical: "danger"
};

const statusToneMap: Record<TaskStatus, "info" | "warning" | "danger" | "success"> = {
  Backlog: "info",
  "In Progress": "warning",
  Blocked: "danger",
  Completed: "success"
};

export function buildTaskColumns(
  onStatusChange: (taskId: string, status: TaskStatus) => void
): ColumnDef<TaskRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Task ID"
    },
    {
      accessorKey: "title",
      header: "Title"
    },
    {
      accessorKey: "module",
      header: "Module"
    },
    {
      accessorKey: "assignee",
      header: "Assignee"
    },
    {
      accessorKey: "dueDate",
      header: "Due Date"
    },
    {
      accessorKey: "priority",
      header: "Priority",
      cell: ({ row }) => (
        <StatusBadge
          label={row.original.priority}
          tone={priorityToneMap[row.original.priority]}
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
            onChange={event => onStatusChange(row.original.id, event.target.value as TaskStatus)}
            value={row.original.status}
          >
            {(["Backlog", "In Progress", "Blocked", "Completed"] as TaskStatus[]).map(status => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      accessorKey: "effortPoints",
      header: "Points"
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
