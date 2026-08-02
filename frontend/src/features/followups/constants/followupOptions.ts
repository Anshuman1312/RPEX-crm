import {
  FollowUpType,
  FollowUpStatus
} from "@/features/followups/types/followup";

export const followUpTypeOptions: Array<FollowUpType | "All"> = [
  "All",
  "call",
  "email",
  "sms",
  "meeting",
  "site_visit",
  "video_call",
  "whatsapp",
  "other"
];

export const followUpPriorityOptions = [
  "All",
  "Low",
  "Medium",
  "High"
];

export const followUpStatusOptions: Array<FollowUpStatus | "All"> = [
  "All",
  "scheduled",
  "completed",
  "cancelled",
  "overdue"
];
