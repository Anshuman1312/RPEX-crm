import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { ActivityRecord } from "@/features/activity-timeline/types/activity";

const actionToneMap: Record<string, "success" | "info" | "warning" | "danger"> = {
  created: "success",
  updated: "info",
  deleted: "danger",
  stage_changed: "warning",
  status_changed: "warning",
  assigned: "info",
  exported: "success",
  login: "info",
  logout: "info"
};

export const activityColumns: ColumnDef<ActivityRecord>[] = [
  { accessorKey: "id", header: "Event ID" },
  { accessorKey: "occurredAt", header: "Time" },
  { accessorKey: "actor", header: "Actor" },
  { accessorKey: "module", header: "Module" },
  {
    accessorKey: "action",
    header: "Action",
    cell: ({ row }) => (
      <StatusBadge
        label={row.original.action.replace(/_/g, " ")}
        tone={actionToneMap[row.original.action] ?? "info"}
      />
    )
  },
  { accessorKey: "subject", header: "Subject" },
  { accessorKey: "detail", header: "Detail" }
];
