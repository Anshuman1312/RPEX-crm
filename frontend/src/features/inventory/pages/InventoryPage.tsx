import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { InventoryCreateForm } from "@/features/inventory/components/InventoryCreateForm";
import { InventoryFiltersBar } from "@/features/inventory/components/InventoryFiltersBar";
import { InventoryStatsCards } from "@/features/inventory/components/InventoryStatsCards";
import { buildInventoryColumns } from "@/features/inventory/components/inventoryColumns";
import { useInventoryFilters } from "@/features/inventory/hooks/useInventoryFilters";
import {
  useCreateInventoryUnitMutation,
  useGetInventoryUnitsQuery,
  useUpdateInventoryStatusMutation
} from "@/features/inventory/services/inventoryApi";
import { InventoryStatus } from "@/features/inventory/types/inventory";
import { CreateInventoryUnitFormValues } from "@/features/inventory/validation/inventorySchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function InventoryPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, category, setCategory, status, setStatus } =
    useInventoryFilters();
  const { data, isLoading, isFetching, isError, refetch } = useGetInventoryUnitsQuery(filters);
  const [createInventoryUnit, { isLoading: isCreatingInventoryUnit }] =
    useCreateInventoryUnitMutation();
  const [updateInventoryStatus] = useUpdateInventoryStatusMutation();

  const columns = useMemo(
    () =>
      buildInventoryColumns(async (unitId: string, nextStatus: InventoryStatus) => {
        try {
          await updateInventoryStatus({ unitId, status: nextStatus }).unwrap();
          toast.success("Inventory status updated");
        } catch {
          toast.error("Unable to update inventory status");
        }
      }),
    [updateInventoryStatus]
  );

  const handleCreateInventoryUnit = async (values: CreateInventoryUnitFormValues) => {
    try {
      await createInventoryUnit(values).unwrap();
      toast.success("Inventory unit created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create inventory unit");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Unit
        </Button>
      }
      description="Inventory and stock workspace with segmentation, availability, and assignment tracking."
      title="Inventory"
    >
      {isLoading ? <LoadingState label="Loading inventory workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load inventory units. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Inventory workspace unavailable"
        />
      ) : null}

      {data ? <InventoryStatsCards stats={data.stats} /> : null}

      <InventoryFiltersBar
        category={category}
        onCategoryChange={setCategory}
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        search={search}
        status={status}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Unit"
        size="lg"
      >
        <InventoryCreateForm
          isSubmitting={isCreatingInventoryUnit}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateInventoryUnit}
        />
      </Dialog>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        title="Inventory Portfolio"
        onRefresh={refetch}
        isRefreshing={isFetching}
      />
    </PageContainer>
  );
}
