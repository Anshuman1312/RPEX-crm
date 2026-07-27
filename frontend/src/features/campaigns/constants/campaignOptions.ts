import { CampaignChannel, CampaignStatus } from "@/features/campaigns/types/campaign";

export const campaignChannelOptions: Array<CampaignChannel | "All"> = [
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
