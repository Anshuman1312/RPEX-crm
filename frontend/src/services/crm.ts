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

export async function fetchCustomers() {
  const response = await api.get("/customers");
  return response.data as Array<{
    id: string;
    full_name: string;
    email: string | null;
    phone: string;
    city: string | null;
    created_at: string;
    partner_user_id: string | null;
  }>;
}

export async function createCustomer(payload: {
  full_name: string;
  email: string | null;
  phone: string;
  city: string | null;
  partner_user_id: string | null;
}) {
  const response = await api.post("/customers", payload);
  return response.data;
}

export async function fetchBookings() {
  const response = await api.get("/sales/bookings");
  return response.data as Array<{
    id: string;
    customer_id: string;
    project_name: string;
    booking_value: string;
    booking_date: string;
    status: string;
    partner_user_id: string | null;
  }>;
}

export async function createBooking(payload: {
  customer_id: string;
  project_name: string;
  unit_code: string | null;
  booking_value: number;
  booking_date: string;
  partner_user_id: string | null;
}) {
  const response = await api.post("/sales/bookings", payload);
  return response.data;
}

export async function fetchPayments() {
  const response = await api.get("/finance/payments");
  return response.data as Array<{
    id: string;
    customer_id: string;
    booking_id: string | null;
    amount: string;
    payment_date: string;
    payment_mode: string;
    status: string;
    partner_user_id: string | null;
  }>;
}

export async function createPayment(payload: {
  customer_id: string;
  booking_id: string | null;
  amount: number;
  payment_date: string;
  payment_mode: string;
  reference_no: string | null;
}) {
  const response = await api.post("/finance/payments", payload);
  return response.data;
}

export async function fetchInvoices() {
  const response = await api.get("/finance/invoices");
  return response.data as Array<{
    id: string;
    customer_id: string;
    booking_id: string | null;
    invoice_number: string;
    invoice_date: string;
    amount: string;
    gst_amount: string;
    status: string;
    partner_user_id: string | null;
  }>;
}

export async function createInvoice(payload: {
  customer_id: string;
  booking_id: string | null;
  invoice_number: string;
  invoice_date: string;
  amount: number;
  gst_amount: number;
}) {
  const response = await api.post("/finance/invoices", payload);
  return response.data;
}

export async function fetchDocuments() {
  const response = await api.get("/documents");
  return response.data as Array<{
    id: string;
    customer_id: string | null;
    booking_id: string | null;
    category: string;
    file_name: string;
    storage_key: string;
    content_type: string | null;
    size_bytes: number;
    partner_user_id: string | null;
    signed_url: string | null;
  }>;
}

export async function uploadDocument(payload: {
  file: File;
  category: string;
  customer_id: string | null;
  booking_id: string | null;
}) {
  const formData = new FormData();
  formData.append("file", payload.file);

  const params = new URLSearchParams();
  params.set("category", payload.category);
  if (payload.customer_id) {
    params.set("customer_id", payload.customer_id);
  }
  if (payload.booking_id) {
    params.set("booking_id", payload.booking_id);
  }

  const response = await api.post(`/documents/upload?${params.toString()}`, formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
  return response.data;
}

export async function fetchPartnerDashboard() {
  const response = await api.get("/partner/dashboard");
  return response.data as {
    customers: number;
    bookings: number;
    payments: number;
    documents: number;
    total_booking_value: number;
    total_collections: number;
  };
}

export async function fetchPartnerCustomers() {
  const response = await api.get("/partner/customers");
  return response.data as Array<{ id: string; full_name: string; email: string | null; phone: string }>;
}

export async function fetchPartnerBookings() {
  const response = await api.get("/partner/bookings");
  return response.data as Array<{ id: string; customer_id: string; project_name: string; booking_value: string }>;
}

export async function fetchPartnerPayments() {
  const response = await api.get("/partner/payments");
  return response.data as Array<{ id: string; customer_id: string; amount: string; status: string }>;
}

export async function fetchPartnerDocuments() {
  const response = await api.get("/partner/documents");
  return response.data as Array<{ id: string; category: string; file_name: string; storage_key: string; signed_url: string | null }>;
}

export async function fetchDocumentSignedUrl(documentId: string) {
  const response = await api.get<{ id: string; signed_url: string }>(`/documents/${documentId}/signed-url`);
  return response.data;
}

export async function fetchApprovalRequests() {
  const response = await api.get("/approvals", { params: { limit: 100 } });
  return response.data as Array<{
    id: string;
    module: string;
    entity_type: string;
    entity_id: string;
    action: string;
    status: string;
    requested_by: string;
    approver_id: string | null;
    reason: string | null;
    created_at: string;
    updated_at: string;
  }>;
}

export async function createApprovalRequest(payload: {
  module: string;
  entity_type: string;
  entity_id: string;
  action: string;
  approver_id?: string | null;
  reason?: string | null;
  payload?: Record<string, unknown>;
}) {
  const response = await api.post("/approvals", payload);
  return response.data;
}

export async function decideApprovalRequest(requestId: string, status: "APPROVED" | "REJECTED", notes?: string) {
  const response = await api.post(`/approvals/${requestId}/decision`, { status, notes: notes ?? null });
  return response.data;
}
