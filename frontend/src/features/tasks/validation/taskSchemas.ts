import { z } from "zod";
import { taskPriorityOptions } from "@/features/tasks/constants/taskOptions";

export const createTaskSchema = z.object({
  title: z.string().min(2, "Task title is required"),
  module: z.string().min(2, "Module name is required"),
  assignee: z.string().min(2, "Assignee is required"),
  dueDate: z.string().min(10, "Due date is required"),
  priority: z.enum(taskPriorityOptions.filter(option => option !== "All") as ["Low", "Medium", "High", "Critical"]),
  effortPoints: z.coerce.number().int().positive("Effort points must be greater than zero")
});

export type CreateTaskFormValues = z.infer<typeof createTaskSchema>;
