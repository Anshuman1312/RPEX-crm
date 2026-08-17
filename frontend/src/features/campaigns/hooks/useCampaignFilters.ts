import { useMemo, useState } from "react";
import { CampaignFilters, CampaignStatus } from "@/features/campaigns/types/campaign";

export function useCampaignFilters() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState<string>("All");
  const [status, setStatus] = useState<CampaignStatus | "All">("All");

  const filters = useMemo<CampaignFilters>(
    () => ({
      search,
      type,
      status
    }),
    [type, search, status]
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
