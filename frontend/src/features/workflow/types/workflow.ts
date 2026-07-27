export type WorkflowTrigger =
  | "Lead Created"
  | "Booking Confirmed"
  | "Payment Received"
  | "Task Overdue"
  | "Customer At Risk"
  | "Manual";

export type WorkflowStatus = "Active" | "Paused" | "Draft";

export type WorkflowAction =
  | "Send Notification"
  | "Create Task"
  | "Assign Agent"
  | "Update Status"
  | "Generate Report";

export interface WorkflowRecord {
  id: string;
  name: string;
  trigger: WorkflowTrigger;
  action: WorkflowAction;
  status: WorkflowStatus;
  module: string;
  runsTotal: number;
  lastRunAt: string;
  createdAt: string;
}

export interface WorkflowFilters {
  search?: string;
  trigger?: WorkflowTrigger | "All";
  status?: WorkflowStatus | "All";
}

export interface WorkflowStats {
  total: number;
  active: number;
  paused: number;
  draft: number;
}

export interface WorkflowListResponse {
  items: WorkflowRecord[];
  total: number;
  stats: WorkflowStats;
}

export interface CreateWorkflowInput {
  name: string;
  trigger: WorkflowTrigger;
  action: WorkflowAction;
  module: string;
}
