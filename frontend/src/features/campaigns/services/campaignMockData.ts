import {
  CampaignListResponse,
  CampaignRecord,
  CampaignStats,
  CreateCampaignInput
} from "@/features/campaigns/types/campaign";

function formatDate(offsetDays: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

export const initialCampaignRecords: CampaignRecord[] = [
  {
    id: "CP-3001",
    name: "Monsoon Inventory Push",
    channel: "WhatsApp",
    status: "Running",
    owner: "Riya",
    budget: 180000,
    startDate: formatDate(-8),
    endDate: formatDate(14),
    leadsGenerated: 42,
    updatedAt: formatDate(-1)
  },
  {
    id: "CP-3002",
    name: "Premium Tower Launch",
    channel: "Email",
    status: "Completed",
    owner: "Aman",
    budget: 420000,
    startDate: formatDate(-35),
    endDate: formatDate(-5),
    leadsGenerated: 116,
    updatedAt: formatDate(-5)
  },
  {
    id: "CP-3003",
    name: "Referral Booster Week",
    channel: "Referral",
    status: "Paused",
    owner: "Priya",
    budget: 90000,
    startDate: formatDate(-10),
    endDate: formatDate(10),
    leadsGenerated: 19,
    updatedAt: formatDate(-2)
  },
  {
    id: "CP-3004",
    name: "Site Visit Nurture Funnel",
    channel: "SMS",
    status: "Draft",
    owner: "Rohan",
    budget: 65000,
    startDate: formatDate(2),
    endDate: formatDate(21),
    leadsGenerated: 0,
    updatedAt: formatDate(0)
  }
];

export function buildCampaignStats(records: CampaignRecord[]): CampaignStats {
  return {
    total: records.length,
    running: records.filter(record => record.status === "Running").length,
    completed: records.filter(record => record.status === "Completed").length,
    leadsGenerated: records.reduce((sum, record) => sum + record.leadsGenerated, 0)
  };
}

export function buildCampaignListResponse(records: CampaignRecord[]): CampaignListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildCampaignStats(records)
  };
}

export function createCampaignRecord(payload: CreateCampaignInput, index: number): CampaignRecord {
  return {
    id: `CP-${3000 + index}`,
    name: payload.name,
    channel: payload.channel,
    status: "Draft",
    owner: payload.owner,
    budget: payload.budget,
    startDate: payload.startDate,
    endDate: payload.endDate,
    leadsGenerated: 0,
    updatedAt: new Date().toISOString().slice(0, 10)
  };
}
