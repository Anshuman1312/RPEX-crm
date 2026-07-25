export type OrganizationIndustry = "Real Estate" | "Construction" | "Finance" | "Technology" | "Retail";
export type OrganizationStatus = "Active" | "Suspended" | "Inactive";

export interface OrganizationRecord {
  id: string;
  name: string;
  industry: OrganizationIndustry;
  status: OrganizationStatus;
  primaryContact: string;
  email: string;
  phone: string;
  city: string;
  employeeCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface OrganizationFilters {
  search?: string;
  industry?: OrganizationIndustry | "All";
  status?: OrganizationStatus | "All";
}

export interface OrganizationStats {
  total: number;
  active: number;
  suspended: number;
  inactive: number;
}

export interface OrganizationListResponse {
  items: OrganizationRecord[];
  total: number;
  stats: OrganizationStats;
}

export interface CreateOrganizationInput {
  name: string;
  industry: OrganizationIndustry;
  primaryContact: string;
  email: string;
  phone: string;
  city: string;
  employeeCount: number;
}
