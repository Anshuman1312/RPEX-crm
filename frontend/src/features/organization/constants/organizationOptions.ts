import {
  OrganizationIndustry,
  OrganizationStatus
} from "@/features/organization/types/organization";

export const organizationIndustryOptions: Array<OrganizationIndustry | "All"> = [
  "All",
  "Real Estate",
  "Construction",
  "Finance",
  "Technology",
  "Retail"
];

export const organizationStatusOptions: Array<OrganizationStatus | "All"> = [
  "All",
  "Active",
  "Suspended",
  "Inactive"
];
