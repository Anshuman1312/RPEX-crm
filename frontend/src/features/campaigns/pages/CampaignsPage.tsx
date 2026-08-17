import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { buildCampaignColumns } from "@/features/campaigns/components/campaignColumns";
import { CampaignCreateForm } from "@/features/campaigns/components/CampaignCreateForm";
import { CampaignFiltersBar } from "@/features/campaigns/components/CampaignFiltersBar";
import { CampaignStatsCards } from "@/features/campaigns/components/CampaignStatsCards";
import { useCampaignFilters } from "@/features/campaigns/hooks/useCampaignFilters";
import {
  useCreateCampaignMutation,
  useGetCampaignsQuery
} from "@/features/campaigns/services/campaignApi";
import { CreateCampaignFormValues } from "@/features/campaigns/validation/campaignSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function CampaignsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, type, setType, status, setStatus } = useCampaignFilters();
  const { data, isLoading, isError, refetch } = useGetCampaignsQuery(filters);
  const [createCampaign, { isLoading: isCreatingCampaign }] = useCreateCampaignMutation();

  const columns = useMemo(() => buildCampaignColumns(), []);

  const handleCreateCampaign = async (values: CreateCampaignFormValues) => {
    try {
      const payload = {
        name: values.name,
        type: values.type,
        platform: values.platform,
        budget: values.budget,
        start_date: values.start_date,
        end_date: values.end_date,
        extra_data: values.extra_data ? JSON.parse(values.extra_data) : {}
      };
      await createCampaign(payload).unwrap();
      toast.success("Campaign created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create campaign");
    }
  };

  return (
    <PageContainer
      actions={<Button onClick={() => setShowCreateForm(true)}>Create Campaign</Button>}
      description="Campaign execution workspace with channel controls, budgets, and lead conversion visibility."
      title="Campaigns"
    >
      {isLoading ? <LoadingState label="Loading campaigns workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load campaigns. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Campaign workspace unavailable"
        />
      ) : null}

      {data ? <CampaignStatsCards stats={data.stats} /> : null}

      <CampaignFiltersBar
        type={type}
        onTypeChange={setType}
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        search={search}
        status={status}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Campaign"
        size="lg"
      >
        <CampaignCreateForm
          isSubmitting={isCreatingCampaign}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateCampaign}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Campaign Pipeline" />
    </PageContainer>
  );
}
