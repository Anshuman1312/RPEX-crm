import { useMemo, useState } from "react";
import { FollowUpFilters } from "@/features/followups/types/followup";

export function useFollowUpFilters() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState<string>("All");
  const [priority, setPriority] = useState<string>("All");
  const [status, setStatus] = useState<string>("All");

  const filters = useMemo<FollowUpFilters>(
    () => ({
      search,
      type: type === "All" ? undefined : (type as any),
      priority: priority === "All" ? undefined : (priority as any),
      status: status === "All" ? undefined : (status as any)
    }),
    [type, search, priority, status]
  );

  return {
    filters,
    search,
    type,
    priority,
    status,
    setSearch,
    setType,
    setPriority,
    setStatus
  };
}
