import { useMemo } from "react";
import { toast } from "sonner";
import { DataTable, ErrorState, LoadingState } from "@/components";
import { buildPermissionColumns } from "@/features/permissions/components/permissionColumns";
import { PermissionFiltersBar } from "@/features/permissions/components/PermissionFiltersBar";
import { PermissionStatsCards } from "@/features/permissions/components/PermissionStatsCards";
import { usePermissionFilters } from "@/features/permissions/hooks/usePermissionFilters";
import {
  useGetPermissionsQuery,
  useUpdatePermissionStatusMutation
} from "@/features/permissions/services/permissionApi";
import { PermissionStatus } from "@/features/permissions/types/permission";
import { PageContainer } from "@/layouts/components/PageContainer";

export function PermissionsPage() {
  const {
    filters, search, setSearch, module, setModule, action, setAction, status, setStatus
  } = usePermissionFilters();
  const { data, isLoading, isError, refetch } = useGetPermissionsQuery(filters);
  const [updatePermissionStatus] = useUpdatePermissionStatusMutation();

  const columns = useMemo(
    () =>
      buildPermissionColumns(async (permissionId, nextStatus: PermissionStatus) => {
        try {
          await updatePermissionStatus({ permissionId, status: nextStatus }).unwrap();
          toast.success("Permission status updated");
        } catch {
          toast.error("Unable to update permission status");
        }
      }),
    [updatePermissionStatus]
  );

  return (
    <PageContainer
      description="Permission registry across all modules with action-level visibility and status controls."
      title="Permissions"
    >
      {isLoading ? <LoadingState label="Loading permissions workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load permissions. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Permissions workspace unavailable"
        />
      ) : null}

      {data ? <PermissionStatsCards stats={data.stats} /> : null}

      <PermissionFiltersBar
        action={action}
        module={module}
        onActionChange={setAction}
        onModuleChange={setModule}
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        search={search}
        status={status}
      />

      <DataTable columns={columns} data={data?.items ?? []} title="Permission Registry" />
    </PageContainer>
  );
}
