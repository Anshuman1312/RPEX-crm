import {
  CreateEmployeeInput,
  EmployeeListResponse,
  EmployeeRecord,
  EmployeeStats
} from "@/features/employees/types/employee";

function formatDate(offsetDays: number) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

export const initialEmployeeRecords: EmployeeRecord[] = [
  {
    id: "EM-12101",
    fullName: "Riya Sharma",
    email: "riya.sharma@rpexcrm.com",
    department: "Sales",
    band: "Lead",
    manager: "Arjun Mehta",
    status: "Active",
    joiningDate: formatDate(-560),
    updatedAt: formatDate(-1)
  },
  {
    id: "EM-12102",
    fullName: "Aman Verma",
    email: "aman.verma@rpexcrm.com",
    department: "Operations",
    band: "Senior",
    manager: "Kavita Rao",
    status: "On Leave",
    joiningDate: formatDate(-420),
    updatedAt: formatDate(-2)
  },
  {
    id: "EM-12103",
    fullName: "Priya Iyer",
    email: "priya.iyer@rpexcrm.com",
    department: "Finance",
    band: "Manager",
    manager: "Vikas Nair",
    status: "Active",
    joiningDate: formatDate(-910),
    updatedAt: formatDate(-1)
  },
  {
    id: "EM-12104",
    fullName: "Rohan Gupta",
    email: "rohan.gupta@rpexcrm.com",
    department: "Marketing",
    band: "Associate",
    manager: "Neha Kapoor",
    status: "Inactive",
    joiningDate: formatDate(-300),
    updatedAt: formatDate(-8)
  }
];

export function buildEmployeeStats(records: EmployeeRecord[]): EmployeeStats {
  return {
    total: records.length,
    active: records.filter(record => record.status === "Active").length,
    onLeave: records.filter(record => record.status === "On Leave").length,
    inactive: records.filter(record => record.status === "Inactive").length
  };
}

export function buildEmployeeListResponse(records: EmployeeRecord[]): EmployeeListResponse {
  return {
    items: records,
    total: records.length,
    stats: buildEmployeeStats(records)
  };
}

export function createEmployeeRecord(payload: CreateEmployeeInput, index: number): EmployeeRecord {
  return {
    id: `EM-${12100 + index}`,
    fullName: payload.fullName,
    email: payload.email,
    department: payload.department,
    band: payload.band,
    manager: payload.manager,
    status: "Active",
    joiningDate: payload.joiningDate,
    updatedAt: new Date().toISOString().slice(0, 10)
  };
}
