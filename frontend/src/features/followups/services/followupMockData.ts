import {
  CreateFollowUpInput,
  FollowUpListResponse,
  FollowUpRecord,
  FollowUpStats
} from "@/features/followups/types/followup";

function formatDate(offsetDays: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

function formatDateTime(offsetDays: number, hour: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  date.setHours(hour, 0, 0, 0);
  return date.toISOString().slice(0, 16);
}

export const initialFollowUpRecords: FollowUpRecord[] = [
  {
    id: "FU-7001",
    leadName: "Aarav Mehta",
    owner: "Riya",
    scheduledAt: formatDateTime(0, 11),
    channel: "Call",
    priority: "High",
    status: "Pending",
    notes: "Confirm site visit availability.",
    updatedAt: formatDate(-1)
  },
  {
    id: "FU-7002",
    leadName: "Kavya Sharma",
    owner: "Aman",
    scheduledAt: formatDateTime(-1, 16),
    channel: "WhatsApp",
    priority: "Medium",
    status: "Done",
    notes: "Shared payment plan brochure.",
    updatedAt: formatDate(-1)
  },
  {
    id: "FU-7003",
    leadName: "Neel Jain",
    owner: "Priya",
    scheduledAt: formatDateTime(-2, 10),
    channel: "Email",
    priority: "Low",
    status: "Missed",
    notes: "No response, retry next week.",
    updatedAt: formatDate(-2)
  },
  {
    id: "FU-7004",
    leadName: "Ishita Rao",
    owner: "Rohan",
    scheduledAt: formatDateTime(2, 15),
    channel: "Meeting",
    priority: "High",
    status: "Rescheduled",
    notes: "Shifted to align with legal documentation.",
    updatedAt: formatDate(0)
  }
];

export function buildFollowUpStats(records: FollowUpRecord[]): FollowUpStats {
  const today = new Date().toISOString().slice(0, 10);
  return {
    total: records.length,
    pending: records.filter(record => record.status === "Pending").length,
    dueToday: records.filter(record => record.scheduledAt.slice(0, 10) === today).length,
    done: records.filter(record => record.status === "Done").length
  };
}

export function buildFollowUpListResponse(records: FollowUpRecord[]): FollowUpListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildFollowUpStats(records)
  };
}

export function createFollowUpRecord(payload: CreateFollowUpInput, index: number): FollowUpRecord {
  return {
    id: `FU-${7000 + index}`,
    leadName: payload.leadName,
    owner: payload.owner,
    scheduledAt: payload.scheduledAt,
    channel: payload.channel,
    priority: payload.priority,
    status: "Pending",
    notes: payload.notes,
    updatedAt: new Date().toISOString().slice(0, 10)
  };
}
