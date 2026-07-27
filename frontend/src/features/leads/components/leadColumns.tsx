import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { LeadRecord, LeadStage } from "@/features/leads/types/lead";

const stageToneMap: Record<LeadStage, "info" | "success" | "warning" | "neutral" | "danger"> = {
  New: "info",
  Qualified: "warning",
  Negotiation: "neutral",
  Won: "success",
  "Future Perspective": "danger"
};

export function buildLeadColumns(
  onStageChange: (leadId: string, stage: LeadStage) => void
): ColumnDef<LeadRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Lead ID"
    },
    {
      accessorKey: "name",
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
      accessorKey: "stage",
      header: "Stage",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.stage} tone={stageToneMap[row.original.stage]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event => onStageChange(row.original.id, event.target.value as LeadStage)}
            value={row.original.stage}
          >
            {([
              "New",
              "Qualified",
              "Negotiation",
              "Won",
              "Future Perspective"
            ] as LeadStage[]).map(stage => (
              <option key={stage} value={stage}>
                {stage}
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
      accessorKey: "owner",
      header: "Owner"
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
      accessorKey: "nextFollowUp",
      header: "Next Follow-up"
    }
  ];
}
