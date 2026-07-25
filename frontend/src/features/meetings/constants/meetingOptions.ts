import { MeetingStatus, MeetingType } from "@/features/meetings/types/meeting";

export const meetingTypeOptions: Array<MeetingType | "All"> = [
  "All",
  "Client Call",
  "Site Visit",
  "Internal",
  "Vendor"
];

export const meetingStatusOptions: Array<MeetingStatus | "All"> = [
  "All",
  "Scheduled",
  "Completed",
  "Cancelled",
  "Rescheduled"
];
