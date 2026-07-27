import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button, DataTable, Dialog, ErrorState, LoadingState } from "@/components";
import { TaskCreateForm } from "@/features/tasks/components/TaskCreateForm";
import { TaskFiltersBar } from "@/features/tasks/components/TaskFiltersBar";
import { TaskStatsCards } from "@/features/tasks/components/TaskStatsCards";
import { buildTaskColumns } from "@/features/tasks/components/taskColumns";
import { useTaskFilters } from "@/features/tasks/hooks/useTaskFilters";
import {
  useCreateTaskMutation,
  useGetTasksQuery,
  useUpdateTaskStatusMutation
} from "@/features/tasks/services/taskApi";
import { TaskStatus } from "@/features/tasks/types/task";
import { CreateTaskFormValues } from "@/features/tasks/validation/taskSchemas";
import { PageContainer } from "@/layouts/components/PageContainer";

export function TasksPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { filters, search, setSearch, priority, setPriority, status, setStatus } = useTaskFilters();
  const { data, isLoading, isError, refetch } = useGetTasksQuery(filters);
  const [createTask, { isLoading: isCreatingTask }] = useCreateTaskMutation();
  const [updateTaskStatus] = useUpdateTaskStatusMutation();

  const columns = useMemo(
    () =>
      buildTaskColumns(async (taskId: string, nextStatus: TaskStatus) => {
        try {
          await updateTaskStatus({ taskId, status: nextStatus }).unwrap();
          toast.success("Task status updated");
        } catch {
          toast.error("Unable to update task status");
        }
      }),
    [updateTaskStatus]
  );

  const handleCreateTask = async (values: CreateTaskFormValues) => {
    try {
      await createTask(values).unwrap();
      toast.success("Task created successfully");
      setShowCreateForm(false);
    } catch {
      toast.error("Unable to create task");
    }
  };

  return (
    <PageContainer
      actions={
        <Button onClick={() => setShowCreateForm(true)}>
          Create Task
        </Button>
      }
      description="Task execution workspace with priorities, blockers, assignees, and status flow."
      title="Tasks"
    >
      {isLoading ? <LoadingState label="Loading tasks workspace..." /> : null}
      {isError ? (
        <ErrorState
          description="Could not load tasks. Retry to refresh the workspace."
          onRetry={() => refetch()}
          title="Tasks workspace unavailable"
        />
      ) : null}

      {data ? <TaskStatsCards stats={data.stats} /> : null}

      <TaskFiltersBar
        onPriorityChange={setPriority}
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        priority={priority}
        search={search}
        status={status}
      />

      <Dialog
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create Task"
        size="lg"
      >
        <TaskCreateForm
          isSubmitting={isCreatingTask}
          onCancel={() => setShowCreateForm(false)}
          onSubmit={handleCreateTask}
        />
      </Dialog>

      <DataTable columns={columns} data={data?.items ?? []} title="Task Board" />
    </PageContainer>
  );
}
