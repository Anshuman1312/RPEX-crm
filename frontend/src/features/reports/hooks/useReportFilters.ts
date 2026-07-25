import { useMemo, useState } from "react";
import { ReportFilters, ReportStatus, ReportType } from "@/features/reports/types/report";

export function useReportFilters() {
  const [search, setSearch] = useState("");
  const [type, setType] = useState<ReportType | "All">("All");
  const [status, setStatus] = useState<ReportStatus | "All">("All");

  const filters = useMemo<ReportFilters>(
    () => ({
      search,
      type,
      status
    }),
    [search, status, type]
  );

  return {
    filters,
    search,
    type,
    status,
    setSearch,
    setType,
    setStatus
  };
}
