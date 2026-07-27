import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { buildCalendarColumns } from "@/features/calendar/components/calendarColumns";
import { CalendarEventCreateForm } from "@/features/calendar/components/CalendarEventCreateForm";
import { CalendarFiltersBar } from "@/features/calendar/components/CalendarFiltersBar";
import { CalendarStatsCards } from "@/features/calendar/components/CalendarStatsCards";
import { useCalendarFilters } from "@/features/calendar/hooks/useCalendarFilters";
import {
  useCreateCalendarEventMutation,
  useGetCalendarEventsQuery,
  useUpdateCalendarEventStatusMutation
} from "@/features/calendar/services/calendarApi";
import { CalendarEventStatus } from "@/features/calendar/types/calendar";
import { CreateCalendarEventFormValues } from "@/features/calendar/validation/calendarSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function CalendarPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, type, setType, status, setStatus } = useCalendarFilters();
  const { data, isLoading, isError, refetch } = useGetCalendarEventsQuery(filters);
  const [createCalendarEvent, { isLoading: isCreatingEvent }] = useCreateCalendarEventMutation();
  const [updateCalendarEventStatus] = useUpdateCalendarEventStatusMutation();

  const columns = useMemo(
    () =>
      buildCalendarColumns(async (eventId: string, nextStatus: CalendarEventStatus) => {
        try {
          await updateCalendarEventStatus({ eventId, status: nextStatus }).unwrap();
          toast.success("Calendar event status updated");
        } catch {
          toast.error("Unable to update calendar event status");
        }
      }),
    [updateCalendarEventStatus]
  );

  const handleCreateEvent = async (values: CreateCalendarEventFormValues) => {
    try {
      await createCalendarEvent(values).unwrap();
      toast.success("Calendar event created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create calendar event");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Event
        </Button>
      }
      description="Calendar workspace for scheduling, follow-ups, deadlines, and ownership visibility."
      title="Calendar"
    >
      {isLoading ? <LoadingState label="Loading calendar workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load calendar events. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Calendar workspace unavailable"
        />
      ) : null}

      {data ? <CalendarStatsCards stats={data.stats} /> : null}

      <CalendarFiltersBar
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
        title="Create Event"
        size="lg"
      >
        <CalendarEventCreateForm
          isSubmitting={isCreatingEvent}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateEvent}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Calendar Event Queue" />
    </PageContainer>
  );
}
