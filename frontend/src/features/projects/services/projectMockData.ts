import {
  CreateProjectInput,
  ProjectListResponse,
  ProjectRecord,
  ProjectStats
} from "@/features/projects/types/project";

const today = new Date();

function formatDate(offset: number) {
  const date = new Date(today);
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

export const initialProjectRecords: ProjectRecord[] = [
  {
    id: "PR-3101",
    name: "Skyline Heights Phase 2",
    client: "Apex Realty Group",
    projectManager: "Riya",
    phase: "Execution",
    health: "On Track",
    progress: 62,
    budget: 145000000,
    targetHandover: formatDate(120),
    lastUpdated: formatDate(-1)
  },
  {
    id: "PR-3102",
    name: "Emerald Business Park",
    client: "UrbanCore Developers",
    projectManager: "Aman",
    phase: "Planning",
    health: "Watchlist",
    progress: 28,
    budget: 98000000,
    targetHandover: formatDate(220),
    lastUpdated: formatDate(-3)
  },
  {
    id: "PR-3103",
    name: "Riverfront Residency",
    client: "BlueStone Estates",
    projectManager: "Rohan",
    phase: "Handover",
    health: "Delayed",
    progress: 91,
    budget: 186000000,
    targetHandover: formatDate(18),
    lastUpdated: formatDate(-2)
  },
  {
    id: "PR-3104",
    name: "Orchid Greens",
    client: "Zenith Infra",
    projectManager: "Priya",
    phase: "Completed",
    health: "On Track",
    progress: 100,
    budget: 76000000,
    targetHandover: formatDate(-30),
    lastUpdated: formatDate(-6)
  }
];

function isWithinThirtyDays(dateValue: string) {
  const target = new Date(dateValue).getTime();
  const now = new Date().getTime();
  const days = (target - now) / (1000 * 60 * 60 * 24);
  return days >= 0 && days <= 30;
}

export function buildProjectStats(records: ProjectRecord[]): ProjectStats {
  return {
    total: records.length,
    onTrack: records.filter(record => record.health === "On Track").length,
    delayed: records.filter(record => record.health === "Delayed").length,
    nearHandover: records.filter(record => isWithinThirtyDays(record.targetHandover)).length
  };
}

export function buildProjectListResponse(records: ProjectRecord[]): ProjectListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildProjectStats(records)
  };
}

export function createProjectRecord(payload: CreateProjectInput, index: number): ProjectRecord {
  return {
    id: `PR-${3100 + index}`,
    name: payload.name,
    client: payload.client,
    projectManager: payload.projectManager,
    phase: payload.phase,
    health: "On Track",
    progress: 0,
    budget: payload.budget,
    targetHandover: payload.targetHandover,
    lastUpdated: new Date().toISOString().slice(0, 10)
  };
}
