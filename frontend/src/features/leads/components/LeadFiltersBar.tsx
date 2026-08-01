import { SearchInput } from "@/components";
import { leadSourceOptions, leadStatusOptions } from "@/features/leads/constants/leadOptions";
import { LeadSource, LeadStatus } from "@/features/leads/types/lead";

interface LeadFiltersBarProps {
  search: string;
  status: LeadStatus | "All";
  source: LeadSource | "All";
  onSearchChange: (value: string) => void;
  onStatusChange: (value: LeadStatus | "All") => void;
  onSourceChange: (value: LeadSource | "All") => void;
}

export function LeadFiltersBar({
  search,
  status,
  source,
  onSearchChange,
  onStatusChange,
  onSourceChange
}: LeadFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by lead id, name, email, phone, owner"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as LeadStatus | "All")}
        value={status}
      >
        {leadStatusOptions.map(option => (
          <option key={option} value={option}>
            {option === "All" ? "All Statuses" : option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onSourceChange(event.target.value as LeadSource | "All")}
        value={source}
      >
        {leadSourceOptions.map(option => (
          <option key={option} value={option}>
            {option === "All" ? "All Sources" : option}
          </option>
        ))}
      </select>
    </section>
  );
}

