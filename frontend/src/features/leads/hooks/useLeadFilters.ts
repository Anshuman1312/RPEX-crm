import { useMemo, useState } from "react";
import { LeadFilters, LeadSource, LeadStatus } from "@/features/leads/types/lead";

export function useLeadFilters() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<LeadStatus | "All">("All");
  const [source, setSource] = useState<LeadSource | "All">("All");

  const filters = useMemo<LeadFilters>(
    () => ({
      search,
      status,
      source
    }),
    [search, source, status]
  );

  return {
    filters,
    search,
    status,
    source,
    setSearch,
    setStatus,
    setSource
  };
}

