import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  MeetingRecord,
  MeetingStatus
} from "@/features/meetings/types/meeting";

const meetingStatusToneMap: Record<MeetingStatus, "warning" | "success" | "danger" | "info"> = {
  Scheduled: "warning",
  Completed: "success",
  Cancelled: "danger",
  Rescheduled: "info"
};

export function buildMeetingColumns(
  onStatusChange: (meetingId: string, status: MeetingStatus) => void
): ColumnDef<MeetingRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Meeting ID"
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
          <StatusBadge
            label={row.original.status}
            tone={meetingStatusToneMap[row.original.status]}
          />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event =>
              onStatusChange(row.original.id, event.target.value as MeetingStatus)
            }
            value={row.original.status}
          >
            {(["Scheduled", "Completed", "Cancelled", "Rescheduled"] as MeetingStatus[]).map(
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
      accessorKey: "host",
      header: "Host"
    },
    {
      accessorKey: "attendee",
      header: "Attendee"
    },
    {
      accessorKey: "scheduledAt",
      header: "Scheduled At"
    },
    {
      accessorKey: "location",
      header: "Location"
    },
    {
      accessorKey: "notes",
      header: "Notes"
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
