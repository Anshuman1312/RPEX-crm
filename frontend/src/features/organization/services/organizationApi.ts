import { rootApi } from "@/core/api/rootApi";
import {
  CreateOrganizationInput,
  OrganizationFilters,
  OrganizationListResponse,
  OrganizationRecord,
  OrganizationStatus
} from "@/features/organization/types/organization";
import {
  buildOrganizationListResponse,
  createOrganizationRecord,
  initialOrganizationRecords
} from "@/features/organization/services/organizationMockData";

let inMemoryOrganizations: OrganizationRecord[] = [...initialOrganizationRecords];

function applyFilters(
  records: OrganizationRecord[],
  filters?: OrganizationFilters
): OrganizationRecord[] {
  if (!filters) return records;
  const search = filters.search?.trim().toLowerCase();
  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.name, record.primaryContact, record.email, record.city]
        .join(" ")
        .toLowerCase()
        .includes(search);
    const industryMatch =
      !filters.industry || filters.industry === "All" || record.industry === filters.industry;
    const statusMatch =
      !filters.status || filters.status === "All" || record.status === filters.status;
    return searchMatch && industryMatch && statusMatch;
  });
}

export const organizationApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getOrganizations: builder.query<OrganizationListResponse, OrganizationFilters | void>({
      queryFn: async filters => ({
        data: buildOrganizationListResponse(applyFilters(inMemoryOrganizations, filters))
      }),
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Organizations" as const, id: item.id })),
              { type: "Organizations" as const, id: "LIST" }
            ]
          : [{ type: "Organizations" as const, id: "LIST" }]
    }),

    createOrganization: builder.mutation<OrganizationRecord, CreateOrganizationInput>({
      queryFn: async payload => {
        const record = createOrganizationRecord(payload, inMemoryOrganizations.length + 1);
        inMemoryOrganizations = [record, ...inMemoryOrganizations];
        return { data: record };
      },
      invalidatesTags: [{ type: "Organizations", id: "LIST" }]
    }),

    updateOrganizationStatus: builder.mutation<
      OrganizationRecord,
      { organizationId: string; status: OrganizationStatus }
    >({
      queryFn: async ({ organizationId, status }) => {
        const record = inMemoryOrganizations.find(o => o.id === organizationId);
        if (!record)
          return { error: { status: 404, data: { message: "Organization not found" } } };
        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_r, _e, arg) => [
        { type: "Organizations", id: arg.organizationId },
        { type: "Organizations", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetOrganizationsQuery,
  useCreateOrganizationMutation,
  useUpdateOrganizationStatusMutation
} = organizationApi;
