import { rootApi } from "@/core/api/rootApi";
import {
  CreateLeadInput,
  LeadFilters,
  LeadListResponse,
  LeadRecord,
  LeadStage
} from "@/features/leads/types/lead";
import {
  buildLeadListResponse,
  createLeadRecord,
  initialLeadRecords
} from "@/features/leads/services/leadMockData";

let inMemoryLeads: LeadRecord[] = [...initialLeadRecords];

function applyFilters(records: LeadRecord[], filters?: LeadFilters): LeadRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.name, record.email, record.phone, record.owner]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const stageMatch = !filters.stage || filters.stage === "All" || record.stage === filters.stage;
    const sourceMatch =
      !filters.source || filters.source === "All" || record.source === filters.source;

    return searchMatch && stageMatch && sourceMatch;
  });
}

export const leadApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getLeads: builder.query<LeadListResponse, LeadFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryLeads, filters);
        return { data: buildLeadListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Leads" as const, id: item.id })),
              { type: "Leads" as const, id: "LIST" }
            ]
          : [{ type: "Leads" as const, id: "LIST" }]
    }),

    createLead: builder.mutation<LeadRecord, CreateLeadInput>({
      queryFn: async payload => {
        const nextRecord = createLeadRecord(payload, inMemoryLeads.length + 1);
        inMemoryLeads = [nextRecord, ...inMemoryLeads];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Leads", id: "LIST" }]
    }),

    updateLeadStage: builder.mutation<LeadRecord, { leadId: string; stage: LeadStage }>({
      queryFn: async ({ leadId, stage }) => {
        const record = inMemoryLeads.find(item => item.id === leadId);

        if (!record) {
          return { error: { status: 404, data: { message: "Lead not found" } } };
        }

        record.stage = stage;
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Leads", id: arg.leadId },
        { type: "Leads", id: "LIST" }
      ]
    })
  })
});

export const { useGetLeadsQuery, useCreateLeadMutation, useUpdateLeadStageMutation } = leadApi;
