import { useMemo, useState } from "react";
import {
  InventoryCategory,
  InventoryFilters,
  InventoryStatus
} from "@/features/inventory/types/inventory";

export function useInventoryFilters() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<InventoryCategory | "All">("All");
  const [status, setStatus] = useState<InventoryStatus | "All">("All");

  const filters = useMemo<InventoryFilters>(
    () => ({
      search,
      category,
      status
    }),
    [category, search, status]
  );

  return {
    filters,
    search,
    category,
    status,
    setSearch,
    setCategory,
    setStatus
  };
}
