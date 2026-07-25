import { useMemo, useState } from "react";
import { WorkflowFilters, WorkflowStatus, WorkflowTrigger } from "@/features/workflow/types/workflow";

export function useWorkflowFilters() {
  const [search, setSearch] = useState("");
  const [trigger, setTrigger] = useState<WorkflowTrigger | "All">("All");
  const [status, setStatus] = useState<WorkflowStatus | "All">("All");

  const filters = useMemo<WorkflowFilters>(
    () => ({ search, trigger, status }),
    [search, status, trigger]
  );

  return { filters, search, trigger, status, setSearch, setTrigger, setStatus };
}
