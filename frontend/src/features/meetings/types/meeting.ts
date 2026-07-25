export type MeetingType = "Client Call" | "Site Visit" | "Internal" | "Vendor";
export type MeetingStatus = "Scheduled" | "Completed" | "Cancelled" | "Rescheduled";

export interface MeetingRecord {
  id: string;
  title: string;
  type: MeetingType;
  status: MeetingStatus;
  host: string;
  attendee: string;
  scheduledAt: string;
  location: string;
  notes: string;
  updatedAt: string;
}

export interface MeetingFilters {
  search?: string;
  type?: MeetingType | "All";
  status?: MeetingStatus | "All";
}

export interface MeetingStats {
  total: number;
  scheduled: number;
  completed: number;
  cancelled: number;
}

export interface MeetingListResponse {
  items: MeetingRecord[];
  total: number;
  stats: MeetingStats;
}

export interface CreateMeetingInput {
  title: string;
  type: MeetingType;
  host: string;
  attendee: string;
  scheduledAt: string;
  location: string;
  notes: string;
}
