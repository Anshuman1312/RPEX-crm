import { useMemo, useState } from "react";
import { CustomerFilters } from "@/features/customers/types/customer";

export function useCustomerFilters() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<string>("All");
  const [customerType, setCustomerType] = useState<string>("All");

  const filters = useMemo<CustomerFilters>(
    () => {
      const f: CustomerFilters = { search };
      if (status !== "All") {
        f.statuses = status;
      }
      if (customerType !== "All") {
        f.customer_types = customerType;
      }
      return f;
    },
    [search, status, customerType]
  );

  return {
    filters,
    search,
    status,
    customerType,
    setSearch,
    setStatus,
    setCustomerType
  };
}
