import { rootApi } from "@/core/api/rootApi";
import {
  CreateEmployeeInput,
  EmployeeFilters,
  EmployeeListResponse,
  EmployeeRecord,
  EmployeeStatus
} from "@/features/employees/types/employee";

interface BackendRole {
  id: string;
  name: string;
  code: string;
}

interface BackendDepartment {
  id: string;
  name: string;
  code: string;
}

interface BackendDesignation {
  id: string;
  name: string;
  code: string;
}

interface BackendUser {
  id: string;
  full_name: string;
  email: string;
  status: string;
  employee_code: string;
  role?: BackendRole;
  department?: BackendDepartment;
  designation?: BackendDesignation;
  created_at: string;
  updated_at: string;
}

interface BackendUserListResponse {
  data: BackendUser[];
  total: number;
}

interface BackendLookupItem {
  id: string;
  name: string;
  code: string;
}

interface LookupResponse {
  data: BackendLookupItem[];
}

export const employeeApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getEmployees: builder.query<EmployeeListResponse, EmployeeFilters | void>({
      query: filters => {
        const params: Record<string, string | number> = {
          page: 1,
          page_size: 100
        };
        if (filters) {
          if (filters.search) params.search = filters.search;
          if (filters.status && filters.status !== "All") {
            params.status = filters.status === "Active" ? "active" : "inactive";
          }
        }
        return {
          url: "/users",
          method: "GET",
          params
        };
      },
      transformResponse: (response: BackendUserListResponse): EmployeeListResponse => {
        const users = response.data || [];
        const items: EmployeeRecord[] = users.map((user: BackendUser): EmployeeRecord => ({
          id: user.id,
          fullName: user.full_name,
          email: user.email,
          department: "N/A",
          band: "N/A",
          manager: "N/A",
          status: (user.status === "active" ? "Active" : "Inactive") as EmployeeStatus,
          joiningDate: user.created_at ? new Date(user.created_at).toISOString().slice(0, 10) : "",
          updatedAt: user.updated_at ? new Date(user.updated_at).toISOString().slice(0, 10) : "",
          roleName: user.role?.name || "No Role",
          roleId: user.role?.id || "",
          departmentId: "",
          designationId: ""
        }));

        const total = response.total || items.length;
        const active = items.filter((item: EmployeeRecord) => item.status === "Active").length;
        const inactive = items.filter((item: EmployeeRecord) => item.status === "Inactive").length;

        return {
          items,
          total,
          stats: {
            total,
            active,
            onLeave: 0,
            inactive
          }
        };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Employees" as const, id: item.id })),
              { type: "Employees" as const, id: "LIST" }
            ]
          : [{ type: "Employees" as const, id: "LIST" }]
    }),

    createEmployee: builder.mutation<unknown, CreateEmployeeInput>({
      query: payload => ({
        url: "/users",
        method: "POST",
        body: {
          full_name: payload.fullName,
          email: payload.email,
          password: payload.password,
          phone: payload.phone,
          role_id: payload.roleId || null,
          employee_code: payload.employeeCode || null
        }
      }),
      invalidatesTags: [{ type: "Employees", id: "LIST" }]
    }),

    updateEmployee: builder.mutation<
      unknown,
      { employeeId: string; payload: { status?: string; roleId?: string } }
    >({
      query: ({ employeeId, payload }) => ({
        url: `/users/${employeeId}`,
        method: "PATCH",
        body: {
          status: payload.status,
          role_id: payload.roleId
        }
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Employees", id: arg.employeeId },
        { type: "Employees", id: "LIST" }
      ]
    }),

    updateEmployeeStatus: builder.mutation<
      unknown,
      { employeeId: string; status: EmployeeStatus }
    >({
      query: ({ employeeId, status }) => ({
        url: `/users/${employeeId}`,
        method: "PATCH",
        body: {
          status: status === "Active" ? "active" : "inactive"
        }
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Employees", id: arg.employeeId },
        { type: "Employees", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetEmployeesQuery,
  useCreateEmployeeMutation,
  useUpdateEmployeeMutation,
  useUpdateEmployeeStatusMutation
} = employeeApi;
