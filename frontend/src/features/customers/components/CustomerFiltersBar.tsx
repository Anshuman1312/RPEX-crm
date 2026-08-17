import { SearchInput } from "@/components";
import {
  customerStatusOptions,
  customerTypeOptions
} from "@/features/customers/constants/customerOptions";

interface CustomerFiltersBarProps {
  search: string;
  status: string;
  customerType: string;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onCustomerTypeChange: (value: string) => void;
}

export function CustomerFiltersBar({
  search,
  status,
  customerType,
  onSearchChange,
  onStatusChange,
  onCustomerTypeChange
}: CustomerFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by ID, name, email, or phone..."
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm capitalize"
        onChange={event => onStatusChange(event.target.value)}
        value={status}
      >
        {customerStatusOptions.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm capitalize"
        onChange={event => onCustomerTypeChange(event.target.value)}
        value={customerType}
      >
        {customerTypeOptions.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </section>
  );
}
