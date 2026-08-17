import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { BookingCreateForm } from "@/features/bookings/components/BookingCreateForm";
import { BookingFiltersBar } from "@/features/bookings/components/BookingFiltersBar";
import { BookingStatsCards } from "@/features/bookings/components/BookingStatsCards";
import { buildBookingColumns } from "@/features/bookings/components/bookingColumns";
import { useBookingFilters } from "@/features/bookings/hooks/useBookingFilters";
import {
  useCreateBookingMutation,
  useGetBookingsQuery
} from "@/features/bookings/services/bookingApi";
import { BookingFilters } from "@/features/bookings/types/booking";
import { CreateBookingFormValues } from "@/features/bookings/validation/bookingSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function BookingsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const {
    filters,
    search,
    setSearch,
    financeRequired,
    setFinanceRequired,
    loanAssistanceRequired,
    setLoanAssistanceRequired
  } = useBookingFilters();
  const { data, isLoading, isFetching, isError, refetch } = useGetBookingsQuery(filters);
  const [createBooking, { isLoading: isCreatingBooking }] = useCreateBookingMutation();

  const columns = useMemo(
    () => buildBookingColumns(),
    []
  );

  const handleCreateBooking = async (values: CreateBookingFormValues) => {
    try {
      await createBooking(values).unwrap();
      toast.success("Booking created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create booking");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Booking
        </Button>
      }
      description="Booking lifecycle workspace with stage controls, payment visibility, and quick intake."
      title="Bookings"
    >
      {isLoading ? <LoadingState label="Loading booking workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load bookings. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Booking workspace unavailable"
        />
      ) : null}

      {data ? <BookingStatsCards stats={data.stats} /> : null}

      <BookingFiltersBar
        onFinanceRequiredChange={setFinanceRequired}
        onSearchChange={setSearch}
        onLoanAssistanceRequiredChange={setLoanAssistanceRequired}
        financeRequired={financeRequired}
        search={search}
        loanAssistanceRequired={loanAssistanceRequired}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Booking"
        size="lg"
      >
        <BookingCreateForm
          isSubmitting={isCreatingBooking}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateBooking}
        />
      </Dialog>

      <div className="text-[#38263f] dark:text-[#c4afd3]">
        <DataTable
          columns={columns}
          data={data?.items ?? []}
          title="Booking Pipeline"
          onRefresh={refetch}
          isRefreshing={isFetching}
        />
      </div>
    </PageContainer>
  );
}
