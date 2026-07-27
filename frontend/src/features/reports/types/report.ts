export type ReportType = "Sales" | "Inventory" | "Finance" | "Operations";
export type ReportStatus = "Draft" | "Ready" | "Exported" | "Failed";
export type ReportRange = "This Week" | "This Month" | "This Quarter" | "Custom";

export interface ReportRecord {
  id: string;
  title: string;
  type: ReportType;
  status: ReportStatus;
  range: ReportRange;
  owner: string;
  generatedAt: string;
  rows: number;
  updatedAt: string;
}

export interface ReportFilters {
  search?: string;
  type?: ReportType | "All";
  status?: ReportStatus | "All";
}

export interface ReportStats {
  total: number;
  ready: number;
  exported: number;
  failed: number;
}

export interface ReportListResponse {
  items: ReportRecord[];
  total: number;
  stats: ReportStats;
}

export interface CreateReportInput {
  title: string;
  type: ReportType;
  range: ReportRange;
  owner: string;
}
