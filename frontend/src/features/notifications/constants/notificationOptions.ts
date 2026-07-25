import {
  NotificationStatus,
  NotificationType
} from "@/features/notifications/types/notification";

export const notificationTypeOptions: Array<NotificationType | "All"> = [
  "All",
  "Reminder",
  "Alert",
  "Approval",
  "System"
];

export const notificationStatusOptions: Array<NotificationStatus | "All"> = [
  "All",
  "Unread",
  "Read",
  "Archived"
];
