import { z } from "zod";
import { calendarEventTypeOptions } from "@/features/calendar/constants/calendarOptions";

export const createCalendarEventSchema = z.object({
  title: z.string().min(2, "Event title is required"),
  type: z.enum(calendarEventTypeOptions.filter(option => option !== "All") as ["Meeting", "Site Visit", "Follow-up", "Deadline"]),
  owner: z.string().min(2, "Owner is required"),
  attendee: z.string().min(2, "Attendee is required"),
  eventAt: z.string().min(16, "Event date and time is required"),
  location: z.string().min(2, "Location is required"),
  linkedModule: z.string().min(2, "Linked module is required")
});

export type CreateCalendarEventFormValues = z.infer<typeof createCalendarEventSchema>;
