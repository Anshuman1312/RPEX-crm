import { z } from "zod";
import { meetingTypeOptions } from "@/features/meetings/constants/meetingOptions";

export const createMeetingSchema = z.object({
  title: z.string().min(2, "Meeting title is required"),
  type: z.enum(meetingTypeOptions.filter(option => option !== "All") as ["Client Call", "Site Visit", "Internal", "Vendor"]),
  host: z.string().min(2, "Host is required"),
  attendee: z.string().min(2, "Attendee is required"),
  scheduledAt: z.string().min(16, "Scheduled date and time is required"),
  location: z.string().min(2, "Location is required"),
  notes: z.string().min(2, "Notes are required")
});

export type CreateMeetingFormValues = z.infer<typeof createMeetingSchema>;
