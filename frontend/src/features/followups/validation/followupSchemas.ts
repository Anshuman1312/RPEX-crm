import { z } from "zod";

export const createFollowUpSchema = z.object({
  type: z.enum(["call", "email", "sms", "meeting", "site_visit", "video_call", "whatsapp", "other"]),
  subject: z.string().min(1, "Subject is required"),
  description: z.string().optional().or(z.literal("")),
  scheduled_at: z.string().min(16, "Scheduled date and time is required"),
  assigned_to_user_id: z.string().optional().or(z.literal("")),
  lead_id: z.string().optional().or(z.literal("")),
  customer_id: z.string().optional().or(z.literal("")),
  priority: z.coerce.number().min(0).max(2),
  is_critical: z.preprocess(
    (val) => {
      if (typeof val === "string") return val === "true";
      return !!val;
    },
    z.boolean().default(false)
  ),
  notes: z.string().optional().or(z.literal("")),
  tasks: z.array(
    z.object({
      task_type: z.string().min(1, "Task type is required"),
      title: z.string().min(1, "Task title is required"),
      description: z.string().optional().or(z.literal("")),
      scheduled_at: z.string().optional().or(z.literal("")),
      is_required: z.preprocess(
        (val) => {
          if (typeof val === "string") return val === "true";
          return !!val;
        },
        z.boolean().default(false)
      )
    })
  ).optional()
}).refine(data => data.lead_id || data.customer_id, {
  message: "Either Lead ID or Customer ID must be provided",
  path: ["lead_id"]
});

export type CreateFollowUpFormValues = z.infer<typeof createFollowUpSchema>;
