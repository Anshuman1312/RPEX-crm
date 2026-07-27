export type ProjectPhase = "Planning" | "Execution" | "Handover" | "Completed";
export type ProjectHealth = "On Track" | "Watchlist" | "Delayed";

export interface ProjectRecord {
  id: string;
  name: string;
  client: string;
  projectManager: string;
  phase: ProjectPhase;
  health: ProjectHealth;
  progress: number;
  budget: number;
  targetHandover: string;
  lastUpdated: string;
}

export interface ProjectFilters {
  search?: string;
  phase?: ProjectPhase | "All";
  health?: ProjectHealth | "All";
}

export interface ProjectStats {
  total: number;
  onTrack: number;
  delayed: number;
  nearHandover: number;
}

export interface ProjectListResponse {
  items: ProjectRecord[];
  total: number;
  stats: ProjectStats;
}

export interface CreateProjectInput {
  name: string;
  client: string;
  projectManager: string;
  phase: ProjectPhase;
  budget: number;
  targetHandover: string;
}
