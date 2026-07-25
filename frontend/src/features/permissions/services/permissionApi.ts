import { rootApi } from "@/core/api/rootApi";
import {
  PermissionFilters,
  PermissionListResponse,
  PermissionRecord,
  PermissionStatus
} from "@/features/permissions/types/permission";
import {
  buildPermissionListResponse,
  initialPermissionRecords
} from "@/features/permissions/services/permissionMockData";

let inMemoryPermissions: PermissionRecord[] = [...initialPermissionRecords];

function applyFilters(
  records: PermissionRecord[],
  filters?: PermissionFilters
): PermissionRecord[] {
  if (!filters) return records;
  const search = filters.search?.trim().toLowerCase();
  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.key, record.module, record.description]
        .join(" ")
        .toLowerCase()
        .includes(search);
    const moduleMatch =
      !filters.module || filters.module === "All" || record.module === filters.module;
    const actionMatch =
      !filters.action || filters.action === "All" || record.action === filters.action;
    const statusMatch =
      !filters.status || filters.status === "All" || record.status === filters.status;
    return searchMatch && moduleMatch && actionMatch && statusMatch;
  });
}

export const permissionApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getPermissions: builder.query<PermissionListResponse, PermissionFilters | void>({
      queryFn: async filters => ({
        data: buildPermissionListResponse(applyFilters(inMemoryPermissions, filters))
      }),
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Permissions" as const, id: item.id })),
              { type: "Permissions" as const, id: "LIST" }
            ]
          : [{ type: "Permissions" as const, id: "LIST" }]
    }),

    updatePermissionStatus: builder.mutation<
      PermissionRecord,
      { permissionId: string; status: PermissionStatus }
    >({
      queryFn: async ({ permissionId, status }) => {
        const record = inMemoryPermissions.find(p => p.id === permissionId);
        if (!record)
          return { error: { status: 404, data: { message: "Permission not found" } } };
        record.status = status;
        return { data: record };
      },
      invalidatesTags: (_r, _e, arg) => [
        { type: "Permissions", id: arg.permissionId },
        { type: "Permissions", id: "LIST" }
      ]
    })
  })
});

export const { useGetPermissionsQuery, useUpdatePermissionStatusMutation } = permissionApi;
