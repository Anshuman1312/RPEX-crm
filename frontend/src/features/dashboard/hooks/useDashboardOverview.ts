import { useEffect, useState } from "react";
import { getDashboardOverview } from "@/features/dashboard/services/dashboardService";
import { DashboardOverviewData } from "@/features/dashboard/types/dashboard";

interface UseDashboardOverviewResult {
  data: DashboardOverviewData | null;
  isLoading: boolean;
  isError: boolean;
  refetch: () => Promise<void>;
}

export function useDashboardOverview(): UseDashboardOverviewResult {
  const [data, setData] = useState<DashboardOverviewData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  const fetchData = async () => {
    setIsLoading(true);
    setIsError(false);

    try {
      const result = await getDashboardOverview();
      setData(result);
    } catch {
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void fetchData();
  }, []);

  return {
    data,
    isLoading,
    isError,
    refetch: fetchData
  };
}
