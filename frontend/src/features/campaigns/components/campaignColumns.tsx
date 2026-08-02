import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  CampaignRecord,
  CampaignStatus
} from "@/features/campaigns/types/campaign";

const statusToneMap: Record<CampaignStatus, "info" | "warning" | "danger" | "success"> = {
  Draft: "info",
  Running: "success",
  Paused: "warning",
  Completed: "danger"
};

export function buildCampaignColumns(): ColumnDef<CampaignRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Campaign ID"
    },
    {
      accessorKey: "name",
      header: "Campaign Name"
    },
    {
      accessorKey: "type",
      header: "Type"
    },
    {
      accessorKey: "platform",
      header: "Platform"
    },
    {
      accessorKey: "budget",
      header: "Budget"
    },
    {
      accessorKey: "start_date",
      header: "Start Date"
    },
    {
      accessorKey: "end_date",
      header: "End Date"
    },
    {
      accessorKey: "extra_data",
      header: "Extra Data",
      cell: ({ row }) => (
        <pre className="font-mono text-xs max-w-[200px] truncate">
          {JSON.stringify(row.original.extra_data)}
        </pre>
      )
    },
    {
      accessorKey: "leadsGenerated",
      header: "Leads"
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
        </div>
      )
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
