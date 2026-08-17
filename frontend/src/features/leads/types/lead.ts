export type LeadStatus = "New" | "Qualified" | "Negotiation" | "Won" | "Future Perspective";
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
  fullName: string;
  email: string;
  phone: string;
  source: LeadSource;
  status: LeadStatus;
  priority: LeadPriority;
  assignedToUserId: string;
  budget: number;
  nextFollowupAt: string;
  createdAt: string;
}

export interface LeadFilters {
  search?: string;
  status?: LeadStatus | "All";
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
  fullName: string;
  email: string;
  phone: string;
  source: LeadSource;
  priority: LeadPriority;
  assignedToUserId: string;
  budget: number;
  nextFollowupAt: string;
  status: LeadStatus;
}

