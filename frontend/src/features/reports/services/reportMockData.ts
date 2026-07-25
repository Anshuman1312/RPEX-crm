import {
  CreateReportInput,
  ReportListResponse,
  ReportRecord,
  ReportStats
} from "@/features/reports/types/report";

function formatDateTime(offsetHours: number) {
  const date = new Date();
  date.setHours(date.getHours() + offsetHours);
  return date.toISOString().slice(0, 16);
}

export const initialReportRecords: ReportRecord[] = [
  {
    id: "RP-11101",
    title: "Monthly Sales Conversion",
    type: "Sales",
    status: "Ready",
    range: "This Month",
    owner: "Riya",
    generatedAt: formatDateTime(-3),
    rows: 148,
    updatedAt: formatDateTime(-2)
  },
  {
    id: "RP-11102",
    title: "Inventory Availability Snapshot",
    type: "Inventory",
    status: "Exported",
    range: "This Week",
    owner: "Aman",
    generatedAt: formatDateTime(-7),
    rows: 92,
    updatedAt: formatDateTime(-6)
  },
  {
    id: "RP-11103",
    title: "Quarterly Collection Summary",
    type: "Finance",
    status: "Draft",
    range: "This Quarter",
    owner: "Priya",
    generatedAt: formatDateTime(-1),
    rows: 0,
    updatedAt: formatDateTime(-1)
  },
  {
    id: "RP-11104",
    title: "Ops SLA Breach Report",
    type: "Operations",
    status: "Failed",
    range: "This Month",
    owner: "Rohan",
    generatedAt: formatDateTime(-5),
    rows: 0,
    updatedAt: formatDateTime(-5)
  }
];

export function buildReportStats(records: ReportRecord[]): ReportStats {
  return {
    total: records.length,
    ready: records.filter(record => record.status === "Ready").length,
    exported: records.filter(record => record.status === "Exported").length,
    failed: records.filter(record => record.status === "Failed").length
  };
}

export function buildReportListResponse(records: ReportRecord[]): ReportListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildReportStats(records)
  };
}

export function createReportRecord(payload: CreateReportInput, index: number): ReportRecord {
  const now = new Date().toISOString().slice(0, 16);

  return {
    id: `RP-${11100 + index}`,
    title: payload.title,
    type: payload.type,
    status: "Draft",
    range: payload.range,
    owner: payload.owner,
    generatedAt: now,
    rows: 0,
    updatedAt: now
  };
}
