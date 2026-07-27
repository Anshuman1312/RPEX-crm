import { z } from "zod";
import { workflowActionOptions, workflowTriggerOptions } from "@/features/workflow/constants/workflowOptions";

export const createWorkflowSchema = z.object({
  name: z.string().min(2, "Workflow name is required"),
  trigger: z.enum(
    workflowTriggerOptions.filter(o => o !== "All") as [
      "Lead Created",
      "Booking Confirmed",
      "Payment Received",
      "Task Overdue",
      "Customer At Risk",
      "Manual"
    ]
  ),
  action: z.enum(workflowActionOptions),
  module: z.string().min(2, "Module is required")
});

export type CreateWorkflowFormValues = z.infer<typeof createWorkflowSchema>;
