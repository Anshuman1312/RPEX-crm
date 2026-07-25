import {
  CalendarEventStatus,
  CalendarEventType
} from "@/features/calendar/types/calendar";

export const calendarEventTypeOptions: Array<CalendarEventType | "All"> = [
  "All",
  "Meeting",
  "Site Visit",
  "Follow-up",
  "Deadline"
];

export const calendarEventStatusOptions: Array<CalendarEventStatus | "All"> = [
  "All",
  "Upcoming",
  "Completed",
  "Missed",
  "Cancelled"
];
