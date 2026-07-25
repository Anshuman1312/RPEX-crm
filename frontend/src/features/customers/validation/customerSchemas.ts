import { z } from "zod";

export const createCustomerSchema = z.object({
  title: z.enum(["Mr.", "Miss", "Mrs"], { required_error: "Title is required" }),
  name: z.string().min(2, "Full Name is required"),
  phone: z.string().min(8, "Enter a valid mobile number"),
  alternatePhone: z.string().optional(),
  email: z.string().email("Enter a valid email address").or(z.literal("")),
  occupation: z.string().optional(),
  address: z.string().optional(),
  budgetRange: z.string().optional(),
  timeDuration: z.string().optional(),
  purpose: z.enum(["Investment", "Self Use", "Business"], { required_error: "Purpose is required" }),
  propertyType: z.enum(["Plot", "Villa", "Flat", "Commercial"], { required_error: "Property Type is required" }),
  remarks: z.string().optional()
});

export type CreateCustomerFormValues = z.infer<typeof createCustomerSchema>;
