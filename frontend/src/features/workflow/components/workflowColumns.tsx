import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { WorkflowRecord, WorkflowStatus } from "@/features/workflow/types/workflow";

const statusToneMap: Record<WorkflowStatus, "success" | "warning" | "info"> = {
  Active: "success",
  Paused: "warning",
  Draft: "info"
};

export function buildWorkflowColumns(
  onStatusChange: (workflowId: string, status: WorkflowStatus) => void
): ColumnDef<WorkflowRecord>[] {
  return [
    { accessorKey: "id", header: "Workflow ID" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "trigger", header: "Trigger" },
    { accessorKey: "action", header: "Action" },
    { accessorKey: "module", header: "Module" },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={e => onStatusChange(row.original.id, e.target.value as WorkflowStatus)}
            value={row.original.status}
          >
            {(["Active", "Paused", "Draft"] as WorkflowStatus[]).map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      )
    },
    { accessorKey: "runsTotal", header: "Runs" },
    { accessorKey: "lastRunAt", header: "Last Run" },
    { accessorKey: "createdAt", header: "Created" }
  ];
}
