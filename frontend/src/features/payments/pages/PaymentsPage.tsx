import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { PaymentCreateForm } from "@/features/payments/components/PaymentCreateForm";
import { PaymentFiltersBar } from "@/features/payments/components/PaymentFiltersBar";
import { PaymentStatsCards } from "@/features/payments/components/PaymentStatsCards";
import { buildPaymentColumns } from "@/features/payments/components/paymentColumns";
import { usePaymentFilters } from "@/features/payments/hooks/usePaymentFilters";
import {
  useCreatePaymentMutation,
  useGetPaymentsQuery,
  useUpdatePaymentStatusMutation
} from "@/features/payments/services/paymentApi";
import { PaymentStatus } from "@/features/payments/types/payment";
import { CreatePaymentFormValues } from "@/features/payments/validation/paymentSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function PaymentsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, method, setMethod, status, setStatus } = usePaymentFilters();
  const { data, isLoading, isError, refetch } = useGetPaymentsQuery(filters);
  const [createPayment, { isLoading: isCreatingPayment }] = useCreatePaymentMutation();
  const [updatePaymentStatus] = useUpdatePaymentStatusMutation();

  const columns = useMemo(
    () =>
      buildPaymentColumns(async (paymentId: string, nextStatus: PaymentStatus) => {
        try {
          await updatePaymentStatus({ paymentId, status: nextStatus }).unwrap();
          toast.success("Payment status updated");
        } catch {
          toast.error("Unable to update payment status");
        }
      }),
    [updatePaymentStatus]
  );

  const handleCreatePayment = async (values: CreatePaymentFormValues) => {
    try {
      await createPayment(values).unwrap();
      toast.success("Payment created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create payment");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Payment
        </Button>
      }
      description="Payment reconciliation workspace with transaction status controls and intake."
      title="Payments"
    >
      {isLoading ? <LoadingState label="Loading payment workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load payments. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Payment workspace unavailable"
        />
      ) : null}

      {data ? <PaymentStatsCards stats={data.stats} /> : null}

      <PaymentFiltersBar
        method={method}
        onMethodChange={setMethod}
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        search={search}
        status={status}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Payment"
        size="lg"
      >
        <PaymentCreateForm
          isSubmitting={isCreatingPayment}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreatePayment}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Payment Ledger" />
    </PageContainer>
  );
}
