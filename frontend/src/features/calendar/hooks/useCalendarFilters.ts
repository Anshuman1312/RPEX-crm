import { useMemo, useState } from "react";
import {
  CalendarEventStatus,
  CalendarEventType,
  CalendarFilters
} from "@/features/calendar/types/calendar";

export function useCalendarFilters() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState<CalendarEventType | "All">("All");
  const [status, setStatus] = useState<CalendarEventStatus | "All">("All");

  const filters = useMemo<CalendarFilters>(
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
