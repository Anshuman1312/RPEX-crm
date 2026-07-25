import { rootApi } from "@/core/api/rootApi";
import {
  CreateReportInput,
  ReportFilters,
  ReportListResponse,
  ReportRecord,
  ReportStatus
} from "@/features/reports/types/report";
import {
  buildReportListResponse,
  createReportRecord,
  initialReportRecords
} from "@/features/reports/services/reportMockData";

let inMemoryReports: ReportRecord[] = [...initialReportRecords];

function applyFilters(records: ReportRecord[], filters?: ReportFilters): ReportRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.title, record.type, record.owner]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const typeMatch = !filters.type || filters.type === "All" || record.type === filters.type;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && typeMatch && statusMatch;
  });
}

export const reportApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getReports: builder.query<ReportListResponse, ReportFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryReports, filters);
        return { data: buildReportListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Reports" as const, id: item.id })),
              { type: "Reports" as const, id: "LIST" }
            ]
          : [{ type: "Reports" as const, id: "LIST" }]
    }),

    createReport: builder.mutation<ReportRecord, CreateReportInput>({
      queryFn: async payload => {
        const nextRecord = createReportRecord(payload, inMemoryReports.length + 1);
        inMemoryReports = [nextRecord, ...inMemoryReports];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Reports", id: "LIST" }]
    }),

    updateReportStatus: builder.mutation<
      ReportRecord,
      { reportId: string; status: ReportStatus }
    >({
      queryFn: async ({ reportId, status }) => {
        const record = inMemoryReports.find(item => item.id === reportId);

        if (!record) {
          return { error: { status: 404, data: { message: "Report not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 16);
        if (status === "Ready" || status === "Exported") {
          record.rows = Math.max(record.rows, 1);
        }

        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Reports", id: arg.reportId },
        { type: "Reports", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetReportsQuery,
  useCreateReportMutation,
  useUpdateReportStatusMutation
} = reportApi;
