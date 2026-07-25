import { z } from "zod";
import { campaignChannelOptions } from "@/features/campaigns/constants/campaignOptions";

export const createCampaignSchema = z.object({
  name: z.string().min(2, "Campaign name is required"),
  channel: z.enum(campaignChannelOptions.filter(option => option !== "All") as ["WhatsApp", "Email", "SMS", "Social", "Referral"]),
  owner: z.string().min(2, "Owner is required"),
  budget: z.coerce.number().positive("Budget must be greater than zero"),
  startDate: z.string().min(10, "Start date is required"),
  endDate: z.string().min(10, "End date is required")
});

export type CreateCampaignFormValues = z.infer<typeof createCampaignSchema>;
