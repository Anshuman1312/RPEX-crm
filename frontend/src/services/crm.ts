import { api } from "./api";

export type LeadItem = {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: string;
  source: string | null;
  medium: string | null;
  campaign_id: string | null;
  assigned_to: string | null;
  extra_data: Record<string, string>;
  created_at: string;
};

export type LeadListResponse = {
  items: LeadItem[];
  total: number;
  page: number;
  page_size: number;
};

export type CampaignItem = {
  id: string;
  name: string;
  type: string;
  platform: string;
  budget: string;
  start_date: string | null;
  end_date: string | null;
};

export type KeywordItem = {
  id: string;
  keyword: string;
  url: string;
  target_position: number | null;
  current_position: number | null;
  traffic: number;
  clicks: number;
  impressions: number;
};

export async function fetchLeads(params: Record<string, string | number | undefined>) {
  const response = await api.get<LeadListResponse>("/leads", { params });
  return response.data;
}

export async function updateLeadStatus(leadId: string, status: string) {
  const response = await api.patch(`/leads/${leadId}/status`, { status });
  return response.data;
}

export async function fetchCampaigns() {
  const response = await api.get<CampaignItem[]>("/campaigns");
  return response.data;
}

export async function createCampaign(payload: {
  name: string;
  type: string;
  platform: string;
  budget: number;
  start_date: string | null;
  end_date: string | null;
}) {
  const response = await api.post("/campaigns", payload);
  return response.data;
}

export async function fetchKeywords() {
  const response = await api.get<KeywordItem[]>("/keywords");
  return response.data;
}

export async function createKeyword(payload: {
  keyword: string;
  url: string;
  target_position: number | null;
  current_position: number | null;
  traffic: number;
  clicks: number;
  impressions: number;
  campaign_id: string;
}) {
  const response = await api.post("/keywords", payload);
  return response.data;
}

export async function fetchFollowups() {
  const response = await api.get("/followups");
  return response.data as Array<{ id: string; lead_id: string; followup_date: string; remark: string; status: string }>;
}

export async function createFollowup(payload: {
  lead_id: string;
  assigned_to: string;
  followup_date: string;
  remark: string;
  status: string;
}) {
  const response = await api.post("/followups", payload);
  return response.data;
}
