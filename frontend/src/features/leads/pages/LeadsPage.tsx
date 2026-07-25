import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { LeadCreateForm } from "@/features/leads/components/LeadCreateForm";
import { LeadFiltersBar } from "@/features/leads/components/LeadFiltersBar";
import { LeadStatsCards } from "@/features/leads/components/LeadStatsCards";
import { buildLeadColumns } from "@/features/leads/components/leadColumns";
import { useLeadFilters } from "@/features/leads/hooks/useLeadFilters";
import {
  useCreateLeadMutation,
  useGetLeadsQuery,
  useUpdateLeadStageMutation
} from "@/features/leads/services/leadApi";
import { LeadStage } from "@/features/leads/types/lead";
import { CreateLeadFormValues } from "@/features/leads/validation/leadSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function LeadsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, source, setSource, stage, setStage } = useLeadFilters();
  const { data, isLoading, isError, refetch } = useGetLeadsQuery(filters);
  const [createLead, { isLoading: isCreatingLead }] = useCreateLeadMutation();
  const [updateLeadStage] = useUpdateLeadStageMutation();

  const columns = useMemo(
    () =>
      buildLeadColumns(async (leadId: string, nextStage: LeadStage) => {
        try {
          await updateLeadStage({ leadId, stage: nextStage }).unwrap();
          toast.success("Lead stage updated");
        } catch {
          toast.error("Unable to update lead stage");
        }
      }),
    [updateLeadStage]
  );

  const handleCreateLead = async (values: CreateLeadFormValues) => {
    try {
      await createLead(values).unwrap();
      toast.success("Lead created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create lead");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Lead
        </Button>
      }
      description="Lead management with search, filters, stage workflow, and quick lead creation."
      title="Leads"
    >
      {isLoading ? <LoadingState label="Loading lead pipeline..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load leads. Retry to refresh the pipeline."
          onRetry={() => refetch()}
          title="Lead pipeline unavailable"
        />
      ) : null}

      {data ? <LeadStatsCards stats={data.stats} /> : null}

      <LeadFiltersBar
        onSearchChange={setSearch}
        onSourceChange={setSource}
        onStageChange={setStage}
        search={search}
        source={source}
        stage={stage}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Lead"
        size="lg"
      >
        <LeadCreateForm
          isSubmitting={isCreatingLead}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateLead}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Lead Pipeline" />
    </PageContainer>
  );
}
