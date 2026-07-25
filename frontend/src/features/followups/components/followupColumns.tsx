import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  FollowUpPriority,
  FollowUpRecord,
  FollowUpStatus
} from "@/features/followups/types/followup";

const priorityToneMap: Record<FollowUpPriority, "info" | "warning" | "danger" | "success"> = {
  Low: "info",
  Medium: "warning",
  High: "danger"
};

const statusToneMap: Record<FollowUpStatus, "info" | "warning" | "danger" | "success"> = {
  Pending: "warning",
  Done: "success",
  Missed: "danger",
  Rescheduled: "info"
};

export function buildFollowUpColumns(
  onStatusChange: (followUpId: string, status: FollowUpStatus) => void
): ColumnDef<FollowUpRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Follow-up ID"
    },
    {
      accessorKey: "leadName",
      header: "Lead"
    },
    {
      accessorKey: "owner",
      header: "Owner"
    },
    {
      id: "lastFollowUpDate",
      accessorKey: "updatedAt",
      header: "Last Follow-up Date"
    },
    {
      id: "nextFollowUpDate",
      header: "Next Follow-up Date",
      cell: ({ row }) => row.original.scheduledAt?.slice(0, 10) || "-"
    },
    {
      id: "followUpTime",
      header: "Follow-up Time",
      cell: ({ row }) => row.original.scheduledAt?.slice(11, 16) || "-"
    },
    {
      accessorKey: "channel",
      header: "Follow-up Mode"
    },
    {
      accessorKey: "priority",
      header: "Priority",
      cell: ({ row }) => (
        <StatusBadge label={row.original.priority} tone={priorityToneMap[row.original.priority]} />
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
            onChange={event => onStatusChange(row.original.id, event.target.value as FollowUpStatus)}
            value={row.original.status}
          >
            {(["Pending", "Done", "Missed", "Rescheduled"] as FollowUpStatus[]).map(status => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      accessorKey: "notes",
      header: "Follow-up Notes"
    }
  ];
}
