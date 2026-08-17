import { useMemo, useState } from "react";
import { useSelector } from "react-redux";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { RootState } from "@/app/store";
import { buildEmployeeColumns } from "@/features/employees/components/employeeColumns";
import { EmployeeCreateForm } from "@/features/employees/components/EmployeeCreateForm";
import { EmployeeFiltersBar } from "@/features/employees/components/EmployeeFiltersBar";
import { EmployeeStatsCards } from "@/features/employees/components/EmployeeStatsCards";
import { useEmployeeFilters } from "@/features/employees/hooks/useEmployeeFilters";
import { useGetRolesQuery } from "@/features/roles/services/roleApi";
import {
  useCreateEmployeeMutation,
  useGetEmployeesQuery,
  useUpdateEmployeeMutation
} from "@/features/employees/services/employeeApi";
import { PageContainer } from "@/layouts/components/PageContainer";

export function EmployeesPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const session = useSelector((state: RootState) => state.auth.session);
  const isSuperAdmin = session?.role === "SUPER_ADMIN";

  const { filters, search, setSearch, department, setDepartment, status, setStatus } =
    useEmployeeFilters();
  const { data, isLoading, isError, refetch } = useGetEmployeesQuery(filters);
  const { data: rolesData } = useGetRolesQuery();
  const rolesList = rolesData?.items || [];

  const [createEmployee, { isLoading: isCreatingEmployee }] = useCreateEmployeeMutation();
  const [updateEmployee] = useUpdateEmployeeMutation();

  const columns = useMemo(
    () =>
      buildEmployeeColumns(
        async (employeeId: string, nextStatus: string) => {
          try {
            await updateEmployee({
              employeeId,
              payload: { status: nextStatus === "Active" ? "active" : "inactive" }
            }).unwrap();
            toast.success("Employee status updated");
          } catch {
            toast.error("Unable to update employee status");
          }
        },
        async (employeeId: string, nextRoleId: string) => {
          try {
            await updateEmployee({
              employeeId,
              payload: { roleId: nextRoleId }
            }).unwrap();
            toast.success("Employee role updated");
          } catch {
            toast.error("Unable to update employee role");
          }
        },
        !!isSuperAdmin,
        rolesList
      ),
    [updateEmployee, isSuperAdmin, rolesList]
  );

  const handleCreateEmployee = async (values: any) => {
    try {
      await createEmployee(values).unwrap();
      toast.success("Employee created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create employee");
    }
  };

  return (
    <PageContainer
      actions={
        isSuperAdmin ? (
          <Button onClick={() => setShowCreateForm(true)}>
            Create Employee
          </Button>
        ) : null
      }
      description="Employee operations workspace with directory filters, lifecycle status, and onboarding intake."
      title="Employees"
    >
      {isLoading ? <LoadingState label="Loading employee workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load employees. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Employee workspace unavailable"
        />
      ) : null}

      {data ? <EmployeeStatsCards stats={data.stats} /> : null}

      <EmployeeFiltersBar
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        search={search}
        status={status}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Employee"
        size="lg"
      >
        <EmployeeCreateForm
          isSubmitting={isCreatingEmployee}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateEmployee}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Employee Directory" />
    </PageContainer>
  );
}
