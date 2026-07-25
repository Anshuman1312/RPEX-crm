import { z } from "zod";
import { roleScopeOptions } from "@/features/roles/constants/roleOptions";

export const createRoleSchema = z.object({
  name: z.string().min(2, "Role name is required"),
  scope: z.enum(
    roleScopeOptions.filter(o => o !== "All") as ["System", "Organization", "Module"]
  ),
  description: z.string().min(4, "Description is required")
});

export type CreateRoleFormValues = z.infer<typeof createRoleSchema>;
