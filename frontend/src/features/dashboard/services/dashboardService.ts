import { dashboardOverviewMock } from "@/features/dashboard/constants/dashboardMockData";
import { DashboardOverviewData } from "@/features/dashboard/types/dashboard";

export async function getDashboardOverview(): Promise<DashboardOverviewData> {
  await new Promise(resolve => window.setTimeout(resolve, 180));
  return dashboardOverviewMock;
}
