import { rootApi } from "@/core/api/rootApi";
import {
  CampaignFilters,
  CampaignListResponse,
  CampaignRecord,
  CampaignStatus,
  CreateCampaignInput
} from "@/features/campaigns/types/campaign";

function applyFilters(records: CampaignRecord[], filters?: CampaignFilters): CampaignRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.name, record.type, record.platform, record.status]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const typeMatch =
      !filters.type || filters.type === "All" || record.type === filters.type;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && typeMatch && statusMatch;
  });
}

function buildCampaignStats(records: CampaignRecord[]) {
  return {
    total: records.length,
    running: records.filter(record => record.status === "Running").length,
    completed: records.filter(record => record.status === "Completed").length,
    leadsGenerated: records.reduce((sum, record) => sum + record.leadsGenerated, 0)
  };
}

export const campaignApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getCampaigns: builder.query<CampaignListResponse, CampaignFilters | void>({
      queryFn: async (filters, api, extraOptions, baseQuery) => {
        const listResult = await baseQuery({
          url: "/campaigns",
          method: "GET",
        });

        if (listResult.error) {
          return { error: listResult.error as any };
        }

        const rawItems = (listResult.data as any[]) || [];
        const todayStr = new Date().toISOString().slice(0, 10);

        const items: CampaignRecord[] = rawItems.map(item => {
          let status: CampaignStatus = "Draft";
          const startDateStr = item.start_date ? String(item.start_date) : "";
          const endDateStr = item.end_date ? String(item.end_date) : "";

          if (endDateStr && endDateStr < todayStr) {
            status = "Completed";
          } else if (startDateStr && startDateStr <= todayStr) {
            status = "Running";
          }

          return {
            id: item.id,
            name: item.name || "",
            type: item.type || "",
            platform: item.platform || "",
            budget: Number(item.budget) || 0,
            start_date: startDateStr,
            end_date: endDateStr,
            extra_data: {
              reach: item.reach,
              cpl: item.cpl,
              roas: item.roas,
              conversion: item.conversion,
            },
            status,
            leadsGenerated: Number(item.leads) || 0,
            updatedAt: startDateStr || todayStr,
          };
        });

        const filtered = applyFilters(items, filters || undefined);

        return {
          data: {
            items: filtered,
            total: filtered.length,
            stats: buildCampaignStats(filtered)
          }
        };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Campaigns" as const, id: item.id })),
              { type: "Campaigns" as const, id: "LIST" }
            ]
          : [{ type: "Campaigns" as const, id: "LIST" }]
    }),

    createCampaign: builder.mutation<CampaignRecord, CreateCampaignInput>({
      query: payload => ({
        url: "/campaigns",
        method: "POST",
        data: payload
      }),
      transformResponse: (response: any) => {
        const item = response;
        const todayStr = new Date().toISOString().slice(0, 10);
        return {
          id: item.id,
          name: item.name,
          type: item.type || "",
          platform: item.platform,
          budget: Number(item.budget) || 0,
          start_date: item.start_date || "",
          end_date: item.end_date || "",
          extra_data: item.extra_data || {},
          status: "Draft",
          leadsGenerated: 0,
          updatedAt: todayStr
        };
      },
      invalidatesTags: [{ type: "Campaigns", id: "LIST" }]
    })
  })
});

export const {
  useGetCampaignsQuery,
  useCreateCampaignMutation
} = campaignApi;
