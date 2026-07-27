import { CustomerPropertyType, CustomerPurpose } from "@/features/customers/types/customer";

export const customerPurposeOptions: Array<CustomerPurpose | "All"> = [
  "All",
  "Investment",
  "Self Use",
  "Business"
];

export const customerPropertyTypeOptions: Array<CustomerPropertyType | "All"> = [
  "All",
  "Plot",
  "Villa",
  "Flat",
  "Commercial"
];
