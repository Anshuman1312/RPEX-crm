export type CustomerTitle = "Mr." | "Miss" | "Mrs";
export type CustomerPurpose = "Investment" | "Self Use" | "Business";
export type CustomerPropertyType = "Plot" | "Villa" | "Flat" | "Commercial";

export interface CustomerRecord {
  id: string;
  title: CustomerTitle;
  name: string; // Full Name
  phone: string; // Mobile Number (Primary)
  alternatePhone?: string; // Alternate Mobile Number
  email: string; // Email ID
  occupation?: string;
  address?: string;
  budgetRange?: string;
  timeDuration?: string;
  purpose: CustomerPurpose;
  propertyType: CustomerPropertyType;
  remarks?: string;
}

export interface CustomerFilters {
  search?: string;
  purpose?: CustomerPurpose | "All";
  propertyType?: CustomerPropertyType | "All";
}

export interface CustomerStats {
  total: number;
  investment: number;
  selfUse: number;
  business: number;
}

export interface CustomerListResponse {
  items: CustomerRecord[];
  total: number;
  stats: CustomerStats;
}

export interface CreateCustomerInput {
  title: CustomerTitle;
  name: string;
  phone: string;
  alternatePhone?: string;
  email: string;
  occupation?: string;
  address?: string;
  budgetRange?: string;
  timeDuration?: string;
  purpose: CustomerPurpose;
  propertyType: CustomerPropertyType;
  remarks?: string;
}
