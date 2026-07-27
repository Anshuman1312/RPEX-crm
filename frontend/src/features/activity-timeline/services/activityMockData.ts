import {
  ActivityAction,
  ActivityListResponse,
  ActivityModule,
  ActivityRecord,
  ActivityStats
} from "@/features/activity-timeline/types/activity";

let idSeq = 1;

function makeActivity(
  actor: string,
  module: ActivityModule,
  action: ActivityAction,
  subject: string,
  detail: string,
  minutesAgo: number
): ActivityRecord {
  const date = new Date();
  date.setMinutes(date.getMinutes() - minutesAgo);
  return {
    id: `ACT-${String(idSeq++).padStart(5, "0")}`,
    actor,
    module,
    action,
    subject,
    detail,
    occurredAt: date.toISOString().slice(0, 16)
  };
}

export const initialActivityRecords: ActivityRecord[] = [
  makeActivity("Riya", "Bookings", "stage_changed", "BK-5102", "Stage moved to Payment Pending", 5),
  makeActivity("Aman", "Inventory", "status_changed", "IU-4102", "Status changed to Reserved", 18),
  makeActivity("Priya", "Payments", "created", "PY-6103", "New payment record created", 34),
  makeActivity("Rohan", "Leads", "updated", "LD-1003", "Lead details updated by manager", 55),
  makeActivity("Riya", "Customers", "assigned", "CU-2001", "Account manager reassigned to Rohan", 80),
  makeActivity("Admin", "Roles", "created", "ROLE-005", "New role Finance Analyst II created", 110),
  makeActivity("Aman", "Tasks", "status_changed", "TK-7103", "Task marked as Completed", 140),
  makeActivity("Priya", "Reports", "exported", "RP-11101", "Monthly Sales Conversion report exported", 200),
  makeActivity("Rohan", "Employees", "created", "EM-12105", "New employee onboarded", 260),
  makeActivity("Admin", "Settings", "updated", "Theme", "Theme mode changed to dark", 320),
  makeActivity("Riya", "Meetings", "status_changed", "MT-8103", "Meeting rescheduled to next week", 400),
  makeActivity("Admin", "Roles", "deleted", "ROLE-004", "Legacy Viewer role deactivated", 500)
];

function isToday(dateStr: string): boolean {
  return dateStr.slice(0, 10) === new Date().toISOString().slice(0, 10);
}

export function buildActivityStats(records: ActivityRecord[]): ActivityStats {
  return {
    total: records.length,
    today: records.filter(r => isToday(r.occurredAt)).length,
    uniqueActors: new Set(records.map(r => r.actor)).size,
    modules: new Set(records.map(r => r.module)).size
  };
}

export function buildActivityListResponse(records: ActivityRecord[]): ActivityListResponse {
  return { items: records, total: records.length, stats: buildActivityStats(records) };
}
