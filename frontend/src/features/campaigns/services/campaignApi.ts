import { rootApi } from "@/core/api/rootApi";
import {
  CampaignFilters,
  CampaignListResponse,
  CampaignRecord,
  CampaignStatus,
  CreateCampaignInput
} from "@/features/campaigns/types/campaign";
import {
  buildCampaignListResponse,
  createCampaignRecord,
  initialCampaignRecords
} from "@/features/campaigns/services/campaignMockData";

let inMemoryCampaigns: CampaignRecord[] = [...initialCampaignRecords];

function applyFilters(records: CampaignRecord[], filters?: CampaignFilters): CampaignRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.name, record.owner, record.channel, record.status]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const channelMatch =
      !filters.channel || filters.channel === "All" || record.channel === filters.channel;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && channelMatch && statusMatch;
  });
}

export const campaignApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getCampaigns: builder.query<CampaignListResponse, CampaignFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryCampaigns, filters);
        return { data: buildCampaignListResponse(filtered) };
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
      queryFn: async payload => {
        const nextRecord = createCampaignRecord(payload, inMemoryCampaigns.length + 1);
        inMemoryCampaigns = [nextRecord, ...inMemoryCampaigns];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Campaigns", id: "LIST" }]
    }),

    updateCampaignStatus: builder.mutation<
      CampaignRecord,
      { campaignId: string; status: CampaignStatus }
    >({
      queryFn: async ({ campaignId, status }) => {
        const record = inMemoryCampaigns.find(item => item.id === campaignId);

        if (!record) {
          return { error: { status: 404, data: { message: "Campaign not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Campaigns", id: arg.campaignId },
        { type: "Campaigns", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetCampaignsQuery,
  useCreateCampaignMutation,
  useUpdateCampaignStatusMutation
} = campaignApi;
