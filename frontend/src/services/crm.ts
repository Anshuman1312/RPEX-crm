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
  extra_data: Record<string, unknown>;
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
  channel: string;
  reach: number;
  leads: number;
  cpl: number;
  roas: number;
  conversion: number;
};

export type TelecallingCallItem = {
  id: string;
  call_date: string;
  telecaller_id: string;
  lead_id: string | null;
  customer_name: string;
  status: string;
  call_duration_sec: number;
  call_recording_url: string | null;
  daily_target: number;
  notes: string | null;
  created_at: string;
};

export type TelecallingPerformanceItem = {
  telecaller_id: string;
  telecaller_name: string;
  date: string;
  daily_calls: number;
  connected: number;
  not_connected: number;
  interested: number;
  total_duration_sec: number;
  daily_target: number;
  performance_percent: number;
};

export type SalesTeamReportItem = {
  id: string;
  report_date: string;
  sales_executive_id: string;
  sales_executive_name: string;
  target_value: string;
  achieved_sales_value: string;
  bookings_count: number;
  commission_value: string;
  site_visits_count: number;
  attendance_status: string;
  daily_report: string | null;
  created_at: string;
};

export type SalesTeamLeaderboardItem = {
  sales_executive_id: string;
  sales_executive_name: string;
  target_value: number;
  achieved_sales_value: number;
  bookings_count: number;
  commission_value: number;
  site_visits_count: number;
  present_days: number;
  achievement_percent: number;
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

export type ProjectItem = {
  id: string;
  name: string;
  developer_name: string;
  sole_selling_partner: string | null;
  location: string;
  google_maps_url: string | null;
  project_status: string;
  total_inventory: number;
  sold_inventory: number;
  available_inventory: number;
  price_list: Array<Record<string, unknown>>;
  payment_plans: Array<Record<string, unknown>>;
  documents: Array<Record<string, unknown>>;
  gallery: Array<Record<string, unknown>>;
  videos: Array<Record<string, unknown>>;
  brochure: Record<string, unknown>;
  legal_status: string | null;
  amenities: string[];
  nearby_landmarks: string[];
  created_at: string;
};

export type InventoryUnitItem = {
  id: string;
  project_id: string;
  plot_no: string;
  size: string;
  facing: string | null;
  is_corner: boolean;
  corner_or_normal: "CORNER" | "NORMAL";
  price: string;
  booking_status: "AVAILABLE" | "HOLD" | "BOOKED" | "SOLD";
  customer_name: string | null;
  sales_executive: string | null;
  booking_date: string | null;
  agreement_status: string | null;
  payment_status: string | null;
  color_code: "GREEN" | "YELLOW" | "BLUE" | "RED";
  created_at: string;
};

export type SiteVisitItem = {
  id: string;
  visit_date: string;
  visit_time: string;
  customer_name: string;
  sales_executive: string;
  pickup_required: boolean;
  vehicle_assigned: string | null;
  driver: string | null;
  attendance: string;
  feedback: string | null;
  outcome: string | null;
  created_by: string;
  created_at: string;
};

export async function fetchLeads(params: Record<string, string | number | undefined>) {
  const response = await api.get<LeadListResponse>("/leads", { params });
  return response.data;
}

export async function updateLeadStatus(leadId: string, status: string) {
  const response = await api.patch(`/leads/${leadId}/status`, { status });
  return response.data;
}

export async function createLead(payload: {
  name: string;
  phone: string;
  email: string;
  source: string;
  status: string;
  budget: string | null;
  preferred_location: string | null;
  property_type: string | null;
  notes: string | null;
  interested_project: string | null;
  assigned_to: string | null;
  assigned_to_name: string | null;
  lead_score: number | null;
}) {
  const response = await api.post("/leads", payload);
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
  channel: string | null;
  reach: number;
  leads: number;
  roas: number;
  conversion: number;
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

export async function fetchProjects() {
  const response = await api.get<ProjectItem[]>("/projects");
  return response.data;
}

export async function createProject(payload: {
  name: string;
  developer_name: string;
  sole_selling_partner: string | null;
  location: string;
  google_maps_url: string | null;
  project_status: string;
  total_inventory: number;
  sold_inventory: number;
  price_list: Array<Record<string, unknown>>;
  payment_plans: Array<Record<string, unknown>>;
  documents: Array<Record<string, unknown>>;
  gallery: Array<Record<string, unknown>>;
  videos: Array<Record<string, unknown>>;
  brochure: Record<string, unknown>;
  legal_status: string | null;
  amenities: string[];
  nearby_landmarks: string[];
}) {
  const response = await api.post("/projects", payload);
  return response.data;
}

export async function fetchInventoryUnits(projectId?: string) {
  const response = await api.get<InventoryUnitItem[]>("/inventory", {
    params: projectId ? { project_id: projectId } : undefined
  });
  return response.data;
}

export async function createInventoryUnit(payload: {
  project_id: string;
  plot_no: string;
  size: string;
  facing: string | null;
  is_corner: boolean;
  price: number;
  booking_status: "AVAILABLE" | "HOLD" | "BOOKED" | "SOLD";
  customer_name: string | null;
  sales_executive: string | null;
  booking_date: string | null;
  agreement_status: string | null;
  payment_status: string | null;
}) {
  const response = await api.post("/inventory", payload);
  return response.data;
}

export async function fetchSiteVisits() {
  const response = await api.get<SiteVisitItem[]>("/site-visits");
  return response.data;
}

export async function createSiteVisit(payload: {
  visit_date: string;
  visit_time: string;
  customer_name: string;
  sales_executive: string;
  pickup_required: boolean;
  vehicle_assigned: string | null;
  driver: string | null;
  attendance: string;
  feedback: string | null;
  outcome: string | null;
}) {
  const response = await api.post("/site-visits", payload);
  return response.data;
}

export async function fetchFollowups() {
  const response = await api.get("/followups");
  return response.data as Array<{
    id: string;
    lead_id: string;
    assigned_to: string;
    followup_date: string;
    next_followup_date: string | null;
    remark: string;
    call_notes: string | null;
    whatsapp_notes: string | null;
    meeting_notes: string | null;
    voice_recording_url: string | null;
    sms_log: Array<Record<string, unknown>>;
    followup_history: Array<Record<string, unknown>>;
    auto_reminder_enabled: boolean;
    status: string;
  }>;
}

export async function createFollowup(payload: {
  lead_id: string;
  assigned_to: string;
  followup_date: string;
  next_followup_date: string | null;
  remark: string;
  call_notes: string | null;
  whatsapp_notes: string | null;
  meeting_notes: string | null;
  voice_recording_url: string | null;
  sms_log: Array<Record<string, unknown>>;
  auto_reminder_enabled: boolean;
  status: string;
}) {
  const response = await api.post("/followups", payload);
  return response.data;
}

export async function updateFollowup(followupId: string, payload: {
  next_followup_date?: string | null;
  remark?: string | null;
  call_notes?: string | null;
  whatsapp_notes?: string | null;
  meeting_notes?: string | null;
  voice_recording_url?: string | null;
  sms_log?: Array<Record<string, unknown>>;
  auto_reminder_enabled?: boolean;
  status?: string;
}) {
  const response = await api.patch(`/followups/${followupId}`, payload);
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
    birth_date: string | null;
    anniversary_date: string | null;
    extra_data: Record<string, unknown>;
    created_at: string;
    partner_user_id: string | null;
  }>;
}

export async function createCustomer(payload: {
  full_name: string;
  email: string | null;
  phone: string;
  city: string | null;
  birth_date: string | null;
  anniversary_date: string | null;
  extra_data: Record<string, unknown>;
  partner_user_id: string | null;
}) {
  const response = await api.post("/customers", payload);
  return response.data;
}

export async function fetchTelecallingCalls() {
  const response = await api.get<TelecallingCallItem[]>("/telecalling/calls");
  return response.data;
}

export async function createTelecallingCall(payload: {
  call_date: string;
  telecaller_id: string;
  lead_id: string | null;
  customer_name: string;
  status: string;
  call_duration_sec: number;
  call_recording_url: string | null;
  daily_target: number;
  notes: string | null;
}) {
  const response = await api.post("/telecalling/calls", payload);
  return response.data;
}

export async function fetchTelecallingPerformance() {
  const response = await api.get<TelecallingPerformanceItem[]>("/telecalling/performance");
  return response.data;
}

export async function fetchSalesTeamReports() {
  const response = await api.get<SalesTeamReportItem[]>("/sales-team/reports");
  return response.data;
}

export async function createSalesTeamReport(payload: {
  report_date: string;
  sales_executive_id: string;
  sales_executive_name: string;
  target_value: number;
  achieved_sales_value: number;
  bookings_count: number;
  commission_value: number;
  site_visits_count: number;
  attendance_status: string;
  daily_report: string | null;
}) {
  const response = await api.post("/sales-team/reports", payload);
  return response.data;
}

export async function fetchSalesTeamLeaderboard() {
  const response = await api.get<SalesTeamLeaderboardItem[]>("/sales-team/leaderboard");
  return response.data;
}

export async function fetchBookings() {
  const response = await api.get("/sales/bookings");
  return response.data as Array<{
    id: string;
    customer_id: string;
    project_name: string;
    plot_number: string | null;
    booking_value: string;
    booking_date: string;
    payment_method: string | null;
    receipt: string | null;
    agreement_date: string | null;
    emi_details: string | null;
    loan_required: boolean;
    kyc_documents: string[];
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
  payment_method: string | null;
  receipt: string | null;
  plot_number: string | null;
  agreement_date: string | null;
  emi_details: string | null;
  loan_required: boolean;
  kyc_documents: string[];
  partner_user_id: string | null;
}) {
  const response = await api.post("/sales/bookings", payload);
  return response.data;
}

export type BookingDocuments = {
  booking_receipt: Record<string, unknown>;
  booking_form: Record<string, unknown>;
  agreement_checklist: {
    title: string;
    items: Array<{ name: string; done: boolean }>;
  };
};

export async function fetchBookingDocuments(bookingId: string) {
  const response = await api.get<BookingDocuments>(`/sales/bookings/${bookingId}/documents`);
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
