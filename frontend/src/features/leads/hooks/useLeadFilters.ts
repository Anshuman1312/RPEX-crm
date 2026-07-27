import { useMemo, useState } from "react";
import { LeadFilters, LeadSource, LeadStage } from "@/features/leads/types/lead";

export function useLeadFilters() {
  const [search, setSearch] = useState("");
  const [stage, setStage] = useState<LeadStage | "All">("All");
  const [source, setSource] = useState<LeadSource | "All">("All");

  const filters = useMemo<LeadFilters>(
    () => ({
      search,
      stage,
      source
    }),
    [search, source, stage]
  );

  return {
    filters,
    search,
    stage,
    source,
    setSearch,
    setStage,
    setSource
  };
}
