export type CampaignChannel = "WhatsApp" | "Email" | "SMS" | "Social" | "Referral";
export type CampaignStatus = "Draft" | "Running" | "Paused" | "Completed";

export interface CampaignRecord {
  id: string;
  name: string;
  channel: CampaignChannel;
  status: CampaignStatus;
  owner: string;
  budget: number;
  startDate: string;
  endDate: string;
  leadsGenerated: number;
  updatedAt: string;
}

export interface CampaignFilters {
  search?: string;
  channel?: CampaignChannel | "All";
  status?: CampaignStatus | "All";
}

export interface CampaignStats {
  total: number;
  running: number;
  completed: number;
  leadsGenerated: number;
}

export interface CampaignListResponse {
  items: CampaignRecord[];
  total: number;
  stats: CampaignStats;
}

export interface CreateCampaignInput {
  name: string;
  channel: CampaignChannel;
  owner: string;
  budget: number;
  startDate: string;
  endDate: string;
}
