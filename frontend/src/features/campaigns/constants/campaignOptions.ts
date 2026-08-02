import { CampaignStatus } from "@/features/campaigns/types/campaign";

export const campaignTypeOptions: string[] = [
  "All",
  "WhatsApp",
  "Email",
  "SMS",
  "Social",
  "Referral"
];

export const campaignStatusOptions: Array<CampaignStatus | "All"> = [
  "All",
  "Draft",
  "Running",
  "Paused",
  "Completed"
];
