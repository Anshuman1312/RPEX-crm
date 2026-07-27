import { z } from "zod";
import { employeeBandOptions, employeeDepartmentOptions } from "@/features/employees/constants/employeeOptions";

export const createEmployeeSchema = z.object({
  fullName: z.string().min(2, "Employee name is required"),
  email: z.string().email("Enter a valid email address"),
  department: z.enum(employeeDepartmentOptions.filter(option => option !== "All") as ["Sales", "Operations", "Finance", "Marketing", "HR"]),
  band: z.enum(employeeBandOptions),
  manager: z.string().min(2, "Manager name is required"),
  joiningDate: z.string().min(10, "Joining date is required")
});

export type CreateEmployeeFormValues = z.infer<typeof createEmployeeSchema>;
