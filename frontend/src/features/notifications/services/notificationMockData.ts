import {
  CreateNotificationInput,
  NotificationListResponse,
  NotificationRecord,
  NotificationStats
} from "@/features/notifications/types/notification";

function formatDateTime(offsetHours: number) {
  const date = new Date();
  date.setHours(date.getHours() + offsetHours);
  return date.toISOString().slice(0, 16);
}

export const initialNotificationRecords: NotificationRecord[] = [
  {
    id: "NT-10101",
    title: "Pending payment reminder",
    message: "Booking BK-5102 has pending tranche due tomorrow.",
    type: "Reminder",
    status: "Unread",
    owner: "Riya",
    sourceModule: "Payments",
    createdAt: formatDateTime(-2),
    updatedAt: formatDateTime(-2)
  },
  {
    id: "NT-10102",
    title: "Inventory alert",
    message: "Unit A-1204 has been reserved by another sales rep.",
    type: "Alert",
    status: "Read",
    owner: "Aman",
    sourceModule: "Inventory",
    createdAt: formatDateTime(-6),
    updatedAt: formatDateTime(-5)
  },
  {
    id: "NT-10103",
    title: "Approval required",
    message: "Discount exception request awaits manager decision.",
    type: "Approval",
    status: "Unread",
    owner: "Priya",
    sourceModule: "Bookings",
    createdAt: formatDateTime(-8),
    updatedAt: formatDateTime(-8)
  },
  {
    id: "NT-10104",
    title: "System maintenance notice",
    message: "Reporting service maintenance scheduled tonight.",
    type: "System",
    status: "Archived",
    owner: "All Users",
    sourceModule: "Platform",
    createdAt: formatDateTime(-20),
    updatedAt: formatDateTime(-12)
  }
];

export function buildNotificationStats(records: NotificationRecord[]): NotificationStats {
  return {
    total: records.length,
    unread: records.filter(record => record.status === "Unread").length,
    read: records.filter(record => record.status === "Read").length,
    archived: records.filter(record => record.status === "Archived").length
  };
}

export function buildNotificationListResponse(
  records: NotificationRecord[]
): NotificationListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildNotificationStats(records)
  };
}

export function createNotificationRecord(
  payload: CreateNotificationInput,
  index: number
): NotificationRecord {
  const now = new Date().toISOString().slice(0, 16);

  return {
    id: `NT-${10100 + index}`,
    title: payload.title,
    message: payload.message,
    type: payload.type,
    status: "Unread",
    owner: payload.owner,
    sourceModule: payload.sourceModule,
    createdAt: now,
    updatedAt: now
  };
}
