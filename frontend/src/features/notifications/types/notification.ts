export type NotificationType = "Reminder" | "Alert" | "Approval" | "System";
export type NotificationStatus = "Unread" | "Read" | "Archived";

export interface NotificationRecord {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  status: NotificationStatus;
  owner: string;
  sourceModule: string;
  createdAt: string;
  updatedAt: string;
}

export interface NotificationFilters {
  search?: string;
  type?: NotificationType | "All";
  status?: NotificationStatus | "All";
}

export interface NotificationStats {
  total: number;
  unread: number;
  read: number;
  archived: number;
}

export interface NotificationListResponse {
  items: NotificationRecord[];
  total: number;
  stats: NotificationStats;
}

export interface CreateNotificationInput {
  title: string;
  message: string;
  type: NotificationType;
  owner: string;
  sourceModule: string;
}
