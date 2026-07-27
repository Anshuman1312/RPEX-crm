import { useMemo, useState } from "react";
import {
  CustomerFilters,
  CustomerPropertyType,
  CustomerPurpose
} from "@/features/customers/types/customer";

export function useCustomerFilters() {
  const [search, setSearch] = useState("");
  const [purpose, setPurpose] = useState<CustomerPurpose | "All">("All");
  const [propertyType, setPropertyType] = useState<CustomerPropertyType | "All">("All");

  const filters = useMemo<CustomerFilters>(
    () => ({
      search,
      purpose,
      propertyType
    }),
    [search, purpose, propertyType]
  );

  return {
    filters,
    search,
    purpose,
    propertyType,
    setSearch,
    setPurpose,
    setPropertyType
  };
}
