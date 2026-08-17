import { z } from "zod";

export const createEmployeeSchema = z.object({
  fullName: z.string().min(2, "Full name is required"),
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  phone: z.string().min(10, "Phone number must be at least 10 digits"),
  roleId: z.string().min(1, "Role is required")
});

export type CreateEmployeeFormValues = z.infer<typeof createEmployeeSchema>;
