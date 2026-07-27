import { SearchInput } from "@/components";
import {
  notificationStatusOptions,
  notificationTypeOptions
} from "@/features/notifications/constants/notificationOptions";
import {
  NotificationStatus,
  NotificationType
} from "@/features/notifications/types/notification";

interface NotificationFiltersBarProps {
  search: string;
  type: NotificationType | "All";
  status: NotificationStatus | "All";
  onSearchChange: (value: string) => void;
  onTypeChange: (value: NotificationType | "All") => void;
  onStatusChange: (value: NotificationStatus | "All") => void;
}

export function NotificationFiltersBar({
  search,
  type,
  status,
  onSearchChange,
  onTypeChange,
  onStatusChange
}: NotificationFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by id, title, message, owner, module"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onTypeChange(event.target.value as NotificationType | "All")}
        value={type}
      >
        {notificationTypeOptions.map(option => (
          <option key={option} value={option}>
            Type: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as NotificationStatus | "All")}
        value={status}
      >
        {notificationStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
