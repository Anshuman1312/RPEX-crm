import { useMemo, useState } from "react";
import { CampaignChannel, CampaignFilters, CampaignStatus } from "@/features/campaigns/types/campaign";

export function useCampaignFilters() {
  const [search, setSearch] = useState("");
  const [channel, setChannel] = useState<CampaignChannel | "All">("All");
  const [status, setStatus] = useState<CampaignStatus | "All">("All");

  const filters = useMemo<CampaignFilters>(
    () => ({
      search,
      channel,
      status
    }),
    [channel, search, status]
  );

  return {
    filters,
    search,
    channel,
    status,
    setSearch,
    setChannel,
    setStatus
  };
}
