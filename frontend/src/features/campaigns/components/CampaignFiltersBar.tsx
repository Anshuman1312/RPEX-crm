import { SearchInput } from "@/components";
import {
  campaignTypeOptions,
  campaignStatusOptions
} from "@/features/campaigns/constants/campaignOptions";
import { CampaignStatus } from "@/features/campaigns/types/campaign";

interface CampaignFiltersBarProps {
  search: string;
  type: string | "All";
  status: CampaignStatus | "All";
  onSearchChange: (value: string) => void;
  onTypeChange: (value: string) => void;
  onStatusChange: (value: CampaignStatus | "All") => void;
}

export function CampaignFiltersBar({
  search,
  type,
  status,
  onSearchChange,
  onTypeChange,
  onStatusChange
}: CampaignFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by campaign id, name, type or platform"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onTypeChange(event.target.value)}
        value={type}
      >
        {campaignTypeOptions.map(option => (
          <option key={option} value={option}>
            Type: {option}
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
