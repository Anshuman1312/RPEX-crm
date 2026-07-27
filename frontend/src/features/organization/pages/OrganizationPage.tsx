import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { buildOrganizationColumns } from "@/features/organization/components/organizationColumns";
import { OrganizationCreateForm } from "@/features/organization/components/OrganizationCreateForm";
import { OrganizationFiltersBar } from "@/features/organization/components/OrganizationFiltersBar";
import { OrganizationStatsCards } from "@/features/organization/components/OrganizationStatsCards";
import { useOrganizationFilters } from "@/features/organization/hooks/useOrganizationFilters";
import {
  useCreateOrganizationMutation,
  useGetOrganizationsQuery,
  useUpdateOrganizationStatusMutation
} from "@/features/organization/services/organizationApi";
import { OrganizationStatus } from "@/features/organization/types/organization";
import { CreateOrganizationFormValues } from "@/features/organization/validation/organizationSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function OrganizationPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, industry, setIndustry, status, setStatus } =
    useOrganizationFilters();
  const { data, isLoading, isError, refetch } = useGetOrganizationsQuery(filters);
  const [createOrganization, { isLoading: isCreating }] = useCreateOrganizationMutation();
  const [updateOrganizationStatus] = useUpdateOrganizationStatusMutation();

  const columns = useMemo(
    () =>
      buildOrganizationColumns(async (organizationId, nextStatus: OrganizationStatus) => {
        try {
          await updateOrganizationStatus({ organizationId, status: nextStatus }).unwrap();
          toast.success("Organization status updated");
        } catch {
          toast.error("Unable to update organization status");
        }
      }),
    [updateOrganizationStatus]
  );

  const handleCreate = async (values: CreateOrganizationFormValues) => {
    try {
      await createOrganization(values).unwrap();
      toast.success("Organization created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create organization");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Organization
        </Button>
      }
      description="Organization registry with industry segmentation, status lifecycle, and contact management."
      title="Organization"
    >
      {isLoading ? <LoadingState label="Loading organization workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load organizations. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Organization workspace unavailable"
        />
      ) : null}

      {data ? <OrganizationStatsCards stats={data.stats} /> : null}

      <OrganizationFiltersBar
        industry={industry}
        onIndustryChange={setIndustry}
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        search={search}
        status={status}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Organization"
        size="lg"
      >
        <OrganizationCreateForm
          isSubmitting={isCreating}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreate}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Organization Registry" />
    </PageContainer>
  );
}
