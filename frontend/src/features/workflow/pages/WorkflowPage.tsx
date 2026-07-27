import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { buildWorkflowColumns } from "@/features/workflow/components/workflowColumns";
import { WorkflowCreateForm } from "@/features/workflow/components/WorkflowCreateForm";
import { WorkflowFiltersBar } from "@/features/workflow/components/WorkflowFiltersBar";
import { WorkflowStatsCards } from "@/features/workflow/components/WorkflowStatsCards";
import { useWorkflowFilters } from "@/features/workflow/hooks/useWorkflowFilters";
import {
  useCreateWorkflowMutation,
  useGetWorkflowsQuery,
  useUpdateWorkflowStatusMutation
} from "@/features/workflow/services/workflowApi";
import { WorkflowStatus } from "@/features/workflow/types/workflow";
import { CreateWorkflowFormValues } from "@/features/workflow/validation/workflowSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function WorkflowPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, trigger, setTrigger, status, setStatus } = useWorkflowFilters();
  const { data, isLoading, isError, refetch } = useGetWorkflowsQuery(filters);
  const [createWorkflow, { isLoading: isCreating }] = useCreateWorkflowMutation();
  const [updateWorkflowStatus] = useUpdateWorkflowStatusMutation();

  const columns = useMemo(
    () =>
      buildWorkflowColumns(async (workflowId, nextStatus: WorkflowStatus) => {
        try {
          await updateWorkflowStatus({ workflowId, status: nextStatus }).unwrap();
          toast.success("Workflow status updated");
        } catch {
          toast.error("Unable to update workflow status");
        }
      }),
    [updateWorkflowStatus]
  );

  const handleCreate = async (values: CreateWorkflowFormValues) => {
    try {
      await createWorkflow(values).unwrap();
      toast.success("Workflow created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create workflow");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Workflow
        </Button>
      }
      description="Automation rules workspace with trigger-action definitions, run history, and status controls."
      title="Workflow"
    >
      {isLoading ? <LoadingState label="Loading workflow workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load workflows. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Workflow workspace unavailable"
        />
      ) : null}

      {data ? <WorkflowStatsCards stats={data.stats} /> : null}

      <WorkflowFiltersBar
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        onTriggerChange={setTrigger}
        search={search}
        status={status}
        trigger={trigger}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Workflow"
        size="lg"
      >
        <WorkflowCreateForm
          isSubmitting={isCreating}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreate}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Workflow Registry" />
    </PageContainer>
  );
}
