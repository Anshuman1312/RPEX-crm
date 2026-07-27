import {
  CreateMeetingInput,
  MeetingListResponse,
  MeetingRecord,
  MeetingStats
} from "@/features/meetings/types/meeting";

function formatDateTime(offsetDays: number, hour: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  date.setHours(hour, 30, 0, 0);
  return date.toISOString().slice(0, 16);
}

function formatDate(offset: number) {
  const date = new Date();
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

export const initialMeetingRecords: MeetingRecord[] = [
  {
    id: "MT-8101",
    title: "Payment milestone review",
    type: "Client Call",
    status: "Scheduled",
    host: "Riya",
    attendee: "Ishita Rao",
    scheduledAt: formatDateTime(1, 11),
    location: "Google Meet",
    notes: "Discuss tranche release timeline.",
    updatedAt: formatDate(-1)
  },
  {
    id: "MT-8102",
    title: "Tower B possession walkthrough",
    type: "Site Visit",
    status: "Completed",
    host: "Rohan",
    attendee: "Aarav Mehta",
    scheduledAt: formatDateTime(-1, 16),
    location: "Skyline Heights",
    notes: "Unit readiness confirmed.",
    updatedAt: formatDate(-1)
  },
  {
    id: "MT-8103",
    title: "Weekly execution sync",
    type: "Internal",
    status: "Rescheduled",
    host: "Priya",
    attendee: "Project Team",
    scheduledAt: formatDateTime(2, 10),
    location: "Conference Room 2",
    notes: "Moved due to vendor dependency update.",
    updatedAt: formatDate(-2)
  },
  {
    id: "MT-8104",
    title: "Marketing media alignment",
    type: "Vendor",
    status: "Cancelled",
    host: "Aman",
    attendee: "Creative Partner",
    scheduledAt: formatDateTime(0, 14),
    location: "Zoom",
    notes: "Cancelled after scope reprioritization.",
    updatedAt: formatDate(-3)
  }
];

export function buildMeetingStats(records: MeetingRecord[]): MeetingStats {
  return {
    total: records.length,
    scheduled: records.filter(record => record.status === "Scheduled").length,
    completed: records.filter(record => record.status === "Completed").length,
    cancelled: records.filter(record => record.status === "Cancelled").length
  };
}

export function buildMeetingListResponse(records: MeetingRecord[]): MeetingListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildMeetingStats(records)
  };
}

export function createMeetingRecord(payload: CreateMeetingInput, index: number): MeetingRecord {
  return {
    id: `MT-${8100 + index}`,
    title: payload.title,
    type: payload.type,
    status: "Scheduled",
    host: payload.host,
    attendee: payload.attendee,
    scheduledAt: payload.scheduledAt,
    location: payload.location,
    notes: payload.notes,
    updatedAt: new Date().toISOString().slice(0, 10)
  };
}
