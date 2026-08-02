import { SearchInput } from "@/components";
import {
  followUpTypeOptions,
  followUpPriorityOptions,
  followUpStatusOptions
} from "@/features/followups/constants/followupOptions";

interface FollowUpFiltersBarProps {
  search: string;
  type: string;
  priority: string;
  status: string;
  onSearchChange: (value: string) => void;
  onTypeChange: (value: string) => void;
  onPriorityChange: (value: string) => void;
  onStatusChange: (value: string) => void;
}

export function FollowUpFiltersBar({
  search,
  type,
  priority,
  status,
  onSearchChange,
  onTypeChange,
  onPriorityChange,
  onStatusChange
}: FollowUpFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by subject, notes or reference..."
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm capitalize"
        onChange={event => onTypeChange(event.target.value)}
        value={type}
      >
        {followUpTypeOptions.map(option => (
          <option key={option} value={option}>
            Type: {option === "All" ? "All" : option.replace("_", " ")}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onPriorityChange(event.target.value)}
        value={priority}
      >
        {followUpPriorityOptions.map(option => (
          <option key={option} value={option}>
            Priority: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm capitalize"
        onChange={event => onStatusChange(event.target.value)}
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
