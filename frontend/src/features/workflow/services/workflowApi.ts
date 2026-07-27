import { rootApi } from "@/core/api/rootApi";
import {
  CreateWorkflowInput,
  WorkflowFilters,
  WorkflowListResponse,
  WorkflowRecord,
  WorkflowStatus
} from "@/features/workflow/types/workflow";
import {
  buildWorkflowListResponse,
  createWorkflowRecord,
  initialWorkflowRecords
} from "@/features/workflow/services/workflowMockData";

let inMemoryWorkflows: WorkflowRecord[] = [...initialWorkflowRecords];

function applyFilters(records: WorkflowRecord[], filters?: WorkflowFilters): WorkflowRecord[] {
  if (!filters) return records;
  const search = filters.search?.trim().toLowerCase();
  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.name, record.trigger, record.action, record.module]
        .join(" ")
        .toLowerCase()
        .includes(search);
    const triggerMatch =
      !filters.trigger || filters.trigger === "All" || record.trigger === filters.trigger;
    const statusMatch =
      !filters.status || filters.status === "All" || record.status === filters.status;
    return searchMatch && triggerMatch && statusMatch;
  });
}

export const workflowApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getWorkflows: builder.query<WorkflowListResponse, WorkflowFilters | void>({
      queryFn: async filters => ({
        data: buildWorkflowListResponse(applyFilters(inMemoryWorkflows, filters))
      }),
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Workflow" as const, id: item.id })),
              { type: "Workflow" as const, id: "LIST" }
            ]
          : [{ type: "Workflow" as const, id: "LIST" }]
    }),

    createWorkflow: builder.mutation<WorkflowRecord, CreateWorkflowInput>({
      queryFn: async payload => {
        const record = createWorkflowRecord(payload, inMemoryWorkflows.length + 1);
        inMemoryWorkflows = [record, ...inMemoryWorkflows];
        return { data: record };
      },
      invalidatesTags: [{ type: "Workflow", id: "LIST" }]
    }),

    updateWorkflowStatus: builder.mutation<
      WorkflowRecord,
      { workflowId: string; status: WorkflowStatus }
    >({
      queryFn: async ({ workflowId, status }) => {
        const record = inMemoryWorkflows.find(w => w.id === workflowId);
        if (!record)
          return { error: { status: 404, data: { message: "Workflow not found" } } };
        record.status = status;
        return { data: record };
      },
      invalidatesTags: (_r, _e, arg) => [
        { type: "Workflow", id: arg.workflowId },
        { type: "Workflow", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetWorkflowsQuery,
  useCreateWorkflowMutation,
  useUpdateWorkflowStatusMutation
} = workflowApi;
