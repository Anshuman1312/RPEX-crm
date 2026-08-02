import { rootApi } from "@/core/api/rootApi";
import {
  CreateFollowUpInput,
  FollowUpFilters,
  FollowUpListResponse,
  FollowUpRecord,
  FollowUpStatus
} from "@/features/followups/types/followup";

export const followupApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getFollowUps: builder.query<FollowUpListResponse, FollowUpFilters | void>({
      queryFn: async (filters, api, extraOptions, baseQuery) => {
        const params: Record<string, any> = {};
        if (filters) {
          if (filters.search) params.search = filters.search;
          if (filters.lead_id) params.lead_id = filters.lead_id;
          if (filters.customer_id) params.customer_id = filters.customer_id;
          if (filters.assigned_to_user_id) params.assigned_to_user_id = filters.assigned_to_user_id;
          if (filters.is_critical !== undefined) params.is_critical = filters.is_critical;
          
          if (filters.priority !== undefined && filters.priority !== "All") {
            if (filters.priority === "Low") params.priority = 0;
            if (filters.priority === "Medium") params.priority = 1;
            if (filters.priority === "High") params.priority = 2;
          }
          if (filters.status && filters.status !== "All") {
            params.statuses = filters.status;
          }
          if (filters.type && filters.type !== "All") {
            params.types = filters.type;
          }
        }

        const listResult = await baseQuery({
          url: "/followups",
          method: "GET",
          params
        });

        if (listResult.error) {
          return { error: listResult.error as any };
        }

        const listEnvelope = listResult.data as any;
        const rawItems = listEnvelope?.data || [];
        const total = listEnvelope?.pagination?.total ?? rawItems.length;

        const items: FollowUpRecord[] = rawItems.map((item: any) => ({
          id: item.id,
          followup_number: item.followup_number,
          type: item.type,
          subject: item.subject,
          scheduled_at: item.scheduled_at,
          status: item.status,
          priority: item.priority,
          is_critical: item.is_critical,
          lead_id: item.lead_id,
          customer_id: item.customer_id,
          assigned_to_user_id: item.assigned_to_user_id,
          task_count: item.task_count || 0,
          created_at: item.created_at,
          updated_at: item.updated_at
        }));

        const todayStr = new Date().toISOString().slice(0, 10);
        const stats = {
          total: items.length,
          pending: items.filter(item => item.status === "scheduled").length,
          done: items.filter(item => item.status === "completed").length,
          dueToday: items.filter(item => item.status === "scheduled" && item.scheduled_at?.startsWith(todayStr)).length
        };

        return {
          data: {
            items,
            total,
            stats
          }
        };
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
      query: payload => ({
        url: "/followups",
        method: "POST",
        data: payload
      }),
      transformResponse: (response: any) => response.data,
      invalidatesTags: [{ type: "Followups", id: "LIST" }]
    }),

    updateFollowUp: builder.mutation<
      FollowUpRecord,
      { followUpId: string; payload: Partial<CreateFollowUpInput> }
    >({
      query: ({ followUpId, payload }) => ({
        url: `/followups/${followUpId}`,
        method: "PATCH",
        data: payload
      }),
      transformResponse: (response: any) => response.data,
      invalidatesTags: (_result, _error, arg) => [
        { type: "Followups", id: arg.followUpId },
        { type: "Followups", id: "LIST" }
      ]
    }),

    deleteFollowUp: builder.mutation<void, string>({
      query: followUpId => ({
        url: `/followups/${followUpId}`,
        method: "DELETE"
      }),
      invalidatesTags: [{ type: "Followups", id: "LIST" }]
    }),

    updateFollowUpStatus: builder.mutation<
      FollowUpRecord,
      { followUpId: string; status: FollowUpStatus; notes?: string }
    >({
      query: ({ followUpId, status, notes }) => ({
        url: `/followups/${followUpId}/status`,
        method: "POST",
        data: { status, notes }
      }),
      transformResponse: (response: any) => response.data,
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
  useUpdateFollowUpMutation,
  useDeleteFollowUpMutation,
  useUpdateFollowUpStatusMutation
} = followupApi;
