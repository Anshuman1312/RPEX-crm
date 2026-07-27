import { rootApi } from "@/core/api/rootApi";
import {
  CreateTaskInput,
  TaskFilters,
  TaskListResponse,
  TaskRecord,
  TaskStatus
} from "@/features/tasks/types/task";
import {
  buildTaskListResponse,
  createTaskRecord,
  initialTaskRecords
} from "@/features/tasks/services/taskMockData";

let inMemoryTasks: TaskRecord[] = [...initialTaskRecords];

function applyFilters(records: TaskRecord[], filters?: TaskFilters): TaskRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.title, record.module, record.assignee]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const priorityMatch =
      !filters.priority || filters.priority === "All" || record.priority === filters.priority;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && priorityMatch && statusMatch;
  });
}

export const taskApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getTasks: builder.query<TaskListResponse, TaskFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryTasks, filters);
        return { data: buildTaskListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Tasks" as const, id: item.id })),
              { type: "Tasks" as const, id: "LIST" }
            ]
          : [{ type: "Tasks" as const, id: "LIST" }]
    }),

    createTask: builder.mutation<TaskRecord, CreateTaskInput>({
      queryFn: async payload => {
        const nextRecord = createTaskRecord(payload, inMemoryTasks.length + 1);
        inMemoryTasks = [nextRecord, ...inMemoryTasks];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Tasks", id: "LIST" }]
    }),

    updateTaskStatus: builder.mutation<TaskRecord, { taskId: string; status: TaskStatus }>({
      queryFn: async ({ taskId, status }) => {
        const record = inMemoryTasks.find(item => item.id === taskId);

        if (!record) {
          return { error: { status: 404, data: { message: "Task not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Tasks", id: arg.taskId },
        { type: "Tasks", id: "LIST" }
      ]
    })
  })
});

export const { useGetTasksQuery, useCreateTaskMutation, useUpdateTaskStatusMutation } = taskApi;
