import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  ProjectHealth,
  ProjectRecord
} from "@/features/projects/types/project";

const healthToneMap: Record<ProjectHealth, "success" | "warning" | "danger"> = {
  "On Track": "success",
  Watchlist: "warning",
  Delayed: "danger"
};

export function buildProjectColumns(
  onHealthChange: (projectId: string, health: ProjectHealth) => void
): ColumnDef<ProjectRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Project ID"
    },
    {
      accessorKey: "name",
      header: "Project"
    },
    {
      accessorKey: "client",
      header: "Client"
    },
    {
      accessorKey: "phase",
      header: "Phase"
    },
    {
      accessorKey: "health",
      header: "Health",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.health} tone={healthToneMap[row.original.health]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event =>
              onHealthChange(row.original.id, event.target.value as ProjectHealth)
            }
            value={row.original.health}
          >
            {(["On Track", "Watchlist", "Delayed"] as ProjectHealth[]).map(health => (
              <option key={health} value={health}>
                {health}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      accessorKey: "projectManager",
      header: "Manager"
    },
    {
      accessorKey: "progress",
      header: "Progress",
      cell: ({ row }) => `${row.original.progress}%`
    },
    {
      accessorKey: "budget",
      header: "Budget",
      cell: ({ row }) =>
        new Intl.NumberFormat("en-IN", {
          style: "currency",
          currency: "INR",
          maximumFractionDigits: 0
        }).format(row.original.budget)
    },
    {
      accessorKey: "targetHandover",
      header: "Target Handover"
    },
    {
      accessorKey: "lastUpdated",
      header: "Last Updated"
    }
  ];
}
