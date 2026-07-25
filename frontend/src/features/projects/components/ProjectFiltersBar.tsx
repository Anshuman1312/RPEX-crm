import { SearchInput } from "@/components";
import {
  projectHealthOptions,
  projectPhaseOptions
} from "@/features/projects/constants/projectOptions";
import {
  ProjectHealth,
  ProjectPhase
} from "@/features/projects/types/project";

interface ProjectFiltersBarProps {
  search: string;
  phase: ProjectPhase | "All";
  health: ProjectHealth | "All";
  onSearchChange: (value: string) => void;
  onPhaseChange: (value: ProjectPhase | "All") => void;
  onHealthChange: (value: ProjectHealth | "All") => void;
}

export function ProjectFiltersBar({
  search,
  phase,
  health,
  onSearchChange,
  onPhaseChange,
  onHealthChange
}: ProjectFiltersBarProps) {
  return (
    <section className="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
      <SearchInput
        onChange={onSearchChange}
        placeholder="Search by project id, name, client, manager"
        value={search}
      />

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onPhaseChange(event.target.value as ProjectPhase | "All")}
        value={phase}
      >
        {projectPhaseOptions.map(option => (
          <option key={option} value={option}>
            Phase: {option}
          </option>
        ))}
      </select>

      <select
        className="h-10 rounded-md border bg-background px-3 text-sm"
        onChange={event => onHealthChange(event.target.value as ProjectHealth | "All")}
        value={health}
      >
        {projectHealthOptions.map(option => (
          <option key={option} value={option}>
            Health: {option}
          </option>
        ))}
      </select>
    </section>
  );
}
