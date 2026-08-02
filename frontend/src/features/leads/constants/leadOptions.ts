import { LeadPriority, LeadSource, LeadStatus } from "@/features/leads/types/lead";

export const leadStatusOptions: Array<LeadStatus | "All"> = [
  "All",
  "New",
  "Qualified",
  "Negotiation",
  "Won",
  "Future Perspective"
];


export const leadSourceOptions: Array<LeadSource | "All"> = [
  "All",
  //"Facebook",
 // "Instagram",
 // "Google Ads",
  "Website",
  //"WhatsApp",
  "Walk-in",
  "Referral",
  "Channel Partner",
  "Client Reference",
  "Exhibition/Event",
  //"JustDial",
  "Other"
];

export const leadPriorityOptions: Array<LeadPriority | "All"> = [
  "All",
  "Hot",
  "Warm",
  "Cold"
];
