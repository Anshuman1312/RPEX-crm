import { useMemo, useState } from "react";
import {
  OrganizationFilters,
  OrganizationIndustry,
  OrganizationStatus
} from "@/features/organization/types/organization";

export function useOrganizationFilters() {
  const [search, setSearch] = useState("");
  const [industry, setIndustry] = useState<OrganizationIndustry | "All">("All");
  const [status, setStatus] = useState<OrganizationStatus | "All">("All");

  const filters = useMemo<OrganizationFilters>(
    () => ({ search, industry, status }),
    [industry, search, status]
  );

  return { filters, search, industry, status, setSearch, setIndustry, setStatus };
}
