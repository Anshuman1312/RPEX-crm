import { Button, StatusBadge, Tooltip } from "@/components";
import { LeadRecord, LeadStatus } from "@/features/leads/types/lead";
import { ColumnDef } from "@tanstack/react-table";
import { Edit, Trash2 } from "lucide-react";

const statusToneMap: Record<LeadStatus, "info" | "success" | "warning" | "neutral" | "danger"> = {
  New: "info",
  Qualified: "warning",
  Negotiation: "neutral",
  Won: "success",
  "Future Perspective": "danger"
};

export function buildLeadColumns(
  onStatusChange: (leadId: string, status: LeadStatus) => void,
  onEdit: (lead: LeadRecord) => void,
  onDelete: (leadId: string) => void
): ColumnDef<LeadRecord>[] {
  return [
    {
      accessorKey: "fullName",
      header: "Name"
    },
    {
      accessorKey: "email",
      header: "Email"
    },
    {
      accessorKey: "source",
      header: "Source"
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event => onStatusChange(row.original.id, event.target.value as LeadStatus)}
            value={row.original.status}
          >
            {([
              "New",
              "Qualified",
              "Negotiation",
              "Won",
              "Future Perspective"
            ] as LeadStatus[]).map(status => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      accessorKey: "priority",
      header: "Priority",
      cell: ({ row }) => {
        const priority = row.original.priority || "Warm";
        const priorityIconMap = {
          Hot: "Hot",
          Warm: "Warm",
          Cold: "Cold"
        };
        const priorityToneMap = {
          Hot: "danger" as const,
          Warm: "warning" as const,
          Cold: "info" as const
        };
        return (
          <StatusBadge label={priorityIconMap[priority]} tone={priorityToneMap[priority]} />
        );
      }
    },
    {
      accessorKey: "assignedToUserId",
      header: "Assigned To",
      cell: ({ row }) => {
        const value = row.original.assignedToUserId;
        if (!value) return <span className="text-muted-foreground">-</span>;
        
        const truncated = value.length > 12 
          ? `${value.slice(0, 8)}...${value.slice(-4)}`
          : value;
          
        return (
          <Tooltip content={value}>
            <span className="cursor-help font-mono text-xs text-muted-foreground underline decoration-dotted">
              {truncated}
            </span>
          </Tooltip>
        );
      }
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
      accessorKey: "nextFollowupAt",
      header: "Next Follow-up"
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex items-center gap-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(row.original)}
            className="h-8 w-8 p-0"
          >
            <Edit className="h-4 w-4 text-muted-foreground hover:text-foreground" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onDelete(row.original.id)}
            className="h-8 w-8 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ];
}

