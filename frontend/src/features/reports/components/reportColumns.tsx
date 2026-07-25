import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import { ReportRecord, ReportStatus } from "@/features/reports/types/report";

const statusToneMap: Record<ReportStatus, "info" | "warning" | "success" | "danger"> = {
  Draft: "info",
  Ready: "warning",
  Exported: "success",
  Failed: "danger"
};

export function buildReportColumns(
  onStatusChange: (reportId: string, status: ReportStatus) => void
): ColumnDef<ReportRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Report ID"
    },
    {
      accessorKey: "title",
      header: "Title"
    },
    {
      accessorKey: "type",
      header: "Type"
    },
    {
      accessorKey: "range",
      header: "Range"
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event => onStatusChange(row.original.id, event.target.value as ReportStatus)}
            value={row.original.status}
          >
            {(["Draft", "Ready", "Exported", "Failed"] as ReportStatus[]).map(status => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>
      )
    },
    {
      accessorKey: "owner",
      header: "Owner"
    },
    {
      accessorKey: "generatedAt",
      header: "Generated"
    },
    {
      accessorKey: "rows",
      header: "Rows"
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
