import { SearchInput } from "@/components";
import {
  meetingStatusOptions,
  meetingTypeOptions
} from "@/features/meetings/constants/meetingOptions";
import {
  MeetingStatus,
  MeetingType
} from "@/features/meetings/types/meeting";

interface MeetingFiltersBarProps {
  search: string;
  type: MeetingType | "All";
  status: MeetingStatus | "All";
  onSearchChange: (value: string) => void;
  onTypeChange: (value: MeetingType | "All") => void;
  onStatusChange: (value: MeetingStatus | "All") => void;
}

export function MeetingFiltersBar({
  search,
  type,
  status,
  onSearchChange,
  onTypeChange,
  onStatusChange
}: MeetingFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by meeting id, title, host, attendee, location"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onTypeChange(event.target.value as MeetingType | "All")}
        value={type}
      >
        {meetingTypeOptions.map(option => (
          <option key={option} value={option}>
            Type: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as MeetingStatus | "All")}
        value={status}
      >
        {meetingStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
