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

export function buildCampaignColumns(
  onStatusChange: (campaignId: string, status: CampaignStatus) => void
): ColumnDef<CampaignRecord>[] {
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
      accessorKey: "channel",
      header: "Channel"
    },
    {
      accessorKey: "owner",
      header: "Owner"
    },
    {
      accessorKey: "budget",
      header: "Budget"
    },
    {
      accessorKey: "startDate",
      header: "Start"
    },
    {
      accessorKey: "endDate",
      header: "End"
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
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event => onStatusChange(row.original.id, event.target.value as CampaignStatus)}
            value={row.original.status}
          >
            {(["Draft", "Running", "Paused", "Completed"] as CampaignStatus[]).map(status => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
