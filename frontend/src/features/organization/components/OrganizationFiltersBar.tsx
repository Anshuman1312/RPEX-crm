import { SearchInput } from "@/components";
import {
  organizationIndustryOptions,
  organizationStatusOptions
} from "@/features/organization/constants/organizationOptions";
import {
  OrganizationIndustry,
  OrganizationStatus
} from "@/features/organization/types/organization";

interface Props {
  search: string;
  industry: OrganizationIndustry | "All";
  status: OrganizationStatus | "All";
  onSearchChange: (v: string) => void;
  onIndustryChange: (v: OrganizationIndustry | "All") => void;
  onStatusChange: (v: OrganizationStatus | "All") => void;
}

export function OrganizationFiltersBar({
  search, industry, status, onSearchChange, onIndustryChange, onStatusChange
}: Props) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by id, name, contact, email, city"
        value={search}
      />
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onIndustryChange(e.target.value as OrganizationIndustry | "All")}
        value={industry}
      >
        {organizationIndustryOptions.map(o => (
          <option key={o} value={o}>Industry: {o}</option>
        ))}
      </select>
      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={e => onStatusChange(e.target.value as OrganizationStatus | "All")}
        value={status}
      >
        {organizationStatusOptions.map(o => (
          <option key={o} value={o}>Status: {o}</option>
        ))}
      </select>
    </section>
  );
}
