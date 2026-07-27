import {
  CreateOrganizationInput,
  OrganizationListResponse,
  OrganizationRecord,
  OrganizationStats
} from "@/features/organization/types/organization";

function formatDate(offsetDays: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

export const initialOrganizationRecords: OrganizationRecord[] = [
  {
    id: "ORG-1001",
    name: "RPEX Group",
    industry: "Real Estate",
    status: "Active",
    primaryContact: "Arjun Mehta",
    email: "arjun@rpexgroup.com",
    phone: "+91 98100 11223",
    city: "Mumbai",
    employeeCount: 120,
    createdAt: formatDate(-720),
    updatedAt: formatDate(-1)
  },
  {
    id: "ORG-1002",
    name: "Apex Ventures",
    industry: "Construction",
    status: "Active",
    primaryContact: "Kavita Rao",
    email: "kavita@apexventures.com",
    phone: "+91 98200 33441",
    city: "Pune",
    employeeCount: 65,
    createdAt: formatDate(-480),
    updatedAt: formatDate(-4)
  },
  {
    id: "ORG-1003",
    name: "Orbit Realty",
    industry: "Real Estate",
    status: "Suspended",
    primaryContact: "Vikas Nair",
    email: "vikas@orbitrealty.in",
    phone: "+91 99110 55667",
    city: "Bangalore",
    employeeCount: 30,
    createdAt: formatDate(-310),
    updatedAt: formatDate(-12)
  },
  {
    id: "ORG-1004",
    name: "BlueStone Estates",
    industry: "Finance",
    status: "Inactive",
    primaryContact: "Neha Kapoor",
    email: "neha@bluestoneestates.com",
    phone: "+91 97000 88990",
    city: "Delhi",
    employeeCount: 14,
    createdAt: formatDate(-200),
    updatedAt: formatDate(-30)
  }
];

export function buildOrganizationStats(records: OrganizationRecord[]): OrganizationStats {
  return {
    total: records.length,
    active: records.filter(r => r.status === "Active").length,
    suspended: records.filter(r => r.status === "Suspended").length,
    inactive: records.filter(r => r.status === "Inactive").length
  };
}

export function buildOrganizationListResponse(
  records: OrganizationRecord[]
): OrganizationListResponse {
  return { items: records, total: records.length, stats: buildOrganizationStats(records) };
}

export function createOrganizationRecord(
  payload: CreateOrganizationInput,
  index: number
): OrganizationRecord {
  const today = new Date().toISOString().slice(0, 10);
  return {
    id: `ORG-${1000 + index}`,
    name: payload.name,
    industry: payload.industry,
    status: "Active",
    primaryContact: payload.primaryContact,
    email: payload.email,
    phone: payload.phone,
    city: payload.city,
    employeeCount: payload.employeeCount,
    createdAt: today,
    updatedAt: today
  };
}
