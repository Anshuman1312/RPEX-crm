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
  const [viewingLead, setViewingLead] = useState<LeadRecord | null>(null);
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

  const handleViewClick = useCallback((lead: LeadRecord) => {
    setViewingLead(lead);
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
        handleDeleteClick,
        handleViewClick
      ),
    [updateLeadStatus, handleEditClick, handleDeleteClick, handleViewClick]
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
        description="Capture lead profile, ownership, and follow-up schedule."
        size="xl"
      >
        <LeadCreateForm
          isSubmitting={isCreatingLead}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateLead}
        />
      </Dialog>

      <Dialog
        isOpen={!!viewingLead}
        onClose={() => setViewingLead(null)}
        title="View Lead Details"
        description="Detailed lead profile details in read-only mode."
        size="xl"
      >
        {viewingLead ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Lead Name</span>
                <p className="mt-1 text-sm font-semibold">{viewingLead.fullName}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Email Address</span>
                <p className="mt-1 text-sm font-semibold">{viewingLead.email || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Phone Number</span>
                <p className="mt-1 text-sm font-semibold">{viewingLead.phone || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Assigned Owner ID</span>
                <p className="mt-1 text-sm font-semibold font-mono text-xs text-muted-foreground">{viewingLead.assignedToUserId || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Lead Source</span>
                <p className="mt-1 text-sm font-semibold">{viewingLead.source}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Priority Level</span>
                <p className="mt-1 text-sm font-semibold">{viewingLead.priority}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Lead Status</span>
                <p className="mt-1 text-sm font-semibold">{viewingLead.status}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Budget</span>
                <p className="mt-1 text-sm font-semibold text-primary">
                  {new Intl.NumberFormat("en-IN", {
                    style: "currency",
                    currency: "INR",
                    maximumFractionDigits: 0
                  }).format(viewingLead.budget)}
                </p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Next Follow-up Date</span>
                <p className="mt-1 text-sm font-semibold">{viewingLead.nextFollowupAt || "-"}</p>
              </div>
            </div>
            <div className="flex justify-end border-t pt-4">
              <Button onClick={() => setViewingLead(null)} variant="outline">
                Close
              </Button>
            </div>
          </div>
        ) : null}
      </Dialog>

      <Dialog
        isOpen={!!editingLead}
        onClose={() => setEditingLead(null)}
        title="Edit Lead"
        description="Capture lead profile, ownership, and follow-up schedule."
        size="xl"
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

