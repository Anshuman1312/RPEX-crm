import {
  CreateWorkflowInput,
  WorkflowListResponse,
  WorkflowRecord,
  WorkflowStats
} from "@/features/workflow/types/workflow";

function formatDate(offsetDays: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

export const initialWorkflowRecords: WorkflowRecord[] = [
  {
    id: "WF-001",
    name: "New Lead Alert",
    trigger: "Lead Created",
    action: "Send Notification",
    status: "Active",
    module: "Leads",
    runsTotal: 142,
    lastRunAt: formatDate(-1),
    createdAt: formatDate(-180)
  },
  {
    id: "WF-002",
    name: "Booking Confirmation Task",
    trigger: "Booking Confirmed",
    action: "Create Task",
    status: "Active",
    module: "Bookings",
    runsTotal: 67,
    lastRunAt: formatDate(-2),
    createdAt: formatDate(-150)
  },
  {
    id: "WF-003",
    name: "At-Risk Customer Escalation",
    trigger: "Customer At Risk",
    action: "Assign Agent",
    status: "Paused",
    module: "Customers",
    runsTotal: 23,
    lastRunAt: formatDate(-14),
    createdAt: formatDate(-90)
  },
  {
    id: "WF-004",
    name: "Overdue Task Reminder",
    trigger: "Task Overdue",
    action: "Send Notification",
    status: "Active",
    module: "Tasks",
    runsTotal: 88,
    lastRunAt: formatDate(-1),
    createdAt: formatDate(-120)
  },
  {
    id: "WF-005",
    name: "Payment Receipt Report",
    trigger: "Payment Received",
    action: "Generate Report",
    status: "Draft",
    module: "Payments",
    runsTotal: 0,
    lastRunAt: "—",
    createdAt: formatDate(-5)
  }
];

export function buildWorkflowStats(records: WorkflowRecord[]): WorkflowStats {
  return {
    total: records.length,
    active: records.filter(r => r.status === "Active").length,
    paused: records.filter(r => r.status === "Paused").length,
    draft: records.filter(r => r.status === "Draft").length
  };
}

export function buildWorkflowListResponse(records: WorkflowRecord[]): WorkflowListResponse {
  return { items: records, total: records.length, stats: buildWorkflowStats(records) };
}

export function createWorkflowRecord(payload: CreateWorkflowInput, index: number): WorkflowRecord {
  const today = new Date().toISOString().slice(0, 10);
  return {
    id: `WF-${String(index).padStart(3, "0")}`,
    name: payload.name,
    trigger: payload.trigger,
    action: payload.action,
    status: "Draft",
    module: payload.module,
    runsTotal: 0,
    lastRunAt: "—",
    createdAt: today
  };
}
