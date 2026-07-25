import { CreateLeadInput, LeadListResponse, LeadRecord, LeadStats } from "@/features/leads/types/lead";

const today = new Date();

function formatDate(offset: number) {
  const date = new Date(today);
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

export const initialLeadRecords: LeadRecord[] = [
  {
    id: "LD-1001",
    name: "Aarav Mehta",
    email: "aarav.mehta@example.com",
    phone: "+91 98220 11234",
    source: "Website",
    stage: "New",
    priority: "Hot",
    owner: "Riya",
    budget: 2500000,
    nextFollowUp: formatDate(1),
    createdAt: formatDate(-3)
  },
  {
    id: "LD-1002",
    name: "Kavya Sharma",
    email: "kavya.sharma@example.com",
    phone: "+91 98110 22344",
    source: "Referral",
    stage: "Qualified",
    priority: "Warm",
    owner: "Aman",
    budget: 4200000,
    nextFollowUp: formatDate(2),
    createdAt: formatDate(-8)
  },
  {
    id: "LD-1003",
    name: "Neel Jain",
    email: "neel.jain@example.com",
    phone: "+91 99555 12987",
    source: "Google Ads",
    stage: "Negotiation",
    priority: "Cold",
    owner: "Priya",
    budget: 3600000,
    nextFollowUp: formatDate(3),
    createdAt: formatDate(-10)
  },
  {
    id: "LD-1004",
    name: "Ishita Rao",
    email: "ishita.rao@example.com",
    phone: "+91 99223 40011",
    source: "Website",
    stage: "Won",
    priority: "Hot",
    owner: "Rohan",
    budget: 5100000,
    nextFollowUp: formatDate(0),
    createdAt: formatDate(-14)
  },
  {
    id: "LD-1005",
    name: "Samar Verma",
    email: "samar.verma@example.com",
    phone: "+91 97777 30303",
    source: "Channel Partner",
    stage: "Lost",
    priority: "Cold",
    owner: "Riya",
    budget: 2100000,
    nextFollowUp: formatDate(5),
    createdAt: formatDate(-20)
  }
];

export function buildLeadStats(records: LeadRecord[]): LeadStats {
  return {
    total: records.length,
    newLeads: records.filter(record => record.stage === "New").length,
    qualified: records.filter(record => record.stage === "Qualified").length,
    won: records.filter(record => record.stage === "Won").length
  };
}

export function buildLeadListResponse(records: LeadRecord[]): LeadListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildLeadStats(records)
  };
}

export function createLeadRecord(payload: CreateLeadInput, index: number): LeadRecord {
  return {
    id: `LD-${1000 + index}`,
    name: payload.name,
    email: payload.email,
    phone: payload.phone,
    source: payload.source,
    stage: "New",
    priority: payload.priority,
    owner: payload.owner,
    budget: payload.budget,
    nextFollowUp: payload.nextFollowUp,
    createdAt: new Date().toISOString().slice(0, 10)
  };
}
