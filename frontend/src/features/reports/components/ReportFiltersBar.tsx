import { SearchInput } from "@/components";
import { reportStatusOptions, reportTypeOptions } from "@/features/reports/constants/reportOptions";
import { ReportStatus, ReportType } from "@/features/reports/types/report";

interface ReportFiltersBarProps {
  search: string;
  type: ReportType | "All";
  status: ReportStatus | "All";
  onSearchChange: (value: string) => void;
  onTypeChange: (value: ReportType | "All") => void;
  onStatusChange: (value: ReportStatus | "All") => void;
}

export function ReportFiltersBar({
  search,
  type,
  status,
  onSearchChange,
  onTypeChange,
  onStatusChange
}: ReportFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by report id, title, type, owner"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onTypeChange(event.target.value as ReportType | "All")}
        value={type}
      >
        {reportTypeOptions.map(option => (
          <option key={option} value={option}>
            Type: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as ReportStatus | "All")}
        value={status}
      >
        {reportStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
