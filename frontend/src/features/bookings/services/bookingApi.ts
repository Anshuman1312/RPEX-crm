import { rootApi } from "@/core/api/rootApi";
import {
  BookingFilters,
  BookingListResponse,
  BookingRecord,
  CreateBookingInput
} from "@/features/bookings/types/booking";
import {
  buildBookingListResponse,
  createBookingRecord,
  initialBookingRecords
} from "@/features/bookings/services/bookingMockData";

let inMemoryBookings: BookingRecord[] = [...initialBookingRecords];

function applyFilters(records: BookingRecord[], filters?: BookingFilters): BookingRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter((record) => {
    const searchMatch =
      !search ||
      [record.id, record.bookingInterested, record.preferredPaymentMode]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const financeMatch =
      !filters.financeRequired ||
      filters.financeRequired === "All" ||
      (filters.financeRequired === "Yes" && record.financeRequired) ||
      (filters.financeRequired === "No" && !record.financeRequired);

    const loanMatch =
      !filters.loanAssistanceRequired ||
      filters.loanAssistanceRequired === "All" ||
      (filters.loanAssistanceRequired === "Yes" && record.loanAssistanceRequired) ||
      (filters.loanAssistanceRequired === "No" && !record.loanAssistanceRequired);

    return searchMatch && financeMatch && loanMatch;
  });
}

export const bookingApi = rootApi.injectEndpoints({
  endpoints: (builder) => ({
    getBookings: builder.query<BookingListResponse, BookingFilters | void>({
      queryFn: async (filters) => {
        const filtered = applyFilters(inMemoryBookings, filters || undefined);
        return { data: buildBookingListResponse(filtered) };
      },
      providesTags: (result) =>
        result
          ? [
              ...result.items.map((item) => ({ type: "Bookings" as const, id: item.id })),
              { type: "Bookings" as const, id: "LIST" }
            ]
          : [{ type: "Bookings" as const, id: "LIST" }]
    }),

    createBooking: builder.mutation<BookingRecord, CreateBookingInput>({
      queryFn: async (payload) => {
        const nextRecord = createBookingRecord(payload, inMemoryBookings.length + 1);
        inMemoryBookings = [nextRecord, ...inMemoryBookings];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Bookings", id: "LIST" }]
    })
  })
});

export const { useGetBookingsQuery, useCreateBookingMutation } = bookingApi;
