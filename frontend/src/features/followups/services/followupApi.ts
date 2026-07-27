import { rootApi } from "@/core/api/rootApi";
import {
  CreateFollowUpInput,
  FollowUpFilters,
  FollowUpListResponse,
  FollowUpRecord,
  FollowUpStatus
} from "@/features/followups/types/followup";
import {
  buildFollowUpListResponse,
  createFollowUpRecord,
  initialFollowUpRecords
} from "@/features/followups/services/followupMockData";

let inMemoryFollowUps: FollowUpRecord[] = [...initialFollowUpRecords];

function applyFilters(records: FollowUpRecord[], filters?: FollowUpFilters): FollowUpRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.leadName, record.owner, record.channel, record.status]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const channelMatch =
      !filters.channel || filters.channel === "All" || record.channel === filters.channel;
    const priorityMatch =
      !filters.priority || filters.priority === "All" || record.priority === filters.priority;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && channelMatch && priorityMatch && statusMatch;
  });
}

export const followUpApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getFollowUps: builder.query<FollowUpListResponse, FollowUpFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryFollowUps, filters);
        return { data: buildFollowUpListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Followups" as const, id: item.id })),
              { type: "Followups" as const, id: "LIST" }
            ]
          : [{ type: "Followups" as const, id: "LIST" }]
    }),

    createFollowUp: builder.mutation<FollowUpRecord, CreateFollowUpInput>({
      queryFn: async payload => {
        const nextRecord = createFollowUpRecord(payload, inMemoryFollowUps.length + 1);
        inMemoryFollowUps = [nextRecord, ...inMemoryFollowUps];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Followups", id: "LIST" }]
    }),

    updateFollowUpStatus: builder.mutation<
      FollowUpRecord,
      { followUpId: string; status: FollowUpStatus }
    >({
      queryFn: async ({ followUpId, status }) => {
        const record = inMemoryFollowUps.find(item => item.id === followUpId);

        if (!record) {
          return { error: { status: 404, data: { message: "Follow-up not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Followups", id: arg.followUpId },
        { type: "Followups", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetFollowUpsQuery,
  useCreateFollowUpMutation,
  useUpdateFollowUpStatusMutation
} = followUpApi;
