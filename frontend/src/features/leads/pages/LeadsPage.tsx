import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { LeadCreateForm } from "@/features/leads/components/LeadCreateForm";
import { LeadFiltersBar } from "@/features/leads/components/LeadFiltersBar";
import { LeadStatsCards } from "@/features/leads/components/LeadStatsCards";
import { buildLeadColumns } from "@/features/leads/components/leadColumns";
import { useLeadFilters } from "@/features/leads/hooks/useLeadFilters";
import { useConfirm } from "@/hooks/useConfirm";
import {
  useCreateLeadMutation,
  useDeleteLeadMutation,
  useGetLeadsQuery,
  useUpdateLeadMutation,
  useUpdateLeadStatusMutation
} from "@/features/leads/services/leadQueries";
import { LeadRecord, LeadStatus } from "@/features/leads/types/lead";
import { CreateLeadFormValues } from "@/features/leads/validation/leadSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function LeadsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingLead, setEditingLead] = useState<LeadRecord | null>(null);
  const { filters, search, setSearch, source, setSource, status, setStatus } = useLeadFilters();
  const { data, isLoading, isError, refetch } = useGetLeadsQuery(filters);
  
  const [createLead, { isLoading: isCreatingLead }] = useCreateLeadMutation();
  const [updateLead, { isLoading: isUpdatingLead }] = useUpdateLeadMutation();
  const [deleteLead] = useDeleteLeadMutation();
  const [updateLeadStatus] = useUpdateLeadStatusMutation();

  const [ConfirmDialog, confirm] = useConfirm(
    "Delete Lead",
    "Are you sure you want to delete this lead? This action cannot be undone."
  );

  const handleEditClick = useCallback((lead: LeadRecord) => {
    setEditingLead(lead);
  }, []);

  const handleDeleteClick = useCallback(async (leadId: string) => {
    const ok = await confirm();
    if (ok) {
      try {
        await deleteLead(leadId);
        toast.success("Lead deleted successfully");
      } catch {
        toast.error("Unable to delete lead");
      }
    }
  }, [confirm, deleteLead]);

  const columns = useMemo(
    () =>
      buildLeadColumns(
        async (leadId: string, nextStatus: LeadStatus) => {
          try {
            await updateLeadStatus({ leadId, status: nextStatus });
            toast.success("Lead status updated");
          } catch {
            toast.error("Unable to update lead status");
          }
        },
        handleEditClick,
        handleDeleteClick
      ),
    [updateLeadStatus, handleEditClick, handleDeleteClick]
  );

  const handleCreateLead = async (values: CreateLeadFormValues) => {
    try {
      await createLead(values);
      toast.success("Lead created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create lead");
    }
  };

  const handleUpdateLead = async (values: CreateLeadFormValues) => {
    if (!editingLead) return;
    try {
      await updateLead({ leadId: editingLead.id, payload: values });
      toast.success("Lead updated successfully");
      setEditingLead(null);
    } catch {
      toast.error("Unable to update lead");
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
      <LeadStatsCards stats={data?.stats ?? { total: 0, newLeads: 0, qualified: 0, won: 0 }} />

      <LeadFiltersBar
        onSearchChange={setSearch}
        onSourceChange={setSource}
        onStatusChange={setStatus}
        search={search}
        source={source}
        status={status}
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

      <Dialog
        isOpen={!!editingLead}
        onClose={() => setEditingLead(null)}
        title="Edit Lead"
        size="lg"
      >
        {editingLead ? (
          <LeadCreateForm
            isSubmitting={isUpdatingLead}
            onCancel={() => setEditingLead(null)}
            onSubmit={handleUpdateLead}
            initialValues={{
              fullName: editingLead.fullName,
              email: editingLead.email,
              phone: editingLead.phone,
              source: editingLead.source,
              priority: editingLead.priority,
              assignedToUserId: editingLead.assignedToUserId,
              budget: editingLead.budget,
              nextFollowupAt: editingLead.nextFollowupAt,
              status: editingLead.status,
            }}
          />
        ) : null}
      </Dialog>

      <ConfirmDialog />

      <DataTable columns={columns} data={data?.items ?? []} title="Lead Pipeline" />
    </PageContainer>
  );
}

