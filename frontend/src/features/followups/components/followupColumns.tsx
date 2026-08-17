import { ColumnDef } from "@tanstack/react-table";
import { Button, StatusBadge, Tooltip } from "@/components";
import { Edit, Eye, Trash2 } from "lucide-react";
import {
  FollowUpRecord,
  FollowUpStatus,
} from "@/features/followups/types/followup";

const priorityTextMap: Record<number, string> = {
  0: "Low",
  1: "Medium",
  2: "High"
};

const priorityToneMap: Record<number, "info" | "warning" | "danger" | "success"> = {
  0: "info",
  1: "warning",
  2: "danger"
};

const statusTextMap: Record<FollowUpStatus, string> = {
  scheduled: "Scheduled",
  completed: "Completed",
  cancelled: "Cancelled",
  overdue: "Overdue"
};

const statusToneMap: Record<FollowUpStatus, "info" | "warning" | "danger" | "success"> = {
  scheduled: "info",
  completed: "success",
  cancelled: "danger",
  overdue: "warning"
};

export function buildFollowUpColumns(
  onStatusChange: (followUpId: string, status: FollowUpStatus) => void,
  onEdit: (followup: FollowUpRecord) => void,
  onDelete: (followUpId: string) => void,
  onView: (followup: FollowUpRecord) => void
): ColumnDef<FollowUpRecord>[] {
  return [
    {
      accessorKey: "followup_number",
      header: "FollowUp Id",
      cell: ({ row }) => (
        <span className="font-semibold text-primary font-mono text-xs">
          {row.original.followup_number}
        </span>
      )
    },
    {
      accessorKey: "subject",
      header: "Subject"
    },
    {
      accessorKey: "type",
      header: "Type",
      cell: ({ row }) => (
        <span className="capitalize">{row.original.type?.replace("_", " ")}</span>
      )
    },
    {
      accessorKey: "scheduled_at",
      header: "Scheduled At",
      cell: ({ row }) => {
        const d = row.original.scheduled_at;
        return d ? d.replace("T", " ").slice(0, 16) : "-";
      }
    },
    {
      accessorKey: "priority",
      header: "Priority",
      cell: ({ row }) => {
        const priVal = row.original.priority;
        const text = priorityTextMap[priVal] || "Medium";
        const tone = priorityToneMap[priVal] || "warning";
        return <StatusBadge label={text} tone={tone} />;
      }
    },
    {
      accessorKey: "is_critical",
      header: "Critical",
      cell: ({ row }) => (
        <span className={row.original.is_critical ? "text-red-500 font-bold" : "text-muted-foreground"}>
          {row.original.is_critical ? "Yes" : "No"}
        </span>
      )
    },
    {
      accessorKey: "lead_id",
      header: "Lead/Customer Reference",
      cell: ({ row }) => {
        const lead = row.original.lead_id;
        const cust = row.original.customer_id;
        if (!lead && !cust) return <span className="text-muted-foreground">-</span>;
        const val = lead ? `Lead: ${lead.slice(0, 8)}...` : `Cust: ${cust!.slice(0, 8)}...`;
        return (
          <Tooltip content={lead ? `Lead ID: ${lead}` : `Customer ID: ${cust}`}>
            <span className="cursor-help font-mono text-xs text-muted-foreground underline decoration-dotted">
              {val}
            </span>
          </Tooltip>
        );
      }
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge
            label={statusTextMap[row.original.status] || "Scheduled"}
            tone={statusToneMap[row.original.status] || "info"}
          />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event => onStatusChange(row.original.id, event.target.value as FollowUpStatus)}
            value={row.original.status}
          >
            {(["scheduled", "completed", "cancelled", "overdue"] as FollowUpStatus[]).map(status => (
              <option key={status} value={status}>
                {statusTextMap[status]}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex items-center gap-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onView(row.original)}
            className="h-8 w-8 p-0"
            title="View Follow-up Details"
          >
            <Eye className="h-4 w-4 text-muted-foreground hover:text-foreground" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(row.original)}
            className="h-8 w-8 p-0"
            title="Edit Follow-up"
          >
            <Edit className="h-4 w-4 text-muted-foreground hover:text-foreground" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onDelete(row.original.id)}
            className="h-8 w-8 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
            title="Delete Follow-up"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];
}
