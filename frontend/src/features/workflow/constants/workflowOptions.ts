import { WorkflowAction, WorkflowStatus, WorkflowTrigger } from "@/features/workflow/types/workflow";

export const workflowTriggerOptions: Array<WorkflowTrigger | "All"> = [
  "All",
  "Lead Created",
  "Booking Confirmed",
  "Payment Received",
  "Task Overdue",
  "Customer At Risk",
  "Manual"
];

export const workflowStatusOptions: Array<WorkflowStatus | "All"> = [
  "All",
  "Active",
  "Paused",
  "Draft"
];

export const workflowActionOptions: WorkflowAction[] = [
  "Send Notification",
  "Create Task",
  "Assign Agent",
  "Update Status",
  "Generate Report"
];
