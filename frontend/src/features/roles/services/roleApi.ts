import { rootApi } from "@/core/api/rootApi";
import {
  CreateRoleInput,
  RoleFilters,
  RoleListResponse,
  RoleRecord,
  RoleStatus,
  RoleScope,
  RoleStats
} from "@/features/roles/types/role";

export const roleApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getRoles: builder.query<RoleListResponse, RoleFilters | void>({
      query: () => ({
        url: "/users/roles",
        method: "GET"
      }),
      transformResponse: (response: any): RoleListResponse => {
        const items: RoleRecord[] = (response.data || []).map((r: any) => {
          let scope: RoleScope = "Organization";
          if (r.code === "SUPER_ADMIN" || r.code === "ADMIN") {
            scope = "System";
          }
          return {
            id: r.id,
            name: r.name,
            description: r.description || "",
            scope,
            status: (r.status || "Active") as RoleStatus,
            assignedUsers: r.assignedUsers || 0,
            permissions: r.permissions || [],
            createdAt: r.createdAt || new Date().toISOString().slice(0, 10),
            updatedAt: r.updatedAt || new Date().toISOString().slice(0, 10)
          };
        });

        const stats: RoleStats = {
          total: items.length,
          active: items.filter(item => item.status === "Active").length,
          system: items.filter(item => item.scope === "System").length,
          inactive: items.filter(item => item.status === "Inactive").length
        };

        return {
          items,
          total: items.length,
          stats
        };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Roles" as const, id: item.id })),
              { type: "Roles" as const, id: "LIST" }
            ]
          : [{ type: "Roles" as const, id: "LIST" }]
    }),

    createRole: builder.mutation<RoleRecord, CreateRoleInput>({
      query: payload => ({
        url: "/users/roles",
        method: "POST",
        body: payload
      }),
      invalidatesTags: [{ type: "Roles", id: "LIST" }]
    }),

    updateRoleStatus: builder.mutation<RoleRecord, { roleId: string; status: RoleStatus }>({
      query: ({ roleId, status }) => ({
        url: `/users/roles/${roleId}/status`,
        method: "PATCH",
        body: { status }
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Roles", id: arg.roleId },
        { type: "Roles", id: "LIST" }
      ]
    })
  })
});

export const { useGetRolesQuery, useCreateRoleMutation, useUpdateRoleStatusMutation } = roleApi;
