import { SearchInput } from "@/components";
import {
  campaignChannelOptions,
  campaignStatusOptions
} from "@/features/campaigns/constants/campaignOptions";
import {
  CampaignChannel,
  CampaignStatus
} from "@/features/campaigns/types/campaign";

interface CampaignFiltersBarProps {
  search: string;
  channel: CampaignChannel | "All";
  status: CampaignStatus | "All";
  onSearchChange: (value: string) => void;
  onChannelChange: (value: CampaignChannel | "All") => void;
  onStatusChange: (value: CampaignStatus | "All") => void;
}

export function CampaignFiltersBar({
  search,
  channel,
  status,
  onSearchChange,
  onChannelChange,
  onStatusChange
}: CampaignFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by campaign id, name, owner or channel"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onChannelChange(event.target.value as CampaignChannel | "All")}
        value={channel}
      >
        {campaignChannelOptions.map(option => (
          <option key={option} value={option}>
            Channel: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as CampaignStatus | "All")}
        value={status}
      >
        {campaignStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
