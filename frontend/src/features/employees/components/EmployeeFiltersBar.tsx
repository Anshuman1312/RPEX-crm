import { SearchInput } from "@/components";
import {
  employeeStatusOptions
} from "@/features/employees/constants/employeeOptions";
import {
  EmployeeStatus
} from "@/features/employees/types/employee";

interface EmployeeFiltersBarProps {
  search: string;
  status: EmployeeStatus | "All";
  onSearchChange: (value: string) => void;
  onStatusChange: (value: EmployeeStatus | "All") => void;
}

export function EmployeeFiltersBar({
  search,
  status,
  onSearchChange,
  onStatusChange
}: EmployeeFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by name, email, or employee code"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as EmployeeStatus | "All")}
        value={status}
      >
        {employeeStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
