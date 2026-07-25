export type CalendarEventType = "Meeting" | "Site Visit" | "Follow-up" | "Deadline";
export type CalendarEventStatus = "Upcoming" | "Completed" | "Missed" | "Cancelled";

export interface CalendarEventRecord {
  id: string;
  title: string;
  type: CalendarEventType;
  status: CalendarEventStatus;
  owner: string;
  attendee: string;
  eventAt: string;
  location: string;
  linkedModule: string;
  updatedAt: string;
}

export interface CalendarFilters {
  search?: string;
  type?: CalendarEventType | "All";
  status?: CalendarEventStatus | "All";
}

export interface CalendarStats {
  total: number;
  upcoming: number;
  completed: number;
  missed: number;
}

export interface CalendarEventListResponse {
  items: CalendarEventRecord[];
  total: number;
  stats: CalendarStats;
}

export interface CreateCalendarEventInput {
  title: string;
  type: CalendarEventType;
  owner: string;
  attendee: string;
  eventAt: string;
  location: string;
  linkedModule: string;
}
