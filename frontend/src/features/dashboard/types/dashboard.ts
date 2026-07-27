export type DashboardWidgetId =
  | "leadStats"
  | "revenueTrend"
  | "bookingPipeline"
  | "payments"
  | "tasks"
  | "meetings"
  | "recentActivity"
  | "quickActions";

export interface KpiMetric {
  id: string;
  label: string;
  value: string;
  change: string;
  positive?: boolean;
}

export interface TrendPoint {
  name: string;
  value: number;
}

export interface PaymentBreakdown {
  label: string;
  value: number;
}

export interface TaskSummary {
  label: string;
  count: number;
  tone: "info" | "warning" | "danger" | "success";
}

export interface MeetingSummary {
  title: string;
  when: string;
  owner: string;
}

export interface ActivityItem {
  id: string;
  text: string;
  timestamp: string;
}

export interface QuickActionItem {
  id: string;
  label: string;
  description: string;
}

export interface DashboardOverviewData {
  kpis: KpiMetric[];
  leadTrend: TrendPoint[];
  bookingPipeline: TrendPoint[];
  paymentBreakdown: PaymentBreakdown[];
  tasks: TaskSummary[];
  meetings: MeetingSummary[];
  recentActivity: ActivityItem[];
  quickActions: QuickActionItem[];
}
