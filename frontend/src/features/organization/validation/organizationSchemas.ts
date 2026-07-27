import { z } from "zod";
import { organizationIndustryOptions } from "@/features/organization/constants/organizationOptions";

export const createOrganizationSchema = z.object({
  name: z.string().min(2, "Organization name is required"),
  industry: z.enum(
    organizationIndustryOptions.filter(o => o !== "All") as [
      "Real Estate",
      "Construction",
      "Finance",
      "Technology",
      "Retail"
    ]
  ),
  primaryContact: z.string().min(2, "Primary contact is required"),
  email: z.string().email("Enter a valid email address"),
  phone: z.string().min(8, "Enter a valid phone number"),
  city: z.string().min(2, "City is required"),
  employeeCount: z.coerce.number().int().positive("Employee count must be greater than zero")
});

export type CreateOrganizationFormValues = z.infer<typeof createOrganizationSchema>;
