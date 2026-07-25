import {
  FollowUpChannel,
  FollowUpPriority,
  FollowUpStatus
} from "@/features/followups/types/followup";

export const followUpChannelOptions: Array<FollowUpChannel | "All"> = [
  "All",
  "Call",
  "WhatsApp",
  "Email",
  "Meeting"
];

export const followUpPriorityOptions: Array<FollowUpPriority | "All"> = [
  "All",
  "Low",
  "Medium",
  "High"
];

export const followUpStatusOptions: Array<FollowUpStatus | "All"> = [
  "All",
  "Pending",
  "Done",
  "Missed",
  "Rescheduled"
];
