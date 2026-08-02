export type CampaignStatus = "Draft" | "Running" | "Paused" | "Completed";

export interface CampaignRecord {
  id: string;
  name: string;
  type: string;
  platform: string;
  budget: number;
  start_date: string;
  end_date: string;
  extra_data: Record<string, any>;
  status: CampaignStatus;
  leadsGenerated: number;
  updatedAt: string;
}

export interface CampaignFilters {
  search?: string;
  type?: string | "All";
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
  type: string;
  platform: string;
  budget: number;
  start_date: string;
  end_date: string;
  extra_data: Record<string, any>;
}
