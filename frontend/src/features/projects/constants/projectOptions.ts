import { ProjectHealth, ProjectPhase } from "@/features/projects/types/project";

export const projectPhaseOptions: Array<ProjectPhase | "All"> = [
  "All",
  "Planning",
  "Execution",
  "Handover",
  "Completed"
];

export const projectHealthOptions: Array<ProjectHealth | "All"> = [
  "All",
  "On Track",
  "Watchlist",
  "Delayed"
];
