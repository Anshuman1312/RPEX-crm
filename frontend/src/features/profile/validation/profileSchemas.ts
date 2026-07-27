import { z } from "zod";

export const profileSchema = z.object({
  displayName: z.string().min(2, "Display name must be at least 2 characters"),
  phone: z.string().min(8, "Enter a valid phone number"),
  city: z.string().min(2, "City is required"),
  bio: z.string().max(300, "Bio must be under 300 characters")
});

export type ProfileFormValues = z.infer<typeof profileSchema>;
