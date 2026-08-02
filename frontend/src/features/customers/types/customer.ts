export interface CustomerRecord {
  id: string;
  customer_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  alternate_phone?: string;
  company_name?: string;
  customer_type: string;
  status: string;
  referred_by_user_id?: string;
  referred_by_date?: string;
  lead_converted_from_id?: string;
  lead_converted_date?: string;
  preferred_contact_method?: string;
  preferred_language?: string;
  gstin?: string;
  pan?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerFilters {
  search?: string;
  statuses?: string;
  customer_types?: string;
}

export interface CustomerStats {
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  total: number;
}

export interface CustomerListResponse {
  items: CustomerRecord[];
  total: number;
  stats: CustomerStats;
}

export interface CreateCustomerInput {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  alternate_phone?: string;
  company_name?: string;
  customer_type: string;
  referred_by_user_id?: string;
  lead_converted_from_id?: string;
  preferred_contact_method?: string;
  preferred_language?: string;
  gstin?: string;
  pan?: string;
  notes?: string;
}
