import { rootApi } from "@/core/api/rootApi";
import {
  CreateCustomerInput,
  CustomerFilters,
  CustomerListResponse,
  CustomerRecord
} from "@/features/customers/types/customer";
import {
  buildCustomerListResponse,
  createCustomerRecord,
  initialCustomerRecords
} from "@/features/customers/services/customerMockData";

let inMemoryCustomers: CustomerRecord[] = [...initialCustomerRecords];

function applyFilters(
  records: CustomerRecord[],
  filters?: CustomerFilters | void
): CustomerRecord[] {
  if (!filters) {
    return records;
  }

  const f = filters as CustomerFilters;
  const search = f.search?.trim().toLowerCase();

  return records.filter((record) => {
    const searchMatch =
      !search ||
      [
        record.id,
        record.name,
        record.email,
        record.phone,
        record.alternatePhone || "",
        record.occupation || "",
        record.address || "",
        record.remarks || ""
      ]
        .join(" ")
        .toLowerCase()
        .includes(search);

    const purposeMatch = !f.purpose || f.purpose === "All" || record.purpose === f.purpose;
    const propertyTypeMatch =
      !f.propertyType || f.propertyType === "All" || record.propertyType === f.propertyType;

    return searchMatch && purposeMatch && propertyTypeMatch;
  });
}

export const customerApi = rootApi.injectEndpoints({
  endpoints: (builder) => ({
    getCustomers: builder.query<CustomerListResponse, CustomerFilters | void>({
      queryFn: async (filters) => {
        const filtered = applyFilters(inMemoryCustomers, filters);
        return { data: buildCustomerListResponse(filtered) };
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
      queryFn: async (payload) => {
        const nextRecord = createCustomerRecord(payload, inMemoryCustomers.length + 1);
        inMemoryCustomers = [nextRecord, ...inMemoryCustomers];
        return { data: nextRecord };
      },
      invalidatesTags: [{ type: "Customers", id: "LIST" }]
    })
  })
});

export const { useGetCustomersQuery, useCreateCustomerMutation } = customerApi;
