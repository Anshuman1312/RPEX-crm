import { ActivityFiltersBar } from "@/features/activity-timeline/components/ActivityFiltersBar";
import { ActivityStatsCards } from "@/features/activity-timeline/components/ActivityStatsCards";
import { activityColumns } from "@/features/activity-timeline/components/activityColumns";
import { useActivityFilters } from "@/features/activity-timeline/hooks/useActivityFilters";
import { useGetActivitiesQuery } from "@/features/activity-timeline/services/activityApi";
import { DataTable, ErrorState, LoadingState } from "@/components";
import { PageContainer } from "@/layouts/components/PageContainer";

export function ActivityTimelinePage() {
  const { filters, search, setSearch, module, setModule, action, setAction } = useActivityFilters();
  const { data, isLoading, isError, refetch } = useGetActivitiesQuery(filters);

  return (
    <PageContainer
      description="Immutable audit log of all CRM events across modules, actors, and actions."
      title="Activity Timeline"
    >
      {isLoading ? <LoadingState label="Loading activity timeline..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load activity events. Retry to refresh the timeline."
          onRetry={() => refetch()}
          title="Activity timeline unavailable"
        />
      ) : null}

      {data ? <ActivityStatsCards stats={data.stats} /> : null}

      <ActivityFiltersBar
        action={action}
        module={module}
        onActionChange={setAction}
        onModuleChange={setModule}
        onSearchChange={setSearch}
        search={search}
      />

      <DataTable columns={activityColumns} data={data?.items ?? []} title="Event Log" />
    </PageContainer>
  );
}
