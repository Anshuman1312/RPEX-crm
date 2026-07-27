import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { buildRoleColumns } from "@/features/roles/components/roleColumns";
import { RoleCreateForm } from "@/features/roles/components/RoleCreateForm";
import { RoleFiltersBar } from "@/features/roles/components/RoleFiltersBar";
import { RoleStatsCards } from "@/features/roles/components/RoleStatsCards";
import { useRoleFilters } from "@/features/roles/hooks/useRoleFilters";
import {
  useCreateRoleMutation,
  useGetRolesQuery,
  useUpdateRoleStatusMutation
} from "@/features/roles/services/roleApi";
import { RoleStatus } from "@/features/roles/types/role";
import { CreateRoleFormValues } from "@/features/roles/validation/roleSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function RolesPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, scope, setScope, status, setStatus } = useRoleFilters();
  const { data, isLoading, isError, refetch } = useGetRolesQuery(filters);
  const [createRole, { isLoading: isCreating }] = useCreateRoleMutation();
  const [updateRoleStatus] = useUpdateRoleStatusMutation();

  const columns = useMemo(
    () =>
      buildRoleColumns(async (roleId, nextStatus: RoleStatus) => {
        try {
          await updateRoleStatus({ roleId, status: nextStatus }).unwrap();
          toast.success("Role status updated");
        } catch {
          toast.error("Unable to update role status");
        }
      }),
    [updateRoleStatus]
  );

  const handleCreate = async (values: CreateRoleFormValues) => {
    try {
      await createRole(values).unwrap();
      toast.success("Role created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create role");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Role
        </Button>
      }
      description="Role management workspace for access control, scope definition, and user assignment."
      title="Roles"
    >
      {isLoading ? <LoadingState label="Loading roles workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load roles. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Roles workspace unavailable"
        />
      ) : null}

      {data ? <RoleStatsCards stats={data.stats} /> : null}

      <RoleFiltersBar
        onSearchChange={setSearch}
        onScopeChange={setScope}
        onStatusChange={setStatus}
        scope={scope}
        search={search}
        status={status}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Role"
        size="lg"
      >
        <RoleCreateForm
          isSubmitting={isCreating}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreate}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Role Registry" />
    </PageContainer>
  );
}
