import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { ProjectCreateForm } from "@/features/projects/components/ProjectCreateForm";
import { ProjectFiltersBar } from "@/features/projects/components/ProjectFiltersBar";
import { ProjectStatsCards } from "@/features/projects/components/ProjectStatsCards";
import { buildProjectColumns } from "@/features/projects/components/projectColumns";
import { useProjectFilters } from "@/features/projects/hooks/useProjectFilters";
import {
  useCreateProjectMutation,
  useGetProjectsQuery,
  useUpdateProjectHealthMutation
} from "@/features/projects/services/projectApi";
import { ProjectHealth } from "@/features/projects/types/project";
import { CreateProjectFormValues } from "@/features/projects/validation/projectSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function ProjectsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, phase, setPhase, health, setHealth } = useProjectFilters();
  const { data, isLoading, isFetching, isError, refetch } = useGetProjectsQuery(filters);
  const [createProject, { isLoading: isCreatingProject }] = useCreateProjectMutation();
  const [updateProjectHealth] = useUpdateProjectHealthMutation();

  const columns = useMemo(
    () =>
      buildProjectColumns(async (projectId: string, nextHealth: ProjectHealth) => {
        try {
          await updateProjectHealth({ projectId, health: nextHealth }).unwrap();
          toast.success("Project health updated");
        } catch {
          toast.error("Unable to update project health");
        }
      }),
    [updateProjectHealth]
  );

  const handleCreateProject = async (values: CreateProjectFormValues) => {
    try {
      await createProject(values).unwrap();
      toast.success("Project created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create project");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Project
        </Button>
      }
      description="Project delivery workspace with health tracking, phase filters, and handover visibility."
      title="Projects"
    >
      {isLoading ? <LoadingState label="Loading project portfolio..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load projects. Retry to refresh the portfolio."
          onRetry={() => refetch()}
          title="Project portfolio unavailable"
        />
      ) : null}

      {data ? <ProjectStatsCards stats={data.stats} /> : null}

      <ProjectFiltersBar
        health={health}
        onHealthChange={setHealth}
        onPhaseChange={setPhase}
        onSearchChange={setSearch}
        phase={phase}
        search={search}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Project"
        size="lg"
      >
        <ProjectCreateForm
          isSubmitting={isCreatingProject}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateProject}
        />
      </Dialog>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        title="Project Portfolio"
        onRefresh={refetch}
        isRefreshing={isFetching}
      />
    </PageContainer>
  );
}
