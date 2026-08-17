import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, LoadingState } from "@/components";
import { CustomerCreateForm } from "@/features/customers/components/CustomerCreateForm";
import { CustomerFiltersBar } from "@/features/customers/components/CustomerFiltersBar";
import { CustomerStatsCards } from "@/features/customers/components/CustomerStatsCards";
import { buildCustomerColumns } from "@/features/customers/components/customerColumns";
import { useCustomerFilters } from "@/features/customers/hooks/useCustomerFilters";
import { useConfirm } from "@/hooks/useConfirm";
import {
  useCreateCustomerMutation,
  useDeleteCustomerMutation,
  useGetCustomersQuery,
  useUpdateCustomerMutation
} from "@/features/customers/services/customerApi";
import { CustomerRecord } from "@/features/customers/types/customer";
import { CreateCustomerFormValues } from "@/features/customers/validation/customerSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function CustomersPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<CustomerRecord | null>(null);
  const [viewingCustomer, setViewingCustomer] = useState<CustomerRecord | null>(null);

  const { filters, search, status, customerType, setSearch, setStatus, setCustomerType } =
    useCustomerFilters();

  const { data, isLoading, isFetching, refetch } = useGetCustomersQuery(filters);
  const [createCustomer, { isLoading: isCreatingCustomer }] = useCreateCustomerMutation();
  const [updateCustomer, { isLoading: isUpdatingCustomer }] = useUpdateCustomerMutation();
  const [deleteCustomer] = useDeleteCustomerMutation();

  const [ConfirmDialog, confirm] = useConfirm(
    "Delete Customer",
    "Are you sure you want to delete this customer? This action cannot be undone."
  );

  const handleEditClick = useCallback((customer: CustomerRecord) => {
    setEditingCustomer(customer);
  }, []);

  const handleViewClick = useCallback((customer: CustomerRecord) => {
    setViewingCustomer(customer);
  }, []);

  const handleDeleteClick = useCallback(
    async (customerId: string) => {
      const ok = await confirm();
      if (ok) {
        try {
          await deleteCustomer(customerId).unwrap();
          toast.success("Customer deleted successfully");
        } catch {
          toast.error("Unable to delete customer");
        }
      }
    },
    [confirm, deleteCustomer]
  );

  const columns = useMemo(
    () => buildCustomerColumns(handleEditClick, handleDeleteClick, handleViewClick),
    [handleEditClick, handleDeleteClick, handleViewClick]
  );

  const handleCreateCustomer = async (values: CreateCustomerFormValues) => {
    try {
      await createCustomer(values).unwrap();
      toast.success("Client details created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create client details");
    }
  };

  const handleUpdateCustomer = async (values: CreateCustomerFormValues) => {
    if (!editingCustomer) return;
    try {
      await updateCustomer({ id: editingCustomer.id, payload: values }).unwrap();
      toast.success("Client details updated successfully");
      setEditingCustomer(null);
    } catch {
      toast.error("Unable to update client details");
    }
  };

  return (
    <PageContainer
      actions={<Button onClick={() => setShowCreateForm(true)}>Create Client</Button>}
      description="Track and manage prospective client requirements, budgets, and property preferences."
      title="Customer Details"
    >
      {isLoading ? <LoadingState label="Loading client workspace..." /> : null}
      <CustomerStatsCards
        stats={
          data?.stats ?? {
            by_status: {},
            by_type: {},
            total: 0
          }
        }
      />

      <CustomerFiltersBar
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        onCustomerTypeChange={setCustomerType}
        search={search}
        status={status}
        customerType={customerType}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Customer Details"
        description="Create customer profile and capture detailed property preferences."
        size="xl"
      >
        <CustomerCreateForm
          isSubmitting={isCreatingCustomer}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateCustomer}
        />
      </Dialog>

      <Dialog
        isOpen={!!viewingCustomer}
        onClose={() => setViewingCustomer(null)}
        title="View Client Details"
        description="Detailed client profile details in read-only mode."
        size="xl"
      >
        {viewingCustomer ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Client Name
                </span>
                <p className="mt-1 text-sm font-semibold">
                  {viewingCustomer.first_name} {viewingCustomer.last_name}
                </p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Customer ID
                </span>
                <p className="mt-1 text-sm font-semibold">{viewingCustomer.customer_number}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Email Address
                </span>
                <p className="mt-1 text-sm font-semibold">{viewingCustomer.email || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Mobile Number
                </span>
                <p className="mt-1 text-sm font-semibold">{viewingCustomer.phone || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Alternate Mobile
                </span>
                <p className="mt-1 text-sm font-semibold">
                  {viewingCustomer.alternate_phone || "-"}
                </p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Customer Type
                </span>
                <p className="mt-1 text-sm font-semibold capitalize">
                  {viewingCustomer.customer_type.toLowerCase()}
                </p>
              </div>
              {viewingCustomer.company_name && (
                <div>
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Company Name
                  </span>
                  <p className="mt-1 text-sm font-semibold">{viewingCustomer.company_name}</p>
                </div>
              )}
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Preferred Contact Method
                </span>
                <p className="mt-1 text-sm font-semibold capitalize">
                  {viewingCustomer.preferred_contact_method
                    ? viewingCustomer.preferred_contact_method.toLowerCase()
                    : "-"}
                </p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Preferred Language
                </span>
                <p className="mt-1 text-sm font-semibold uppercase">
                  {viewingCustomer.preferred_language || "EN"}
                </p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  GSTIN
                </span>
                <p className="mt-1 text-sm font-semibold">{viewingCustomer.gstin || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  PAN
                </span>
                <p className="mt-1 text-sm font-semibold">{viewingCustomer.pan || "-"}</p>
              </div>
              <div>
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Status
                </span>
                <p className="mt-1 text-sm font-semibold capitalize">
                  {viewingCustomer.status.toLowerCase()}
                </p>
              </div>
              <div className="col-span-full">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Notes
                </span>
                <p className="mt-1 text-sm bg-muted/20 p-2 rounded border whitespace-pre-wrap">
                  {viewingCustomer.notes || "-"}
                </p>
              </div>
            </div>
            <div className="flex justify-end border-t pt-4">
              <Button onClick={() => setViewingCustomer(null)} variant="outline">
                Close
              </Button>
            </div>
          </div>
        ) : null}
      </Dialog>

      <Dialog
        isOpen={!!editingCustomer}
        onClose={() => setEditingCustomer(null)}
        title="Edit Client Details"
        description="Update client profile and captured property preferences."
        size="xl"
      >
        {editingCustomer ? (
          <CustomerCreateForm
            isSubmitting={isUpdatingCustomer}
            onCancel={() => setEditingCustomer(null)}
            onSubmit={handleUpdateCustomer}
            initialValues={{
              first_name: editingCustomer.first_name,
              last_name: editingCustomer.last_name,
              email: editingCustomer.email,
              phone: editingCustomer.phone,
              alternate_phone: editingCustomer.alternate_phone || "",
              company_name: editingCustomer.company_name || "",
              customer_type: (editingCustomer.customer_type?.toLowerCase() as any) || "individual",
              referred_by_user_id: editingCustomer.referred_by_user_id || "",
              lead_converted_from_id: editingCustomer.lead_converted_from_id || "",
              preferred_contact_method:
                (editingCustomer.preferred_contact_method?.toLowerCase() as any) || "",
              preferred_language: editingCustomer.preferred_language || "en",
              gstin: editingCustomer.gstin || "",
              pan: editingCustomer.pan || "",
              notes: editingCustomer.notes || ""
            }}
            submitLabel="Update Client"
          />
        ) : null}
      </Dialog>

      <ConfirmDialog />

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        title="Client Requirements Register"
        onRefresh={refetch}
        isRefreshing={isFetching}
      />
    </PageContainer>
  );
}
