import { z } from "zod";
import { notificationTypeOptions } from "@/features/notifications/constants/notificationOptions";

export const createNotificationSchema = z.object({
  title: z.string().min(2, "Notification title is required"),
  message: z.string().min(2, "Message is required"),
  type: z.enum(notificationTypeOptions.filter(option => option !== "All") as ["Reminder", "Alert", "Approval", "System"]),
  owner: z.string().min(2, "Owner is required"),
  sourceModule: z.string().min(2, "Source module is required")
});

export type CreateNotificationFormValues = z.infer<typeof createNotificationSchema>;
