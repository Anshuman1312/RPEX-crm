import { z } from "zod";

export const createCustomerSchema = z.object({
  first_name: z.string().min(1, "First Name is required"),
  last_name: z.string().min(1, "Last Name is required"),
  email: z.string().email("Enter a valid email address"),
  phone: z.string().min(8, "Enter a valid phone number"),
  alternate_phone: z.string().optional().or(z.literal("")),
  company_name: z.string().optional().or(z.literal("")),
  customer_type: z.enum(["individual", "corporate", "partnership", "trust", "nri"], {
    message: "Customer Type is required"
  }),
  referred_by_user_id: z.string().optional().or(z.literal("")),
  lead_converted_from_id: z.string().optional().or(z.literal("")),
  preferred_contact_method: z
    .enum(["phone", "email", "whatsapp"], {
      message: "Preferred contact method is required"
    })
    .optional()
    .or(z.literal("")),
  preferred_language: z.string().default("en"),
  gstin: z.string().optional().or(z.literal("")),
  pan: z.string().optional().or(z.literal("")),
  notes: z.string().optional().or(z.literal(""))
});

export type CreateCustomerFormValues = z.infer<typeof createCustomerSchema>;
