import { z } from "zod";
import {
  followUpChannelOptions,
  followUpPriorityOptions
} from "@/features/followups/constants/followupOptions";

export const createFollowUpSchema = z.object({
  leadName: z.string().min(2, "Lead name is required"),
  owner: z.string().min(2, "Owner is required"),
  scheduledAt: z.string().min(16, "Scheduled date and time is required"),
  channel: z.enum(followUpChannelOptions.filter(option => option !== "All") as ["Call", "WhatsApp", "Email", "Meeting"]),
  priority: z.enum(followUpPriorityOptions.filter(option => option !== "All") as ["Low", "Medium", "High"]),
  notes: z.string().min(2, "Notes are required")
});

export type CreateFollowUpFormValues = z.infer<typeof createFollowUpSchema>;
