import { rootApi } from "@/core/api/rootApi";
import {
  CreateNotificationInput,
  NotificationFilters,
  NotificationListResponse,
  NotificationRecord,
  NotificationStatus
} from "@/features/notifications/types/notification";
import {
  buildNotificationListResponse,
  createNotificationRecord,
  initialNotificationRecords
} from "@/features/notifications/services/notificationMockData";

let inMemoryNotifications: NotificationRecord[] = [...initialNotificationRecords];

function applyFilters(
  records: NotificationRecord[],
  filters?: NotificationFilters
): NotificationRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.title, record.message, record.owner, record.sourceModule]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const typeMatch = !filters.type || filters.type === "All" || record.type === filters.type;
    const statusMatch = !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && typeMatch && statusMatch;
  });
}

export const notificationApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getNotifications: builder.query<NotificationListResponse, NotificationFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryNotifications, filters);
        return { data: buildNotificationListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Notifications" as const, id: item.id })),
              { type: "Notifications" as const, id: "LIST" }
            ]
          : [{ type: "Notifications" as const, id: "LIST" }]
    }),

    createNotification: builder.mutation<NotificationRecord, CreateNotificationInput>({
      queryFn: async payload => {
        const nextRecord = createNotificationRecord(payload, inMemoryNotifications.length + 1);
        inMemoryNotifications = [nextRecord, ...inMemoryNotifications];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Notifications", id: "LIST" }]
    }),

    updateNotificationStatus: builder.mutation<
      NotificationRecord,
      { notificationId: string; status: NotificationStatus }
    >({
      queryFn: async ({ notificationId, status }) => {
        const record = inMemoryNotifications.find(item => item.id === notificationId);

        if (!record) {
          return { error: { status: 404, data: { message: "Notification not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 16);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Notifications", id: arg.notificationId },
        { type: "Notifications", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetNotificationsQuery,
  useCreateNotificationMutation,
  useUpdateNotificationStatusMutation
} = notificationApi;
