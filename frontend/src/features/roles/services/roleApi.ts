import { rootApi } from "@/core/api/rootApi";
import {
  CreateRoleInput,
  RoleFilters,
  RoleListResponse,
  RoleRecord,
  RoleStatus
} from "@/features/roles/types/role";
import {
  buildRoleListResponse,
  createRoleRecord,
  initialRoleRecords
} from "@/features/roles/services/roleMockData";

let inMemoryRoles: RoleRecord[] = [...initialRoleRecords];

function applyFilters(records: RoleRecord[], filters?: RoleFilters): RoleRecord[] {
  if (!filters) return records;
  const search = filters.search?.trim().toLowerCase();
  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.name, record.description].join(" ").toLowerCase().includes(search);
    const scopeMatch =
      !filters.scope || filters.scope === "All" || record.scope === filters.scope;
    const statusMatch =
      !filters.status || filters.status === "All" || record.status === filters.status;
    return searchMatch && scopeMatch && statusMatch;
  });
}

export const roleApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getRoles: builder.query<RoleListResponse, RoleFilters | void>({
      queryFn: async filters => ({
        data: buildRoleListResponse(applyFilters(inMemoryRoles, filters ?? undefined))
      }),
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Roles" as const, id: item.id })),
              { type: "Roles" as const, id: "LIST" }
            ]
          : [{ type: "Roles" as const, id: "LIST" }]
    }),

    createRole: builder.mutation<RoleRecord, CreateRoleInput>({
      queryFn: async payload => {
        const record = createRoleRecord(payload, inMemoryRoles.length + 1);
        inMemoryRoles = [record, ...inMemoryRoles];
        return { data: record };
      },
      invalidatesTags: [{ type: "Roles", id: "LIST" }]
    }),

    updateRoleStatus: builder.mutation<RoleRecord, { roleId: string; status: RoleStatus }>({
      queryFn: async ({ roleId, status }) => {
        const record = inMemoryRoles.find(r => r.id === roleId);
        if (!record)
          return { error: { status: 404, data: { message: "Role not found" } } };
        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_r, _e, arg) => [
        { type: "Roles", id: arg.roleId },
        { type: "Roles", id: "LIST" }
      ]
    })
  })
});

export const { useGetRolesQuery, useCreateRoleMutation, useUpdateRoleStatusMutation } = roleApi;
