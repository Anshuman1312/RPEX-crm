import { SearchInput } from "@/components";
import {
  inventoryCategoryOptions,
  inventoryStatusOptions
} from "@/features/inventory/constants/inventoryOptions";
import {
  InventoryCategory,
  InventoryStatus
} from "@/features/inventory/types/inventory";

interface InventoryFiltersBarProps {
  search: string;
  category: InventoryCategory | "All";
  status: InventoryStatus | "All";
  onSearchChange: (value: string) => void;
  onCategoryChange: (value: InventoryCategory | "All") => void;
  onStatusChange: (value: InventoryStatus | "All") => void;
}

export function InventoryFiltersBar({
  search,
  category,
  status,
  onSearchChange,
  onCategoryChange,
  onStatusChange
}: InventoryFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by unit id, code, project, agent"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onCategoryChange(event.target.value as InventoryCategory | "All")}
        value={category}
      >
        {inventoryCategoryOptions.map(option => (
          <option key={option} value={option}>
            Category: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onStatusChange(event.target.value as InventoryStatus | "All")}
        value={status}
      >
        {inventoryStatusOptions.map(option => (
          <option key={option} value={option}>
            Status: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
