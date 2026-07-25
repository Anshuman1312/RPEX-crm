import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { ReportCreateForm } from "@/features/reports/components/ReportCreateForm";
import { ReportFiltersBar } from "@/features/reports/components/ReportFiltersBar";
import { ReportStatsCards } from "@/features/reports/components/ReportStatsCards";
import { buildReportColumns } from "@/features/reports/components/reportColumns";
import { useReportFilters } from "@/features/reports/hooks/useReportFilters";
import {
  useCreateReportMutation,
  useGetReportsQuery,
  useUpdateReportStatusMutation
} from "@/features/reports/services/reportApi";
import { ReportStatus } from "@/features/reports/types/report";
import { CreateReportFormValues } from "@/features/reports/validation/reportSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function ReportsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, type, setType, status, setStatus } = useReportFilters();
  const { data, isLoading, isError, refetch } = useGetReportsQuery(filters);
  const [createReport, { isLoading: isCreatingReport }] = useCreateReportMutation();
  const [updateReportStatus] = useUpdateReportStatusMutation();

  const columns = useMemo(
    () =>
      buildReportColumns(async (reportId: string, nextStatus: ReportStatus) => {
        try {
          await updateReportStatus({ reportId, status: nextStatus }).unwrap();
          toast.success("Report status updated");
        } catch {
          toast.error("Unable to update report status");
        }
      }),
    [updateReportStatus]
  );

  const handleCreateReport = async (values: CreateReportFormValues) => {
    try {
      await createReport(values).unwrap();
      toast.success("Report created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create report");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Report
        </Button>
      }
      description="Analytics workspace with report jobs, status tracking, and export readiness flow."
      title="Reports"
    >
      {isLoading ? <LoadingState label="Loading reports workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load reports. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Reports workspace unavailable"
        />
      ) : null}

      {data ? <ReportStatsCards stats={data.stats} /> : null}

      <ReportFiltersBar
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        onTypeChange={setType}
        search={search}
        status={status}
        type={type}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Report"
        size="lg"
      >
        <ReportCreateForm
          isSubmitting={isCreatingReport}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateReport}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Report Runs" />
    </PageContainer>
  );
}
