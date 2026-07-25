import {
  CalendarEventListResponse,
  CalendarEventRecord,
  CalendarStats,
  CreateCalendarEventInput
} from "@/features/calendar/types/calendar";

function formatDateTime(offsetDays: number, hour: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  date.setHours(hour, 0, 0, 0);
  return date.toISOString().slice(0, 16);
}

function formatDate(offsetDays: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

export const initialCalendarEvents: CalendarEventRecord[] = [
  {
    id: "EV-9101",
    title: "Client progress call",
    type: "Meeting",
    status: "Upcoming",
    owner: "Riya",
    attendee: "Ishita Rao",
    eventAt: formatDateTime(1, 11),
    location: "Google Meet",
    linkedModule: "Customers",
    updatedAt: formatDate(-1)
  },
  {
    id: "EV-9102",
    title: "Tower C unit walkthrough",
    type: "Site Visit",
    status: "Completed",
    owner: "Rohan",
    attendee: "Aarav Mehta",
    eventAt: formatDateTime(-1, 16),
    location: "Skyline Heights",
    linkedModule: "Inventory",
    updatedAt: formatDate(-1)
  },
  {
    id: "EV-9103",
    title: "Payment follow-up",
    type: "Follow-up",
    status: "Missed",
    owner: "Aman",
    attendee: "Kavya Sharma",
    eventAt: formatDateTime(-2, 10),
    location: "Phone",
    linkedModule: "Payments",
    updatedAt: formatDate(-2)
  },
  {
    id: "EV-9104",
    title: "Handover checklist deadline",
    type: "Deadline",
    status: "Upcoming",
    owner: "Priya",
    attendee: "Project Team",
    eventAt: formatDateTime(3, 18),
    location: "CRM",
    linkedModule: "Projects",
    updatedAt: formatDate(-1)
  }
];

export function buildCalendarStats(records: CalendarEventRecord[]): CalendarStats {
  return {
    total: records.length,
    upcoming: records.filter(record => record.status === "Upcoming").length,
    completed: records.filter(record => record.status === "Completed").length,
    missed: records.filter(record => record.status === "Missed").length
  };
}

export function buildCalendarEventListResponse(
  records: CalendarEventRecord[]
): CalendarEventListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildCalendarStats(records)
  };
}

export function createCalendarEventRecord(
  payload: CreateCalendarEventInput,
  index: number
): CalendarEventRecord {
  return {
    id: `EV-${9100 + index}`,
    title: payload.title,
    type: payload.type,
    status: "Upcoming",
    owner: payload.owner,
    attendee: payload.attendee,
    eventAt: payload.eventAt,
    location: payload.location,
    linkedModule: payload.linkedModule,
    updatedAt: new Date().toISOString().slice(0, 10)
  };
}
