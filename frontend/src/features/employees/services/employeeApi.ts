import { rootApi } from "@/core/api/rootApi";
import {
  CreateEmployeeInput,
  EmployeeFilters,
  EmployeeListResponse,
  EmployeeRecord,
  EmployeeStatus
} from "@/features/employees/types/employee";
import {
  buildEmployeeListResponse,
  createEmployeeRecord,
  initialEmployeeRecords
} from "@/features/employees/services/employeeMockData";

let inMemoryEmployees: EmployeeRecord[] = [...initialEmployeeRecords];

function applyFilters(records: EmployeeRecord[], filters?: EmployeeFilters): EmployeeRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.fullName, record.email, record.manager, record.department]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const departmentMatch =
      !filters.department ||
      filters.department === "All" ||
      record.department === filters.department;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && departmentMatch && statusMatch;
  });
}

export const employeeApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getEmployees: builder.query<EmployeeListResponse, EmployeeFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryEmployees, filters);
        return { data: buildEmployeeListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Employees" as const, id: item.id })),
              { type: "Employees" as const, id: "LIST" }
            ]
          : [{ type: "Employees" as const, id: "LIST" }]
    }),

    createEmployee: builder.mutation<EmployeeRecord, CreateEmployeeInput>({
      queryFn: async payload => {
        const nextRecord = createEmployeeRecord(payload, inMemoryEmployees.length + 1);
        inMemoryEmployees = [nextRecord, ...inMemoryEmployees];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Employees", id: "LIST" }]
    }),

    updateEmployeeStatus: builder.mutation<
      EmployeeRecord,
      { employeeId: string; status: EmployeeStatus }
    >({
      queryFn: async ({ employeeId, status }) => {
        const record = inMemoryEmployees.find(item => item.id === employeeId);

        if (!record) {
          return { error: { status: 404, data: { message: "Employee not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
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
  useUpdateEmployeeStatusMutation
} = employeeApi;
