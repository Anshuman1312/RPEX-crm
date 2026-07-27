import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { NotificationCreateForm } from "@/features/notifications/components/NotificationCreateForm";
import { NotificationFiltersBar } from "@/features/notifications/components/NotificationFiltersBar";
import { NotificationStatsCards } from "@/features/notifications/components/NotificationStatsCards";
import { buildNotificationColumns } from "@/features/notifications/components/notificationColumns";
import { useNotificationFilters } from "@/features/notifications/hooks/useNotificationFilters";
import {
  useCreateNotificationMutation,
  useGetNotificationsQuery,
  useUpdateNotificationStatusMutation
} from "@/features/notifications/services/notificationApi";
import { NotificationStatus } from "@/features/notifications/types/notification";
import { CreateNotificationFormValues } from "@/features/notifications/validation/notificationSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function NotificationsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, type, setType, status, setStatus } = useNotificationFilters();
  const { data, isLoading, isError, refetch } = useGetNotificationsQuery(filters);
  const [createNotification, { isLoading: isCreatingNotification }] = useCreateNotificationMutation();
  const [updateNotificationStatus] = useUpdateNotificationStatusMutation();

  const columns = useMemo(
    () =>
      buildNotificationColumns(async (notificationId: string, nextStatus: NotificationStatus) => {
        try {
          await updateNotificationStatus({ notificationId, status: nextStatus }).unwrap();
          toast.success("Notification status updated");
        } catch {
          toast.error("Unable to update notification status");
        }
      }),
    [updateNotificationStatus]
  );

  const handleCreateNotification = async (values: CreateNotificationFormValues) => {
    try {
      await createNotification(values).unwrap();
      toast.success("Notification created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create notification");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Notification
        </Button>
      }
      description="Notification center with filtering, triage status, and announcement creation workflow."
      title="Notifications"
    >
      {isLoading ? <LoadingState label="Loading notifications workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load notifications. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Notifications workspace unavailable"
        />
      ) : null}

      {data ? <NotificationStatsCards stats={data.stats} /> : null}

      <NotificationFiltersBar
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
        title="Create Notification"
        size="lg"
      >
        <NotificationCreateForm
          isSubmitting={isCreatingNotification}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateNotification}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Notification Feed" />
    </PageContainer>
  );
}
