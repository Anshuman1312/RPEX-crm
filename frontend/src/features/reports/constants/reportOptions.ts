import { ReportRange, ReportStatus, ReportType } from "@/features/reports/types/report";

export const reportTypeOptions: Array<ReportType | "All"> = [
  "All",
  "Sales",
  "Inventory",
  "Finance",
  "Operations"
];

export const reportStatusOptions: Array<ReportStatus | "All"> = [
  "All",
  "Draft",
  "Ready",
  "Exported",
  "Failed"
];

export const reportRangeOptions: ReportRange[] = [
  "This Week",
  "This Month",
  "This Quarter",
  "Custom"
];
