import { useMemo, useState } from "react";
import {
  NotificationFilters,
  NotificationStatus,
  NotificationType
} from "@/features/notifications/types/notification";

export function useNotificationFilters() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState<NotificationType | "All">("All");
  const [status, setStatus] = useState<NotificationStatus | "All">("All");

  const filters = useMemo<NotificationFilters>(
    () => ({
      search,
      type,
      status
    }),
    [search, status, type]
  );

  return {
    filters,
    search,
    type,
    status,
    setSearch,
    setType,
    setStatus
  };
}
