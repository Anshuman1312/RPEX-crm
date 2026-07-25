import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { buildFollowUpColumns } from "@/features/followups/components/followupColumns";
import { FollowUpCreateForm } from "@/features/followups/components/FollowUpCreateForm";
import { FollowUpFiltersBar } from "@/features/followups/components/FollowUpFiltersBar";
import { FollowUpStatsCards } from "@/features/followups/components/FollowUpStatsCards";
import { useFollowUpFilters } from "@/features/followups/hooks/useFollowUpFilters";
import {
  useCreateFollowUpMutation,
  useGetFollowUpsQuery,
  useUpdateFollowUpStatusMutation
} from "@/features/followups/services/followupApi";
import { FollowUpStatus } from "@/features/followups/types/followup";
import { CreateFollowUpFormValues } from "@/features/followups/validation/followupSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function FollowUpsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, channel, setChannel, priority, setPriority, status, setStatus } =
    useFollowUpFilters();
  const { data, isLoading, isError, refetch } = useGetFollowUpsQuery(filters);
  const [createFollowUp, { isLoading: isCreatingFollowUp }] = useCreateFollowUpMutation();
  const [updateFollowUpStatus] = useUpdateFollowUpStatusMutation();

  const columns = useMemo(
    () =>
      buildFollowUpColumns(async (followUpId: string, nextStatus: FollowUpStatus) => {
        try {
          await updateFollowUpStatus({ followUpId, status: nextStatus }).unwrap();
          toast.success("Follow-up status updated");
        } catch {
          toast.error("Unable to update follow-up status");
        }
      }),
    [updateFollowUpStatus]
  );

  const handleCreateFollowUp = async (values: CreateFollowUpFormValues) => {
    try {
      await createFollowUp(values).unwrap();
      toast.success("Follow-up created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create follow-up");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Follow-up
        </Button>
      }
      description="Follow-up tracking workspace with owner queues, channel mix, and closure visibility."
      title="Follow-ups"
    >
      {isLoading ? <LoadingState label="Loading follow-up workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load follow-ups. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Follow-up workspace unavailable"
        />
      ) : null}

      {data ? <FollowUpStatsCards stats={data.stats} /> : null}

      <FollowUpFiltersBar
        channel={channel}
        onChannelChange={setChannel}
        onPriorityChange={setPriority}
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        priority={priority}
        search={search}
        status={status}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Follow-up"
        size="lg"
      >
        <FollowUpCreateForm
          isSubmitting={isCreatingFollowUp}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateFollowUp}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Follow-up Queue" />
    </PageContainer>
  );
}
