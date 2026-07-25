import { rootApi } from "@/core/api/rootApi";
import {
  ActivityFilters,
  ActivityListResponse
} from "@/features/activity-timeline/types/activity";
import {
  buildActivityListResponse,
  initialActivityRecords
} from "@/features/activity-timeline/services/activityMockData";

export const activityApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getActivities: builder.query<ActivityListResponse, ActivityFilters | void>({
      queryFn: async filters => {
        const search = filters?.search?.trim().toLowerCase();
        const items = initialActivityRecords.filter(record => {
          const searchMatch =
            !search ||
            [record.id, record.actor, record.module, record.action, record.subject, record.detail]
              .join(" ")
              .toLowerCase()
              .includes(search);
          const moduleMatch =
            !filters?.module || filters.module === "All" || record.module === filters.module;
          const actionMatch =
            !filters?.action || filters.action === "All" || record.action === filters.action;
          return searchMatch && moduleMatch && actionMatch;
        });
        return { data: buildActivityListResponse(items) };
      },
      providesTags: [{ type: "Activity" as const, id: "LIST" }]
    })
  })
});

export const { useGetActivitiesQuery } = activityApi;
