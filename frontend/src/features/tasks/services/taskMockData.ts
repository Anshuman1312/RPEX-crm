import {
  CreateTaskInput,
  TaskListResponse,
  TaskRecord,
  TaskStats
} from "@/features/tasks/types/task";

function formatDate(offset: number) {
  const date = new Date();
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

export const initialTaskRecords: TaskRecord[] = [
  {
    id: "TK-7101",
    title: "Finalize payment retry workflow",
    module: "Payments",
    assignee: "Riya",
    dueDate: formatDate(3),
    priority: "High",
    status: "In Progress",
    effortPoints: 8,
    updatedAt: formatDate(-1)
  },
  {
    id: "TK-7102",
    title: "Prepare booking handover checklist",
    module: "Bookings",
    assignee: "Aman",
    dueDate: formatDate(5),
    priority: "Medium",
    status: "Backlog",
    effortPoints: 5,
    updatedAt: formatDate(-2)
  },
  {
    id: "TK-7103",
    title: "Investigate delayed inventory updates",
    module: "Inventory",
    assignee: "Rohan",
    dueDate: formatDate(2),
    priority: "Critical",
    status: "Blocked",
    effortPoints: 13,
    updatedAt: formatDate(-1)
  },
  {
    id: "TK-7104",
    title: "Close lead source analytics bug",
    module: "Leads",
    assignee: "Priya",
    dueDate: formatDate(-1),
    priority: "Low",
    status: "Completed",
    effortPoints: 3,
    updatedAt: formatDate(-3)
  }
];

export function buildTaskStats(records: TaskRecord[]): TaskStats {
  return {
    total: records.length,
    inProgress: records.filter(record => record.status === "In Progress").length,
    blocked: records.filter(record => record.status === "Blocked").length,
    completed: records.filter(record => record.status === "Completed").length
  };
}

export function buildTaskListResponse(records: TaskRecord[]): TaskListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildTaskStats(records)
  };
}

export function createTaskRecord(payload: CreateTaskInput, index: number): TaskRecord {
  return {
    id: `TK-${7100 + index}`,
    title: payload.title,
    module: payload.module,
    assignee: payload.assignee,
    dueDate: payload.dueDate,
    priority: payload.priority,
    status: "Backlog",
    effortPoints: payload.effortPoints,
    updatedAt: new Date().toISOString().slice(0, 10)
  };
}
