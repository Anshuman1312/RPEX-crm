import { SearchInput } from "@/components";
import {
  calendarEventStatusOptions,
  calendarEventTypeOptions
} from "@/features/calendar/constants/calendarOptions";
import {
  CalendarEventStatus,
  CalendarEventType
} from "@/features/calendar/types/calendar";

interface CalendarFiltersBarProps {
  search: string;
  type: CalendarEventType | "All";
  status: CalendarEventStatus | "All";
  onSearchChange: (value: string) => void;
  onTypeChange: (value: CalendarEventType | "All") => void;
  onStatusChange: (value: CalendarEventStatus | "All") => void;
}

export function CalendarFiltersBar({
  search,
  type,
  status,
  onSearchChange,
  onTypeChange,
  onStatusChange
}: CalendarFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by event id, title, owner, attendee, module"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onTypeChange(event.target.value as CalendarEventType | "All")}
        value={type}
      >
        {calendarEventTypeOptions.map(option => (
          <option key={option} value={option}>
            Type: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as CalendarEventStatus | "All")}
        value={status}
      >
        {calendarEventStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
