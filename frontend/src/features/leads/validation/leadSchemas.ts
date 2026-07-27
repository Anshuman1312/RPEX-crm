import { z } from "zod";
import { leadPriorityOptions, leadSourceOptions, leadStageOptions } from "@/features/leads/constants/leadOptions";

export const createLeadSchema = z.object({
  name: z.string().min(2, "Name must have at least 2 characters"),
  email: z.string().email("Enter a valid email address"),
  phone: z.string().min(8, "Enter a valid phone number"),
  source: z.enum(leadSourceOptions.filter(option => option !== "All") as [
    "Facebook",
    "Instagram",
    "Google Ads",
    "Website",
    "WhatsApp",
    "Walk-in",
    "Referral",
    "Channel Partner",
    "Client Reference",
    "Exhibition/Event",
    "JustDial",
    "Other"
  ]),
  priority: z.enum(leadPriorityOptions.filter(option => option !== "All") as ["Hot", "Warm", "Cold"]),
  owner: z.string().min(2, "Owner is required"),
  budget: z.coerce.number().min(1, "Budget must be greater than 0"),
  nextFollowUp: z.string().min(1, "Next follow-up date is required"),
  stage: z.enum(leadStageOptions.filter(option => option !== "All") as [
    "New",
    "Qualified",
    "Negotiation",
    "Won",
    "Future Perspective"
  ])
});

export type CreateLeadFormValues = z.infer<typeof createLeadSchema>;
