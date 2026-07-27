export type TaskPriority = "Low" | "Medium" | "High" | "Critical";
export type TaskStatus = "Backlog" | "In Progress" | "Blocked" | "Completed";

export interface TaskRecord {
  id: string;
  title: string;
  module: string;
  assignee: string;
  dueDate: string;
  priority: TaskPriority;
  status: TaskStatus;
  effortPoints: number;
  updatedAt: string;
}

export interface TaskFilters {
  search?: string;
  priority?: TaskPriority | "All";
  status?: TaskStatus | "All";
}

export interface TaskStats {
  total: number;
  inProgress: number;
  blocked: number;
  completed: number;
}

export interface TaskListResponse {
  items: TaskRecord[];
  total: number;
  stats: TaskStats;
}

export interface CreateTaskInput {
  title: string;
  module: string;
  assignee: string;
  dueDate: string;
  priority: TaskPriority;
  effortPoints: number;
}
