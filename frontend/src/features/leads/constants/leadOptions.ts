import { LeadPriority, LeadSource, LeadStage } from "@/features/leads/types/lead";

export const leadStageOptions: Array<LeadStage | "All"> = [
  "All",
  "New",
  "Qualified",
  "Negotiation",
  "Won",
  "Future Perspective"
];

export const leadSourceOptions: Array<LeadSource | "All"> = [
  "All",
  "Facebook",
  "Instagram",
  "Google Ads",
  "Website",
  "WhatsApp",
  "Walk-in",
  "Referral",
  "Channel Partner",
  "Client Reference",
  "Exhibition/Event",
  "JustDial",
  "Other"
];

export const leadPriorityOptions: Array<LeadPriority | "All"> = [
  "All",
  "Hot",
  "Warm",
  "Cold"
];
