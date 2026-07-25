import { useMemo, useState } from "react";
import {
  FollowUpChannel,
  FollowUpFilters,
  FollowUpPriority,
  FollowUpStatus
} from "@/features/followups/types/followup";

export function useFollowUpFilters() {
  const [search, setSearch] = useState("");
  const [channel, setChannel] = useState<FollowUpChannel | "All">("All");
  const [priority, setPriority] = useState<FollowUpPriority | "All">("All");
  const [status, setStatus] = useState<FollowUpStatus | "All">("All");

  const filters = useMemo<FollowUpFilters>(
    () => ({
      search,
      channel,
      priority,
      status
    }),
    [channel, priority, search, status]
  );

  return {
    filters,
    search,
    channel,
    priority,
    status,
    setSearch,
    setChannel,
    setPriority,
    setStatus
  };
}
