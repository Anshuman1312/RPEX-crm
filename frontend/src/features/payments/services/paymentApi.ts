import { rootApi } from "@/core/api/rootApi";
import {
  CreatePaymentInput,
  PaymentFilters,
  PaymentListResponse,
  PaymentRecord,
  PaymentStatus
} from "@/features/payments/types/payment";
import {
  buildPaymentListResponse,
  createPaymentRecord,
  initialPaymentRecords
} from "@/features/payments/services/paymentMockData";

let inMemoryPayments: PaymentRecord[] = [...initialPaymentRecords];

function applyFilters(records: PaymentRecord[], filters?: PaymentFilters): PaymentRecord[] {
  if (!filters) {
    return records;
  }

  const search = filters.search?.trim().toLowerCase();

  return records.filter(record => {
    const searchMatch =
      !search ||
      [record.id, record.bookingId, record.customerName, record.projectName, record.owner]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const methodMatch =
      !filters.method || filters.method === "All" || record.method === filters.method;
    const statusMatch =
      !filters.status || filters.status === "All" || record.status === filters.status;

    return searchMatch && methodMatch && statusMatch;
  });
}

export const paymentApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    getPayments: builder.query<PaymentListResponse, PaymentFilters | void>({
      queryFn: async filters => {
        const filtered = applyFilters(inMemoryPayments, filters);
        return { data: buildPaymentListResponse(filtered) };
      },
      providesTags: result =>
        result
          ? [
              ...result.items.map(item => ({ type: "Payments" as const, id: item.id })),
              { type: "Payments" as const, id: "LIST" }
            ]
          : [{ type: "Payments" as const, id: "LIST" }]
    }),

    createPayment: builder.mutation<PaymentRecord, CreatePaymentInput>({
      queryFn: async payload => {
        const nextRecord = createPaymentRecord(payload, inMemoryPayments.length + 1);
        inMemoryPayments = [nextRecord, ...inMemoryPayments];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Payments", id: "LIST" }]
    }),

    updatePaymentStatus: builder.mutation<
      PaymentRecord,
      { paymentId: string; status: PaymentStatus }
    >({
      queryFn: async ({ paymentId, status }) => {
        const record = inMemoryPayments.find(item => item.id === paymentId);

        if (!record) {
          return { error: { status: 404, data: { message: "Payment not found" } } };
        }

        record.status = status;
        record.updatedAt = new Date().toISOString().slice(0, 10);
        return { data: record };
      },
      invalidatesTags: (_result, _error, arg) => [
        { type: "Payments", id: arg.paymentId },
        { type: "Payments", id: "LIST" }
      ]
    })
  })
});

export const {
  useGetPaymentsQuery,
  useCreatePaymentMutation,
  useUpdatePaymentStatusMutation
} = paymentApi;
