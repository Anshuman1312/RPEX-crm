import { SearchInput } from "@/components";
import {
  customerPropertyTypeOptions,
  customerPurposeOptions
} from "@/features/customers/constants/customerOptions";
import {
  CustomerPropertyType,
  CustomerPurpose
} from "@/features/customers/types/customer";

interface CustomerFiltersBarProps {
  search: string;
  purpose: CustomerPurpose | "All";
  propertyType: CustomerPropertyType | "All";
  onSearchChange: (value: string) => void;
  onPurposeChange: (value: CustomerPurpose | "All") => void;
  onPropertyTypeChange: (value: CustomerPropertyType | "All") => void;
}

export function CustomerFiltersBar({
  search,
  purpose,
  propertyType,
  onSearchChange,
  onPurposeChange,
  onPropertyTypeChange
}: CustomerFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by client id, name, email, primary/alternate phone"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onPurposeChange(event.target.value as CustomerPurpose | "All")}
        value={purpose}
      >
        {customerPurposeOptions.map(option => (
          <option key={option} value={option}>
            {option === "All" ? "All Purposes" : option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onPropertyTypeChange(event.target.value as CustomerPropertyType | "All")}
        value={propertyType}
      >
        {customerPropertyTypeOptions.map(option => (
          <option key={option} value={option}>
            {option === "All" ? "All Property Types" : option}
          </option>
        ))}
      </select>
    </section>
  );
}
