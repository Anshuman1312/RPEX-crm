import { useMemo, useState } from "react";
import { RoleFilters, RoleScope, RoleStatus } from "@/features/roles/types/role";

export function useRoleFilters() {
  const [search, setSearch] = useState("");
  const [scope, setScope] = useState<RoleScope | "All">("All");
  const [status, setStatus] = useState<RoleStatus | "All">("All");

  const filters = useMemo<RoleFilters>(
    () => ({ search, scope, status }),
    [scope, search, status]
  );

  return { filters, search, scope, status, setSearch, setScope, setStatus };
}
