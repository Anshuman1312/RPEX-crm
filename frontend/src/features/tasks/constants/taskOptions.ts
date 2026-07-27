import { TaskPriority, TaskStatus } from "@/features/tasks/types/task";

export const taskPriorityOptions: Array<TaskPriority | "All"> = [
  "All",
  "Low",
  "Medium",
  "High",
  "Critical"
];

export const taskStatusOptions: Array<TaskStatus | "All"> = [
  "All",
  "Backlog",
  "In Progress",
  "Blocked",
  "Completed"
];
