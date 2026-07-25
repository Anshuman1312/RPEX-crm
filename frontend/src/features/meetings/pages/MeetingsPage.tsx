import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { MeetingCreateForm } from "@/features/meetings/components/MeetingCreateForm";
import { MeetingFiltersBar } from "@/features/meetings/components/MeetingFiltersBar";
import { MeetingStatsCards } from "@/features/meetings/components/MeetingStatsCards";
import { buildMeetingColumns } from "@/features/meetings/components/meetingColumns";
import { useMeetingFilters } from "@/features/meetings/hooks/useMeetingFilters";
import {
  useCreateMeetingMutation,
  useGetMeetingsQuery,
  useUpdateMeetingStatusMutation
} from "@/features/meetings/services/meetingApi";
import { MeetingStatus } from "@/features/meetings/types/meeting";
import { CreateMeetingFormValues } from "@/features/meetings/validation/meetingSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function MeetingsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, type, setType, status, setStatus } = useMeetingFilters();
  const { data, isLoading, isError, refetch } = useGetMeetingsQuery(filters);
  const [createMeeting, { isLoading: isCreatingMeeting }] = useCreateMeetingMutation();
  const [updateMeetingStatus] = useUpdateMeetingStatusMutation();

  const columns = useMemo(
    () =>
      buildMeetingColumns(async (meetingId: string, nextStatus: MeetingStatus) => {
        try {
          await updateMeetingStatus({ meetingId, status: nextStatus }).unwrap();
          toast.success("Meeting status updated");
        } catch {
          toast.error("Unable to update meeting status");
        }
      }),
    [updateMeetingStatus]
  );

  const handleCreateMeeting = async (values: CreateMeetingFormValues) => {
    try {
      await createMeeting(values).unwrap();
      toast.success("Meeting created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create meeting");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Meeting
        </Button>
      }
      description="Meeting coordination workspace with schedule controls, visibility, and follow-up context."
      title="Meetings"
    >
      {isLoading ? <LoadingState label="Loading meetings workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load meetings. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Meetings workspace unavailable"
        />
      ) : null}

      {data ? <MeetingStatsCards stats={data.stats} /> : null}

      <MeetingFiltersBar
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
        title="Create Meeting"
        size="lg"
      >
        <MeetingCreateForm
          isSubmitting={isCreatingMeeting}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateMeeting}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Meeting Calendar Queue" />
    </PageContainer>
  );
}
