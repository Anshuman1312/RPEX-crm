import { useMemo, useState } from "react";
import {
  MeetingFilters,
  MeetingStatus,
  MeetingType
} from "@/features/meetings/types/meeting";

export function useMeetingFilters() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState<MeetingType | "All">("All");
  const [status, setStatus] = useState<MeetingStatus | "All">("All");

  const filters = useMemo<MeetingFilters>(
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
