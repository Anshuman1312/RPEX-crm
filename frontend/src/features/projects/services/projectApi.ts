import { rootApi } from "@/core/api/rootApi";
import {
  CreateProjectInput,
  ProjectFilters,
  ProjectHealth,
  ProjectListResponse,
  ProjectRecord
} from "@/features/projects/types/project";
import {
  buildProjectListResponse,
  createProjectRecord,
  initialProjectRecords
} from "@/features/projects/services/projectMockData";

let inMemoryProjects: ProjectRecord[] = [...initialProjectRecords];

function applyFilters(records: ProjectRecord[], filters?: ProjectFilters): ProjectRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.name, record.client, record.projectManager]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const phaseMatch = !filters.phase || filters.phase === "All" || record.phase === filters.phase;
    const healthMatch = !filters.health || filters.health === "All" || record.health === filters.health;

    return searchMatch && phaseMatch && healthMatch;
  });
}

export const projectApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getProjects: builder.query<ProjectListResponse, ProjectFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryProjects, filters);
        return { data: buildProjectListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Projects" as const, id: item.id })),
              { type: "Projects" as const, id: "LIST" }
            ]
          : [{ type: "Projects" as const, id: "LIST" }]
    }),

    createProject: builder.mutation<ProjectRecord, CreateProjectInput>({
      queryFn: async payload => {
        const nextRecord = createProjectRecord(payload, inMemoryProjects.length + 1);
        inMemoryProjects = [nextRecord, ...inMemoryProjects];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Projects", id: "LIST" }]
    }),

    updateProjectHealth: builder.mutation<
      ProjectRecord,
      { projectId: string; health: ProjectHealth }
    >({
      queryFn: async ({ projectId, health }) => {
        const record = inMemoryProjects.find(item => item.id === projectId);

        if (!record) {
          return { error: { status: 404, data: { message: "Project not found" } } };
        }

        record.health = health;
        record.lastUpdated = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Projects", id: arg.projectId },
        { type: "Projects", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetProjectsQuery,
  useCreateProjectMutation,
  useUpdateProjectHealthMutation
} = projectApi;
