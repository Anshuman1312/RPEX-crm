import { ColumnDef } from "@tanstack/react-table";
import { StatusBadge } from "@/components";
import {
  NotificationRecord,
  NotificationStatus,
  NotificationType
} from "@/features/notifications/types/notification";

const statusToneMap: Record<NotificationStatus, "warning" | "success" | "info"> = {
  Unread: "warning",
  Read: "success",
  Archived: "info"
};

const typeToneMap: Record<NotificationType, "info" | "warning" | "danger" | "success"> = {
  Reminder: "warning",
  Alert: "danger",
  Approval: "info",
  System: "success"
};

export function buildNotificationColumns(
  onStatusChange: (notificationId: string, status: NotificationStatus) => void
): ColumnDef<NotificationRecord>[] {
  return [
    {
      accessorKey: "id",
      header: "Notification ID"
    },
    {
      accessorKey: "title",
      header: "Title"
    },
    {
      accessorKey: "message",
      header: "Message"
    },
    {
      accessorKey: "type",
      header: "Type",
      cell: ({ row }) => <StatusBadge label={row.original.type} tone={typeToneMap[row.original.type]} />
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <StatusBadge label={row.original.status} tone={statusToneMap[row.original.status]} />
          <select
            className="h-8 rounded border bg-background px-2 text-xs"
            onChange={event =>
              onStatusChange(row.original.id, event.target.value as NotificationStatus)
            }
            value={row.original.status}
          >
            {(["Unread", "Read", "Archived"] as NotificationStatus[]).map(status => (
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
      accessorKey: "sourceModule",
      header: "Module"
    },
    {
      accessorKey: "createdAt",
      header: "Created"
    },
    {
      accessorKey: "updatedAt",
      header: "Updated"
    }
  ];
}
