import {
  CreateCustomerInput,
  CustomerListResponse,
  CustomerRecord,
  CustomerStats
} from "@/features/customers/types/customer";

export const initialCustomerRecords: CustomerRecord[] = [
  {
    id: "CU-2001",
    title: "Mrs",
    name: "Ishita Rao",
    email: "ishita.rao@example.com",
    phone: "+91 99223 40011",
    alternatePhone: "+91 99223 40022",
    occupation: "Consultant",
    address: "Flat 202, Block A, Green Ridge",
    budgetRange: "80L - 1.2Cr",
    timeDuration: "Immediate",
    purpose: "Self Use",
    propertyType: "Flat",
    remarks: "Prefers 3BHK flats."
  },
  {
    id: "CU-2002",
    title: "Miss",
    name: "Kavya Sharma",
    email: "kavya.sharma@example.com",
    phone: "+91 98110 22344",
    alternatePhone: "",
    occupation: "Business Owner",
    address: "Villa 10, Royal Meadows",
    budgetRange: "3Cr - 4.5Cr",
    timeDuration: "6 Months",
    purpose: "Investment",
    propertyType: "Villa",
    remarks: "Looking for premium luxury villa options."
  },
  {
    id: "CU-2003",
    title: "Mr.",
    name: "Aarav Mehta",
    email: "aarav.mehta@example.com",
    phone: "+91 98220 11234",
    alternatePhone: "+91 98220 55678",
    occupation: "IT Manager",
    address: "Plot 45, Sector 4, HSR Layout",
    budgetRange: "1.5Cr - 2Cr",
    timeDuration: "1 Month",
    purpose: "Business",
    propertyType: "Plot",
    remarks: "Needs corner plot for commercial utility."
  },
  {
    id: "CU-2004",
    title: "Mr.",
    name: "Neel Jain",
    email: "neel.jain@example.com",
    phone: "+91 99555 12987",
    alternatePhone: "",
    occupation: "Doctor",
    address: "Flat 405, Sector 12, Dwarka",
    budgetRange: "1.2Cr - 1.5Cr",
    timeDuration: "Immediate",
    purpose: "Self Use",
    propertyType: "Commercial",
    remarks: "Wants ground floor space for dental clinic setup."
  }
];

export function buildCustomerStats(records: CustomerRecord[]): CustomerStats {
  return {
    total: records.length,
    investment: records.filter(record => record.purpose === "Investment").length,
    selfUse: records.filter(record => record.purpose === "Self Use").length,
    business: records.filter(record => record.purpose === "Business").length
  };
}

export function buildCustomerListResponse(records: CustomerRecord[]): CustomerListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildCustomerStats(records)
  };
}

export function createCustomerRecord(payload: CreateCustomerInput, index: number): CustomerRecord {
  return {
    id: `CU-${2000 + index}`,
    title: payload.title,
    name: payload.name,
    email: payload.email,
    phone: payload.phone,
    alternatePhone: payload.alternatePhone,
    occupation: payload.occupation,
    address: payload.address,
    budgetRange: payload.budgetRange,
    timeDuration: payload.timeDuration,
    purpose: payload.purpose,
    propertyType: payload.propertyType,
    remarks: payload.remarks
  };
}
