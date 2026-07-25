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
  useGetCampaignsQuery,
  useUpdateCampaignStatusMutation
} from "@/features/campaigns/services/campaignApi";
import { CampaignStatus } from "@/features/campaigns/types/campaign";
import { CreateCampaignFormValues } from "@/features/campaigns/validation/campaignSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function CampaignsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, channel, setChannel, status, setStatus } = useCampaignFilters();
  const { data, isLoading, isError, refetch } = useGetCampaignsQuery(filters);
  const [createCampaign, { isLoading: isCreatingCampaign }] = useCreateCampaignMutation();
  const [updateCampaignStatus] = useUpdateCampaignStatusMutation();

  const columns = useMemo(
    () =>
      buildCampaignColumns(async (campaignId: string, nextStatus: CampaignStatus) => {
        try {
          await updateCampaignStatus({ campaignId, status: nextStatus }).unwrap();
          toast.success("Campaign status updated");
        } catch {
          toast.error("Unable to update campaign status");
        }
      }),
    [updateCampaignStatus]
  );

  const handleCreateCampaign = async (values: CreateCampaignFormValues) => {
    try {
      await createCampaign(values).unwrap();
      toast.success("Campaign created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create campaign");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Campaign
        </Button>
      }
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
        channel={channel}
        onChannelChange={setChannel}
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
