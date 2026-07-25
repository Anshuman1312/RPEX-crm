import { rootApi } from "@/core/api/rootApi";
import {
  CreateMeetingInput,
  MeetingFilters,
  MeetingListResponse,
  MeetingRecord,
  MeetingStatus
} from "@/features/meetings/types/meeting";
import {
  buildMeetingListResponse,
  createMeetingRecord,
  initialMeetingRecords
} from "@/features/meetings/services/meetingMockData";

let inMemoryMeetings: MeetingRecord[] = [...initialMeetingRecords];

function applyFilters(records: MeetingRecord[], filters?: MeetingFilters): MeetingRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.title, record.host, record.attendee, record.location]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const typeMatch = !filters.type || filters.type === "All" || record.type === filters.type;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && typeMatch && statusMatch;
  });
}

export const meetingApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getMeetings: builder.query<MeetingListResponse, MeetingFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryMeetings, filters);
        return { data: buildMeetingListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Meetings" as const, id: item.id })),
              { type: "Meetings" as const, id: "LIST" }
            ]
          : [{ type: "Meetings" as const, id: "LIST" }]
    }),

    createMeeting: builder.mutation<MeetingRecord, CreateMeetingInput>({
      queryFn: async payload => {
        const nextRecord = createMeetingRecord(payload, inMemoryMeetings.length + 1);
        inMemoryMeetings = [nextRecord, ...inMemoryMeetings];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Meetings", id: "LIST" }]
    }),

    updateMeetingStatus: builder.mutation<
      MeetingRecord,
      { meetingId: string; status: MeetingStatus }
    >({
      queryFn: async ({ meetingId, status }) => {
        const record = inMemoryMeetings.find(item => item.id === meetingId);

        if (!record) {
          return { error: { status: 404, data: { message: "Meeting not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Meetings", id: arg.meetingId },
        { type: "Meetings", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetMeetingsQuery,
  useCreateMeetingMutation,
  useUpdateMeetingStatusMutation
} = meetingApi;
