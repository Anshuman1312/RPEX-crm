import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { buildFollowUpColumns } from "@/features/followups/components/followupColumns";
import { FollowUpCreateForm } from "@/features/followups/components/FollowUpCreateForm";
import { FollowUpFiltersBar } from "@/features/followups/components/FollowUpFiltersBar";
import { FollowUpStatsCards } from "@/features/followups/components/FollowUpStatsCards";
import { useFollowUpFilters } from "@/features/followups/hooks/useFollowUpFilters";
import { useConfirm } from "@/hooks/useConfirm";
import {
  useCreateFollowUpMutation,
  useDeleteFollowUpMutation,
  useGetFollowUpsQuery,
  useUpdateFollowUpMutation,
  useUpdateFollowUpStatusMutation
} from "@/features/followups/services/followupApi";
import { FollowUpRecord, FollowUpStatus } from "@/features/followups/types/followup";
import { CreateFollowUpFormValues } from "@/features/followups/validation/followupSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function FollowUpsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingFollowUp, setEditingFollowUp] = useState<FollowUpRecord | null>(null);
  const [viewingFollowUp, setViewingFollowUp] = useState<FollowUpRecord | null>(null);

  const { filters, search, setSearch, type, setType, priority, setPriority, status, setStatus } =
    useFollowUpFilters();

  const { data, isLoading, isFetching, isError, refetch } = useGetFollowUpsQuery(filters);

  const [createFollowUp, { isLoading: isCreatingFollowUp }] = useCreateFollowUpMutation();
  const [updateFollowUp, { isLoading: isUpdatingFollowUp }] = useUpdateFollowUpMutation();
  const [deleteFollowUp] = useDeleteFollowUpMutation();
  const [updateFollowUpStatus] = useUpdateFollowUpStatusMutation();

  const [ConfirmDialog, confirm] = useConfirm(
    "Delete Follow-up",
    "Are you sure you want to delete this follow-up? This action cannot be undone."
  );

  const handleEditClick = useCallback((followup: FollowUpRecord) => {
    setEditingFollowUp(followup);
  }, []);

  const handleViewClick = useCallback((followup: FollowUpRecord) => {
    setViewingFollowUp(followup);
  }, []);

  const handleDeleteClick = useCallback(async (followUpId: string) => {
    const ok = await confirm();
    if (ok) {
      try {
        await deleteFollowUp(followUpId).unwrap();
        toast.success("Follow-up deleted successfully");
      } catch {
        toast.error("Unable to delete follow-up");
      }
    }
  }, [confirm, deleteFollowUp]);

  const columns = useMemo(
    () =>
      buildFollowUpColumns(
        async (followUpId: string, nextStatus: FollowUpStatus) => {
          try {
            await updateFollowUpStatus({ followUpId, status: nextStatus }).unwrap();
            toast.success("Follow-up status updated");
          } catch {
            toast.error("Unable to update follow-up status");
          }
        },
        handleEditClick,
        handleDeleteClick,
        handleViewClick
      ),
    [updateFollowUpStatus, handleEditClick, handleDeleteClick, handleViewClick]
  );

  const handleCreateFollowUp = async (values: CreateFollowUpFormValues) => {
    try {
      const payload = {
        type: values.type,
        subject: values.subject,
        description: values.description || undefined,
        scheduled_at: new Date(values.scheduled_at).toISOString(),
        assigned_to_user_id: values.assigned_to_user_id || undefined,
        lead_id: values.lead_id || undefined,
        customer_id: values.customer_id || undefined,
        priority: Number(values.priority),
        is_critical: values.is_critical,
        notes: values.notes || undefined,
        tasks: values.tasks || []
      };
      await createFollowUp(payload).unwrap();
      toast.success("Follow-up created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create follow-up");
    }
  };

  const handleUpdateFollowUp = async (values: CreateFollowUpFormValues) => {
    if (!editingFollowUp) return;
    try {
      const payload = {
        type: values.type,
        subject: values.subject,
        description: values.description || undefined,
        scheduled_at: new Date(values.scheduled_at).toISOString(),
        assigned_to_user_id: values.assigned_to_user_id || undefined,
        lead_id: values.lead_id || undefined,
        customer_id: values.customer_id || undefined,
        priority: Number(values.priority),
        is_critical: values.is_critical,
        notes: values.notes || undefined
      };
      await updateFollowUp({ followUpId: editingFollowUp.id, payload }).unwrap();
      toast.success("Follow-up updated successfully");
      setEditingFollowUp(null);
    } catch {
      toast.error("Unable to update follow-up");
    }
  };

  return (
    <PageContainer
      actions={<Button onClick={() => setShowCreateForm(true)}>Create Follow-up</Button>}
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
        type={type}
        onTypeChange={setType}
        priority={priority}
        onPriorityChange={setPriority}
        onSearchChange={setSearch}
        status={status}
        onStatusChange={setStatus}
        search={search}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Follow-up"
        description="Track and schedule lead follow-ups with channel, priority, and ownership controls."
        size="xl"
      >
        <FollowUpCreateForm
          isSubmitting={isCreatingFollowUp}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateFollowUp}
        />
      </Dialog>

      <Dialog
        isOpen={!!editingFollowUp}
        onClose={() => setEditingFollowUp(null)}
        title="Edit Follow-up"
        description="Modify scheduled follow-up details, priorities, and dates."
        size="xl"
      >
        {editingFollowUp ? (
          <FollowUpCreateForm
            isSubmitting={isUpdatingFollowUp}
            onCancel={() => setEditingFollowUp(null)}
            onSubmit={handleUpdateFollowUp}
            initialValues={{
              type: editingFollowUp.type,
              subject: editingFollowUp.subject,
              description: editingFollowUp.description || "",
              scheduled_at: editingFollowUp.scheduled_at ? editingFollowUp.scheduled_at.slice(0, 16) : "",
              assigned_to_user_id: editingFollowUp.assigned_to_user_id || "",
              lead_id: editingFollowUp.lead_id || "",
              customer_id: editingFollowUp.customer_id || "",
              priority: editingFollowUp.priority,
              is_critical: editingFollowUp.is_critical,
              notes: editingFollowUp.notes || ""
            }}
          />
        ) : null}
      </Dialog>

      <Dialog
        isOpen={!!viewingFollowUp}
        onClose={() => setViewingFollowUp(null)}
        title="View Follow-up Details"
        description="Detailed follow-up parameters and references in read-only mode."
        size="xl"
      >
        {viewingFollowUp ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">FollowUp Id</span>
                <p className="mt-1 text-sm font-semibold font-mono">{viewingFollowUp.followup_number}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Subject</span>
                <p className="mt-1 text-sm font-semibold">{viewingFollowUp.subject}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Type</span>
                <p className="mt-1 text-sm font-semibold capitalize">{viewingFollowUp.type}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Scheduled At</span>
                <p className="mt-1 text-sm font-semibold">
                  {viewingFollowUp.scheduled_at ? viewingFollowUp.scheduled_at.replace("T", " ").slice(0, 16) : "-"}
                </p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Priority Level</span>
                <p className="mt-1 text-sm font-semibold">
                  {viewingFollowUp.priority === 0 ? "Low" : viewingFollowUp.priority === 1 ? "Medium" : "High"}
                </p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Critical</span>
                <p className="mt-1 text-sm font-semibold">{viewingFollowUp.is_critical ? "Yes" : "No"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Status</span>
                <p className="mt-1 text-sm font-semibold capitalize">{viewingFollowUp.status}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Lead ID Reference</span>
                <p className="mt-1 text-sm font-semibold font-mono text-xs text-muted-foreground">{viewingFollowUp.lead_id || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Customer ID Reference</span>
                <p className="mt-1 text-sm font-semibold font-mono text-xs text-muted-foreground">{viewingFollowUp.customer_id || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Owner ID</span>
                <p className="mt-1 text-sm font-semibold font-mono text-xs text-muted-foreground">{viewingFollowUp.assigned_to_user_id || "-"}</p>
              </div>
              <div className="col-span-full">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Description</span>
                <p className="mt-1 text-sm bg-muted/20 p-2 rounded border">{viewingFollowUp.description || "-"}</p>
              </div>
              <div className="col-span-full">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Follow-up Notes</span>
                <p className="mt-1 text-sm bg-muted/20 p-2 rounded border whitespace-pre-wrap">{viewingFollowUp.notes || "-"}</p>
              </div>
            </div>
            <div className="flex justify-end border-t pt-4">
              <Button onClick={() => setViewingFollowUp(null)} variant="outline">
                Close
              </Button>
            </div>
          </div>
        ) : null}
      </Dialog>

      <ConfirmDialog />

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        title="Follow-up Queue"
        onRefresh={refetch}
        isRefreshing={isFetching}
      />
    </PageContainer>
  );
}
