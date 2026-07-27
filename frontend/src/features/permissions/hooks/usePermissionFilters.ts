import { useMemo, useState } from "react";
import {
  PermissionAction,
  PermissionFilters,
  PermissionModule,
  PermissionStatus
} from "@/features/permissions/types/permission";

export function usePermissionFilters() {
  const [search, setSearch] = useState("");
  const [module, setModule] = useState<PermissionModule | "All">("All");
  const [action, setAction] = useState<PermissionAction | "All">("All");
  const [status, setStatus] = useState<PermissionStatus | "All">("All");

  const filters = useMemo<PermissionFilters>(
    () => ({ search, module, action, status }),
    [action, module, search, status]
  );

  return { filters, search, module, action, status, setSearch, setModule, setAction, setStatus };
}
