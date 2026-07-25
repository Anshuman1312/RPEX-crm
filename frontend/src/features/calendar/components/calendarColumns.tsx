import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  CalendarEventRecord,
  CalendarEventStatus
} from "@/features/calendar/types/calendar";

const eventStatusToneMap: Record<
  CalendarEventStatus,
  "warning" | "success" | "danger" | "info"
> = {
  Upcoming: "warning",
  Completed: "success",
  Missed: "danger",
  Cancelled: "info"
};

export function buildCalendarColumns(
  onStatusChange: (eventId: string, status: CalendarEventStatus) => void
): ColumnDef<CalendarEventRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Event ID"
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
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={eventStatusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event =>
              onStatusChange(row.original.id, event.target.value as CalendarEventStatus)
            }
            value={row.original.status}
          >
            {(["Upcoming", "Completed", "Missed", "Cancelled"] as CalendarEventStatus[]).map(
              status => (
                <option key={status} value={status}>
                  {status}
                </option>
              )
            )}
          </select>
        </div>
      )
    },
    {
      accessorKey: "owner",
      header: "Owner"
    },
    {
      accessorKey: "attendee",
      header: "Attendee"
    },
    {
      accessorKey: "eventAt",
      header: "Event At"
    },
    {
      accessorKey: "location",
      header: "Location"
    },
    {
      accessorKey: "linkedModule",
      header: "Module"
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
