import { useMemo, useState } from "react";
import {
  ActivityAction,
  ActivityFilters,
  ActivityModule
} from "@/features/activity-timeline/types/activity";

export function useActivityFilters() {
  const [search, setSearch] = useState("");
  const [module, setModule] = useState<ActivityModule | "All">("All");
  const [action, setAction] = useState<ActivityAction | "All">("All");

  const filters = useMemo<ActivityFilters>(
    () => ({ search, module, action }),
    [action, module, search]
  );

  return { filters, search, module, action, setSearch, setModule, setAction };
}
