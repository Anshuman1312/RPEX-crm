import { SearchInput } from "@/components";
import {
  followUpChannelOptions,
  followUpPriorityOptions,
  followUpStatusOptions
} from "@/features/followups/constants/followupOptions";
import {
  FollowUpChannel,
  FollowUpPriority,
  FollowUpStatus
} from "@/features/followups/types/followup";

interface FollowUpFiltersBarProps {
  search: string;
  channel: FollowUpChannel | "All";
  priority: FollowUpPriority | "All";
  status: FollowUpStatus | "All";
  onSearchChange: (value: string) => void;
  onChannelChange: (value: FollowUpChannel | "All") => void;
  onPriorityChange: (value: FollowUpPriority | "All") => void;
  onStatusChange: (value: FollowUpStatus | "All") => void;
}

export function FollowUpFiltersBar({
  search,
  channel,
  priority,
  status,
  onSearchChange,
  onChannelChange,
  onPriorityChange,
  onStatusChange
}: FollowUpFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by follow-up id, lead name or owner"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onChannelChange(event.target.value as FollowUpChannel | "All")}
        value={channel}
      >
        {followUpChannelOptions.map(option => (
          <option key={option} value={option}>
            Mode: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onPriorityChange(event.target.value as FollowUpPriority | "All")}
        value={priority}
      >
        {followUpPriorityOptions.map(option => (
          <option key={option} value={option}>
            Priority: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as FollowUpStatus | "All")}
        value={status}
      >
        {followUpStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
