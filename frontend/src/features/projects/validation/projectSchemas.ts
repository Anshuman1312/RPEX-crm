import { z } from "zod";
import { projectPhaseOptions } from "@/features/projects/constants/projectOptions";

export const createProjectSchema = z.object({
  name: z.string().min(2, "Project name must have at least 2 characters"),
  client: z.string().min(2, "Client name is required"),
  projectManager: z.string().min(2, "Project manager is required"),
  phase: z.enum(projectPhaseOptions.filter(option => option !== "All") as ["Planning", "Execution", "Handover", "Completed"]),
  budget: z.coerce.number().positive("Budget must be greater than zero"),
  targetHandover: z.string().min(10, "Target handover date is required")
});

export type CreateProjectFormValues = z.infer<typeof createProjectSchema>;
