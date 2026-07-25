import { rootApi } from "@/core/api/rootApi";
import {
  CreateInventoryUnitInput,
  InventoryFilters,
  InventoryListResponse,
  InventoryStatus,
  InventoryUnitRecord
} from "@/features/inventory/types/inventory";
import {
  buildInventoryListResponse,
  createInventoryUnitRecord,
  initialInventoryUnitRecords
} from "@/features/inventory/services/inventoryMockData";

let inMemoryInventoryUnits: InventoryUnitRecord[] = [...initialInventoryUnitRecords];

function applyFilters(records: InventoryUnitRecord[], filters?: InventoryFilters): InventoryUnitRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.unitCode, record.project, record.assignedAgent]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const categoryMatch =
      !filters.category || filters.category === "All" || record.category === filters.category;
    const statusMatch =
      !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && categoryMatch && statusMatch;
  });
}

export const inventoryApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getInventoryUnits: builder.query<InventoryListResponse, InventoryFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryInventoryUnits, filters);
        return { data: buildInventoryListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Inventory" as const, id: item.id })),
              { type: "Inventory" as const, id: "LIST" }
            ]
          : [{ type: "Inventory" as const, id: "LIST" }]
    }),

    createInventoryUnit: builder.mutation<InventoryUnitRecord, CreateInventoryUnitInput>({
      queryFn: async payload => {
        const nextRecord = createInventoryUnitRecord(payload, inMemoryInventoryUnits.length + 1);
        inMemoryInventoryUnits = [nextRecord, ...inMemoryInventoryUnits];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Inventory", id: "LIST" }]
    }),

    updateInventoryStatus: builder.mutation<
      InventoryUnitRecord,
      { unitId: string; status: InventoryStatus }
    >({
      queryFn: async ({ unitId, status }) => {
        const record = inMemoryInventoryUnits.find(item => item.id === unitId);

        if (!record) {
          return { error: { status: 404, data: { message: "Inventory unit not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Inventory", id: arg.unitId },
        { type: "Inventory", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetInventoryUnitsQuery,
  useCreateInventoryUnitMutation,
  useUpdateInventoryStatusMutation
} = inventoryApi;
