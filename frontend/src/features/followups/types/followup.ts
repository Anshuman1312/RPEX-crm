export type FollowUpChannel = "Call" | "WhatsApp" | "Email" | "Meeting";
export type FollowUpPriority = "Low" | "Medium" | "High";
export type FollowUpStatus = "Pending" | "Done" | "Missed" | "Rescheduled";

export interface FollowUpRecord {
  id: string;
  leadName: string;
  owner: string;
  scheduledAt: string;
  channel: FollowUpChannel;
  priority: FollowUpPriority;
  status: FollowUpStatus;
  notes: string;
  updatedAt: string;
}

export interface FollowUpFilters {
  search?: string;
  channel?: FollowUpChannel | "All";
  priority?: FollowUpPriority | "All";
  status?: FollowUpStatus | "All";
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
  leadName: string;
  owner: string;
  scheduledAt: string;
  channel: FollowUpChannel;
  priority: FollowUpPriority;
  notes: string;
}
