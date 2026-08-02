import { z } from "zod";

export const createCampaignSchema = z.object({
  name: z.string().min(2, "Campaign name is required"),
  type: z.string().min(1, "Campaign type is required"),
  platform: z.string().min(1, "Platform is required"),
  budget: z.coerce.number().positive("Budget must be greater than zero"),
  start_date: z.string().min(10, "Start date is required"),
  end_date: z.string().min(10, "End date is required"),
  extra_data: z.string().optional().refine(
    val => {
      if (!val) return true;
      try {
        JSON.parse(val);
        return true;
      } catch {
        return false;
      }
    },
    { message: "Must be a valid JSON object" }
  )
});

export type CreateCampaignFormValues = z.infer<typeof createCampaignSchema>;
