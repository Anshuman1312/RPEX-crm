import { rootApi } from "@/core/api/rootApi";
import {
  CreateCustomerInput,
  CustomerFilters,
  CustomerListResponse,
  CustomerRecord,
  UpdateCustomerInput
} from "@/features/customers/types/customer";

export const customerApi = rootApi.injectEndpoints({
  endpoints: (builder) => ({
    getCustomers: builder.query<CustomerListResponse, CustomerFilters | void>({
      queryFn: async (filters, api, extraOptions, baseQuery) => {
        const params: Record<string, string | number> = {};
        if (filters) {
          if (filters.search) params.search = filters.search;
          if (filters.statuses) params.statuses = filters.statuses;
          if (filters.customer_types) params.customer_types = filters.customer_types;
        }

        // Fetch list of customers
        const listResult = await baseQuery({
          url: "/customers",
          method: "GET",
          params
        });

        if (listResult.error) {
          return { error: listResult.error as any };
        }

        const listEnvelope = listResult.data as any;
        const items = listEnvelope?.data || [];
        const total = listEnvelope?.pagination?.total ?? items.length;

        // Fetch overview stats
        const statsResult = await baseQuery({
          url: "/customers/stats/overview",
          method: "GET"
        });

        const statsEnvelope = statsResult.data as any;
        const stats = statsEnvelope?.data || { by_status: {}, by_type: {}, total: 0 };

        return {
          data: {
            items,
            total,
            stats
          }
        };
      },
      providesTags: (result) =>
        result
          ? [
              ...result.items.map((item) => ({ type: "Customers" as const, id: item.id })),
              { type: "Customers" as const, id: "LIST" }
            ]
          : [{ type: "Customers" as const, id: "LIST" }]
    }),

    createCustomer: builder.mutation<CustomerRecord, CreateCustomerInput>({
      query: (payload) => ({
        url: "/customers",
        method: "POST",
        data: payload
      }),
      transformResponse: (response: any) => response.data,
      invalidatesTags: [{ type: "Customers", id: "LIST" }]
    }),

    updateCustomer: builder.mutation<CustomerRecord, UpdateCustomerInput>({
      query: ({ id, payload }) => ({
        url: `/customers/${id}`,
        method: "PATCH",
        data: payload
      }),
      transformResponse: (response: any) => response.data,
      invalidatesTags: (result, error, { id }) => [
        { type: "Customers", id },
        { type: "Customers", id: "LIST" }
      ]
    }),

    deleteCustomer: builder.mutation<void, string>({
      query: (id) => ({
        url: `/customers/${id}`,
        method: "DELETE"
      }),
      invalidatesTags: [{ type: "Customers", id: "LIST" }]
    })
  })
});

export const {
  useGetCustomersQuery,
  useCreateCustomerMutation,
  useUpdateCustomerMutation,
  useDeleteCustomerMutation
} = customerApi;
