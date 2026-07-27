import { useMemo, useState } from "react";
import {
  TaskFilters,
  TaskPriority,
  TaskStatus
} from "@/features/tasks/types/task";

export function useTaskFilters() {
  const [search, setSearch] = useState("");
  const [priority, setPriority] = useState<TaskPriority | "All">("All");
  const [status, setStatus] = useState<TaskStatus | "All">("All");

  const filters = useMemo<TaskFilters>(
    () => ({
      search,
      priority,
      status
    }),
    [priority, search, status]
  );

  return {
    filters,
    search,
    priority,
    status,
    setSearch,
    setPriority,
    setStatus
  };
}
