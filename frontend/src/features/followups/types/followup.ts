export type FollowUpType =
  | "call"
  | "email"
  | "sms"
  | "meeting"
  | "site_visit"
  | "video_call"
  | "whatsapp"
  | "other";

export type FollowUpStatus = "scheduled" | "completed" | "cancelled" | "overdue";

export interface FollowUpTaskRecord {
  id: string;
  task_type: string;
  task_number: number;
  title: string;
  description?: string;
  status: string;
  scheduled_at?: string;
  is_required: boolean;
}

export interface FollowUpRecord {
  id: string;
  followup_number: string;
  type: FollowUpType;
  subject: string;
  description?: string;
  scheduled_at: string;
  completed_at?: string;
  status: FollowUpStatus;
  priority: number; // 0 = Low, 1 = Medium, 2 = High
  is_critical: boolean;
  notes?: string;
  lead_id?: string;
  customer_id?: string;
  assigned_to_user_id?: string;
  created_by_user_id?: string;
  task_count?: number;
  tasks?: FollowUpTaskRecord[];
  created_at: string;
  updated_at: string;
}

export interface FollowUpFilters {
  search?: string;
  type?: FollowUpType | "All";
  priority?: "Low" | "Medium" | "High" | "All";
  status?: FollowUpStatus | "All";
  lead_id?: string;
  customer_id?: string;
  assigned_to_user_id?: string;
  is_critical?: boolean;
}

export interface FollowUpStats {
  total: number;
  pending: number;
  dueToday: number;
  done: number;
}

export interface FollowUpListResponse {
  items: FollowUpRecord[];
  total: number;
  stats: FollowUpStats;
}

export interface CreateFollowUpInput {
  type: FollowUpType;
  subject: string;
  description?: string;
  scheduled_at: string;
  assigned_to_user_id?: string;
  lead_id?: string;
  customer_id?: string;
  priority: number;
  is_critical: boolean;
  notes?: string;
  tasks?: {
    task_type: string;
    title: string;
    description?: string;
    scheduled_at?: string;
    is_required: boolean;
  }[];
}
