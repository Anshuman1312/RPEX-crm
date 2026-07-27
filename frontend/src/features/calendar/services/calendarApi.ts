import { rootApi } from "@/core/api/rootApi";
import {
  CalendarEventListResponse,
  CalendarEventRecord,
  CalendarEventStatus,
  CalendarFilters,
  CreateCalendarEventInput
} from "@/features/calendar/types/calendar";
import {
  buildCalendarEventListResponse,
  createCalendarEventRecord,
  initialCalendarEvents
} from "@/features/calendar/services/calendarMockData";

let inMemoryCalendarEvents: CalendarEventRecord[] = [...initialCalendarEvents];

function applyFilters(records: CalendarEventRecord[], filters?: CalendarFilters): CalendarEventRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.title, record.owner, record.attendee, record.location, record.linkedModule]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const typeMatch = !filters.type || filters.type === "All" || record.type === filters.type;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && typeMatch && statusMatch;
  });
}

export const calendarApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getCalendarEvents: builder.query<CalendarEventListResponse, CalendarFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryCalendarEvents, filters);
        return { data: buildCalendarEventListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Calendar" as const, id: item.id })),
              { type: "Calendar" as const, id: "LIST" }
            ]
          : [{ type: "Calendar" as const, id: "LIST" }]
    }),

    createCalendarEvent: builder.mutation<CalendarEventRecord, CreateCalendarEventInput>({
      queryFn: async payload => {
        const nextRecord = createCalendarEventRecord(payload, inMemoryCalendarEvents.length + 1);
        inMemoryCalendarEvents = [nextRecord, ...inMemoryCalendarEvents];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Calendar", id: "LIST" }]
    }),

    updateCalendarEventStatus: builder.mutation<
      CalendarEventRecord,
      { eventId: string; status: CalendarEventStatus }
    >({
      queryFn: async ({ eventId, status }) => {
        const record = inMemoryCalendarEvents.find(item => item.id === eventId);

        if (!record) {
          return { error: { status: 404, data: { message: "Calendar event not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Calendar", id: arg.eventId },
        { type: "Calendar", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetCalendarEventsQuery,
  useCreateCalendarEventMutation,
  useUpdateCalendarEventStatusMutation
} = calendarApi;
