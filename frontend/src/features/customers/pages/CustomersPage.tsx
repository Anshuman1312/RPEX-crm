import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, LoadingState } from "@/components";
import { CustomerCreateForm } from "@/features/customers/components/CustomerCreateForm";
import { CustomerFiltersBar } from "@/features/customers/components/CustomerFiltersBar";
import { CustomerStatsCards } from "@/features/customers/components/CustomerStatsCards";
import { buildCustomerColumns } from "@/features/customers/components/customerColumns";
import { useCustomerFilters } from "@/features/customers/hooks/useCustomerFilters";
import {
  useCreateCustomerMutation,
  useGetCustomersQuery
} from "@/features/customers/services/customerApi";
import { CreateCustomerFormValues } from "@/features/customers/validation/customerSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function CustomersPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, status, customerType, setSearch, setStatus, setCustomerType } =
    useCustomerFilters();
  const { data, isLoading, isError, refetch } = useGetCustomersQuery(filters);
  const [createCustomer, { isLoading: isCreatingCustomer }] = useCreateCustomerMutation();

  const columns = useMemo(() => buildCustomerColumns(), []);

  const handleCreateCustomer = async (values: CreateCustomerFormValues) => {
    try {
      await createCustomer(values).unwrap();
      toast.success("Client details created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create client details");
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

      <DataTable columns={columns} data={data?.items ?? []} title="Client Requirements Register" />
    </PageContainer>
  );
}
