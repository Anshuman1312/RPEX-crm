import { useMemo, useState } from "react";
import {
  ProjectFilters,
  ProjectHealth,
  ProjectPhase
} from "@/features/projects/types/project";

export function useProjectFilters() {
  const [search, setSearch] = useState("");
  const [phase, setPhase] = useState<ProjectPhase | "All">("All");
  const [health, setHealth] = useState<ProjectHealth | "All">("All");

  const filters = useMemo<ProjectFilters>(
    () => ({
      search,
      phase,
      health
    }),
    [health, phase, search]
  );

  return {
    filters,
    search,
    phase,
    health,
    setSearch,
    setPhase,
    setHealth
  };
}
