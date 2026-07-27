import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { buildEmployeeColumns } from "@/features/employees/components/employeeColumns";
import { EmployeeCreateForm } from "@/features/employees/components/EmployeeCreateForm";
import { EmployeeFiltersBar } from "@/features/employees/components/EmployeeFiltersBar";
import { EmployeeStatsCards } from "@/features/employees/components/EmployeeStatsCards";
import { useEmployeeFilters } from "@/features/employees/hooks/useEmployeeFilters";
import {
  useCreateEmployeeMutation,
  useGetEmployeesQuery,
  useUpdateEmployeeStatusMutation
} from "@/features/employees/services/employeeApi";
import { EmployeeStatus } from "@/features/employees/types/employee";
import { CreateEmployeeFormValues } from "@/features/employees/validation/employeeSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function EmployeesPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, department, setDepartment, status, setStatus } =
    useEmployeeFilters();
  const { data, isLoading, isError, refetch } = useGetEmployeesQuery(filters);
  const [createEmployee, { isLoading: isCreatingEmployee }] = useCreateEmployeeMutation();
  const [updateEmployeeStatus] = useUpdateEmployeeStatusMutation();

  const columns = useMemo(
    () =>
      buildEmployeeColumns(async (employeeId: string, nextStatus: EmployeeStatus) => {
        try {
          await updateEmployeeStatus({ employeeId, status: nextStatus }).unwrap();
          toast.success("Employee status updated");
        } catch {
          toast.error("Unable to update employee status");
        }
      }),
    [updateEmployeeStatus]
  );

  const handleCreateEmployee = async (values: CreateEmployeeFormValues) => {
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
        <Button onClick={() => setShowCreateForm(true)}>
          Create Employee
        </Button>
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
        department={department}
        onDepartmentChange={setDepartment}
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
