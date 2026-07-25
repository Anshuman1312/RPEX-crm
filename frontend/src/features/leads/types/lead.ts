export type LeadStage = "New" | "Qualified" | "Negotiation" | "Won" | "Lost";
export type LeadSource =
  | "Facebook"
  | "Instagram"
  | "Google Ads"
  | "Website"
  | "WhatsApp"
  | "Walk-in"
  | "Referral"
  | "Channel Partner"
  | "Client Reference"
  | "Exhibition/Event"
  | "JustDial"
  | "Other";
export type LeadPriority = "Hot" | "Warm" | "Cold";

export interface LeadRecord {
  id: string;
  name: string;
  email: string;
  phone: string;
  source: LeadSource;
  stage: LeadStage;
  priority: LeadPriority;
  owner: string;
  budget: number;
  nextFollowUp: string;
  createdAt: string;
}

export interface LeadFilters {
  search?: string;
  stage?: LeadStage | "All";
  source?: LeadSource | "All";
}

export interface LeadStats {
  total: number;
  newLeads: number;
  qualified: number;
  won: number;
}

export interface LeadListResponse {
  items: LeadRecord[];
  total: number;
  stats: LeadStats;
}

export interface CreateLeadInput {
  name: string;
  email: string;
  phone: string;
  source: LeadSource;
  priority: LeadPriority;
  owner: string;
  budget: number;
  nextFollowUp: string;
}
